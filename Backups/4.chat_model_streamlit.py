import streamlit as st
import anthropic
from typing import List, Dict, Tuple
import os
import re
import pandas as pd
# 🔴 NEW IMPORTS FOR CHAT HISTORY FUNCTIONALITY
import json
from datetime import datetime
import uuid
from pathlib import Path

from streamlit import chat_input
import sys
from pathlib import Path

# prompts_dir = Path(__file__).parent.parent / "prompts"
# sys.path.append(str(prompts_dir))

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from prompts.prompt_loader import (

    get_system_prompt,
    get_ui_text,
    get_response_message,
    get_input_validation_message,
    get_filter_message,
    get_allowed_topics,
    get_forbidden_topics,
    get_code_patterns,
    get_action_options,
    get_language_options,
    get_prompts_config,
    load_chat_filter_prompts
)

# Page configuration
st.set_page_config(
    page_title="QA Agent",
    page_icon="🔒",
    layout="wide"
)

try:
    prompts_config = get_prompts_config()
    ALLOWED_TOPICS = get_allowed_topics()
    FORBIDDEN_TOPICS = get_forbidden_topics()
    SYSTEM_PROMPT = get_system_prompt()
    CODE_PATTERNS = get_code_patterns()
    ACTION_OPTIONS = get_action_options()
except Exception as e:
    st.error(f"Failed to load YAML prompts configuration: {e}")
    st.stop()

# 🔴 NEW: Configuration for chat history storage
CHAT_HISTORY_DIR = "chat_histories"
Path(CHAT_HISTORY_DIR).mkdir(exist_ok=True)


# 🔴 NEW: Chat History Management Functions
def save_chat_history(session_id: str, messages: List[Dict], session_name: str = None):
    """Save chat history to JSON file"""
    try:
        chat_data = {
            "session_id": session_id,
            "session_name": session_name or f"Chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "created_at": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat(),
            "messages": messages
        }
        
        file_path = Path(CHAT_HISTORY_DIR) / f"{session_id}.json"
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(chat_data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        st.error(f"Error saving chat history: {e}")
        return False

def load_chat_history(session_id: str) -> Dict:
    """Load chat history from JSON file"""
    try:
        file_path = Path(CHAT_HISTORY_DIR) / f"{session_id}.json"
        if file_path.exists():
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return None
    except Exception as e:
        st.error(f"Error loading chat history: {e}")
        return None

def get_all_chat_sessions() -> List[Dict]:
    """Get list of all saved chat sessions"""
    sessions = []
    try:
        for file_path in Path(CHAT_HISTORY_DIR).glob("*.json"):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    sessions.append({
                        "session_id": data.get("session_id"),
                        "session_name": data.get("session_name"),
                        "created_at": data.get("created_at"),
                        "last_updated": data.get("last_updated"),
                        "message_count": len(data.get("messages", []))
                    })
            except:
                continue
        return sorted(sessions, key=lambda x: x["last_updated"], reverse=True)
    except Exception as e:
        st.error(f"Error getting chat sessions: {e}")
        return []

def delete_chat_session(session_id: str):
    """Delete a chat session"""
    try:
        file_path = Path(CHAT_HISTORY_DIR) / f"{session_id}.json"
        if file_path.exists():
            file_path.unlink()
            return True
        return False
    except Exception as e:
        st.error(f"Error deleting chat session: {e}")
        return False

def auto_save_messages():
    """Auto-save current messages"""
    if st.session_state.messages and st.session_state.get("current_session_id"):
        save_chat_history(
            st.session_state.current_session_id,
            st.session_state.messages,
            st.session_state.get("current_session_name")
        )

@st.cache_resource
def get_anthropic_client():
    """Initialize and cache the Anthropic client"""
    api_key = st.secrets.get("ANTHROPIC_API_KEY") or os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        st.error("Please set your ANTHROPIC_API_KEY in Streamlit secrets or environment variables")
        st.stop()
    return anthropic.Anthropic(api_key=api_key)

def check_topic_allowed(text: str) -> Tuple[bool, str]:
    """
    Check if the user's input contains allowed topics
    Returns: (is_allowed, reason)
    """
    text_lower = text.lower()
    
    # Check for forbidden topics first
    for forbidden in FORBIDDEN_TOPICS:
        if forbidden.lower() in text_lower:
            return False, get_filter_message('forbidden_topic', topic=forbidden)
    
    # Check for allowed topics
    found_topics = []
    for category, keywords in ALLOWED_TOPICS.items():
        for keyword in keywords:
            if keyword.lower() in text_lower:
                found_topics.append(category)
                break
    
    if found_topics:
        return True, get_filter_message('allowed_topics_found', topics=', '.join(found_topics))
    
    # If no specific topics found, apply more flexible rules
    # Check for programming-related patterns


    for pattern in CODE_PATTERNS:
        if re.search(pattern, text_lower):
            return True, get_filter_message('code_content_detected')
    
    # If nothing matches, it's likely not allowed
    return False, get_filter_message('no_topics_detected')

def filter_user_input(user_input: str) -> Tuple[bool, str]:
    """
    Pre-filter user input before sending to Claude
    Returns: (should_process, message)
    """
    # Basic checks
    if len(user_input.strip()) < 3:
        return False, get_input_validation_message('insufficient_detail')
    
    # Check topic allowance
    is_allowed, reason = check_topic_allowed(user_input)
    
    if not is_allowed:
        return False, get_input_validation_message('topic_restriction', reason=reason)
    
    return True, get_input_validation_message('input_approved')

def parse_structured_text_to_dataframe(response: str) -> pd.DataFrame:
    """
    Parse structured text response (like tables or lists) into DataFrame
    """
    lines = response.strip().split('\n')
    data = []

    # Try to detect if it's a table format
    if '|' in response:
        # Parse markdown table
        table_lines = [line for line in lines if '|' in line and not line.strip().startswith('|--')]
        if table_lines:
            headers = [col.strip() for col in table_lines[0].split('|')[1:-1]]
            for line in table_lines[1:]:
                row = [col.strip() for col in line.split('|')[1:-1]]
                if len(row) == len(headers):
                    data.append(row)
            return pd.DataFrame(data, columns=headers)

    # Try to parse key-value pairs
    kv_pattern = r'(\w+):\s*(.+)'
    matches = re.findall(kv_pattern, response)
    if matches:
        return pd.DataFrame(matches, columns=['Key', 'Value'])

    # Fall back to line-by-line parsing
    return pd.DataFrame({'Text': lines})

def call_claude_with_restrictions(client: anthropic.Anthropic, user_message: str, model: str = "claude-3-7-sonnet-20250219", max_tokens: int = 1000):
    """Call Claude API with system prompt restrictions"""
    try:
        # Construct messages with system prompt
        messages = [
            {"role": "user", "content": f"{SYSTEM_PROMPT}\n\nUser question: {user_message}"}
        ]
        
        response = client.messages.create(
            model=model,
            max_tokens=max_tokens,
            messages=messages
        )
        
        response_text = response.content[0].text
        
        # Post-process response to ensure compliance
        if any(forbidden.lower() in response_text.lower() for forbidden in FORBIDDEN_TOPICS):
            return get_response_message('forbidden_topic_response')
        
        return response_text
        
    except anthropic.APIError as e:
        st.error(f"API Error: {e}")
        return None
    except Exception as e:
        st.error(f"Unexpected error: {e}")
        return None

# 🔴 NEW: Initialize session state with improved chat history management
if "messages" not in st.session_state:
    st.session_state.messages = []

if "current_session_id" not in st.session_state:
    st.session_state.current_session_id = str(uuid.uuid4())

if "current_session_name" not in st.session_state:
    st.session_state.current_session_name = f"Chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

if "anthropic_client" not in st.session_state:
    st.session_state.anthropic_client = get_anthropic_client()

# 🔴 NEW: Auto-save functionality
if "auto_save" not in st.session_state:
    st.session_state.auto_save = True

# Sidebar configuration
with st.sidebar:
    st.title("🔒 QA AI Assistant_4")
    
    # 🔴 NEW: Chat History Management Section
    st.markdown("### 💾 Chat History")
    
    # Auto-save toggle
    auto_save = st.checkbox("Auto-save conversations", value=st.session_state.auto_save)
    st.session_state.auto_save = auto_save
    
    # Current session info
    session_name = st.text_input(
        "Session Name", 
        value=st.session_state.current_session_name,
        help="Give your conversation a memorable name"
    )
    st.session_state.current_session_name = session_name
    
    # Save current session button
    if st.button("💾 Save Current Session"):
        if save_chat_history(
            st.session_state.current_session_id,
            st.session_state.messages,
            st.session_state.current_session_name
        ):
            st.success("Session saved successfully!")
        else:
            st.error("Failed to save session")
    
    # Load previous sessions
    st.markdown("#### 📂 Previous Sessions")
    sessions = get_all_chat_sessions()
    
    if sessions:
        selected_session = st.selectbox(
            "Load Previous Session",
            options=[None] + [s["session_id"] for s in sessions],
            format_func=lambda x: "-- Select Session --" if x is None else next(
                (s["session_name"] for s in sessions if s["session_id"] == x), "Unknown Session"
            )
        )
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📂 Load Session") and selected_session:
                loaded_data = load_chat_history(selected_session)
                if loaded_data:
                    st.session_state.messages = loaded_data["messages"]
                    st.session_state.current_session_id = loaded_data["session_id"]
                    st.session_state.current_session_name = loaded_data["session_name"]
                    st.success("Session loaded!")
                    st.rerun()
        
        with col2:
            if st.button("🗑️ Delete Session") and selected_session:
                if delete_chat_session(selected_session):
                    st.success("Session deleted!")
                    st.rerun()
        
        # Show session details
        if selected_session:
            session_info = next((s for s in sessions if s["session_id"] == selected_session), None)
            if session_info:
                st.caption(f"Created: {session_info['created_at'][:16]}")
                st.caption(f"Messages: {session_info['message_count']}")
    else:
        st.info("No saved sessions found")
    
    st.markdown("---")
    
    st.markdown("### Allowed Topics:")
    st.success("✅ Programming & Software Development")
    st.success("✅ Data Science & Analytics") 
    
    st.markdown("### Forbidden Topics:")
    st.error("❌ Medical or Legal Advice")
    st.error("❌ Personal Information")
    st.error("❌ Politics or Controversial Topics")
    st.error("❌ Harmful Content")
    
    st.markdown("---")
    
    # Model selection
    model = st.selectbox(
        "Select Model",
        ["claude-sonnet-4-20250514", "claude-3-7-sonnet-20250219"],
        index=0
    )
    
    # Max tokens slider
    max_tokens = st.slider(
        "Max Tokens",
        min_value=100,
        max_value=2000,
        value=1000,
        step=100
    )
    
    # Show filtering info
    show_filtering = st.checkbox("Show Filtering Details", value=False)
    
    # 🔴 MODIFIED: Enhanced clear conversation functionality
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🆕 New Chat"):
            # Save current session if auto-save is enabled
            if st.session_state.auto_save and st.session_state.messages:
                save_chat_history(
                    st.session_state.current_session_id,
                    st.session_state.messages,
                    st.session_state.current_session_name
                )
            
            # Start new session
            st.session_state.messages = []
            st.session_state.current_session_id = str(uuid.uuid4())
            st.session_state.current_session_name = f"Chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            st.rerun()
    
    with col2:
        if st.button("🗑️ Clear Chat"):
            st.session_state.messages = []
            st.rerun()

# Main interface
st.title("🔒 AI Test Assistant")
st.markdown("**This AI assistant only answers questions about Programming, Data Science, and Business topics.**")

# 🔴 NEW: Show current session info
st.caption(f"Current Session: {st.session_state.current_session_name} | Messages: {len(st.session_state.messages)}")

# Display current restrictions
with st.expander("📋 What can I help you with?"):
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**🔧 Programming**")
        st.markdown("- Code debugging\n- Algorithm design\n- Software architecture\n- Best practices")
    
    with col2:
        st.markdown("**📊 Data Science**")
        st.markdown("- Data analysis\n- Machine learning\n- Statistics\n- Visualization")

main_option = st.radio(
    "Choose an action to continue:",
    (
        "Test Case generation",
        "Generate Unit Test in Java",
        "Generate Selenium Code",
        "Generate Playwright Code",
        "Generate TestComplete Code",
        "Generate API Code",
        "Convert Existing Code"
        ""
    )
)
if main_option == "Test Case generation":
    user_input= st.text_area("Enter details about the action to be performed...",placeholder='Enter details about the functionality for which you want to create test case....',label_visibility="visible")
    url_input = st.text_input('Application url', placeholder='Enter your AUT url')
else:
    add_new = st.checkbox('Add New Repo')
    desired_repo_location = st.text_input('Repo location', placeholder='Enter desired repo location in your local Desktop/Downloads folders where you want to save the generated code')
    if main_option == "Generate Selenium Code":
        sub_option_2 = st.selectbox("Select language:", get_language_options('selenium_languages'))
        # add_new = st.checkbox('Add New Repo')
        url_input = st.text_input('Application url', placeholder='Enter your AUT url')
        keyword_input =  st.text_input ('Enter Details', placeholder='Enter specific area(if any)/keyword to generate Test Code')

    if main_option == "Generate Unit Test in Java":
        # add_new = st.checkbox('Add New Repo')
        url_input = st.text_input('Application url', placeholder='Enter the AUT url')
        keyword_input =  st.text_input ('Enter repo location', placeholder='Enter git or local repo location')

    if main_option == "Generate TestComplete Code":
        sub_option_3 = st.selectbox("Select language:", get_language_options('testcomplete_languages'))
        url_input = st.text_input('Application url', placeholder='Enter the AUT url')
        keyword_input = st.text_input('Enter Details', placeholder='Enter specific area(if any)/keyword to generate Test Code')

    if main_option == "Generate API Test Code":
        sub_option_4 = st.selectbox("Select language:", get_language_options('api_test_languages'))
        endpoint_input = st.text_input('Endpoints', placeholder= 'Enter endpoints to generate test Code')
        keyword_input = st.text_input('Enter Details',
                                      placeholder='Enter specific area(if any)/keyword to generate Test Code')

    if main_option == "Convert Existing Code":
        sub_option_5 = st.selectbox("Select language:", [
            "Java Selenium to Playwright Javascript",
            "Python Selenium to Playwright Javascript",
            "JavaScript Playwright to Cypress JavaScript",
        ])
        repo_location = st.text_input("Repo Location", placeholder='Enter the existing repo in your local or git:')

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if show_filtering and "filter_info" in message:
            st.caption(f"Filter info: {message['filter_info']}")









def submit_prompt():
    prompt =''
    if main_option == "Test Case generation" and user_input:
       prompt= 'prompt for Test Case generation'

    elif main_option == "Generate Selenium Code" and sub_option_2:
        prompt = 'prompt for Test Case generation'

    elif main_option == "Generate TestComplete Code":
        prompt = 'prompt for Test Case generation'

    elif main_option == "Generate API Test Code":
        prompt = 'prompt for Test Case generation'

    elif main_option == "Convert Existing Code":
        prompt = 'prompt for Test Case generation'
        repo_location = st.text_input("Enter the repo in your local:")

    if prompt :

        # st.chat_input("Enter details about the action to be performed..4.Chat_model.")

        # Pre-filter the input
            should_process, filter_message = filter_user_input(prompt)

            # Add user message to chat history
            user_message = {"role": "user", "content": prompt}
            if show_filtering:
                user_message["filter_info"] = filter_message

            st.session_state.messages.append(user_message)

            # 🔴 NEW: Auto-save after adding user message
            if st.session_state.auto_save:
                auto_save_messages()

            # Display user message
            with st.chat_message("user"):
                st.markdown(prompt)
                if show_filtering:
                    st.caption(f"Filter info: {filter_message}")

            # Process or reject based on filtering
            with st.chat_message("assistant"):
                if not should_process:
                    # Show rejection message
                    rejection_response = f"🚫 {filter_message}\n\nPlease ask me about:\n- Programming and software development\n- Data science and analytics"
                    st.markdown(rejection_response)

                    assistant_message = {"role": "assistant", "content": rejection_response}
                    if show_filtering:
                        assistant_message["filter_info"] = "Request rejected by pre-filter"
                    st.session_state.messages.append(assistant_message)

                    # 🔴 NEW: Auto-save after adding assistant message
                    if st.session_state.auto_save:
                        auto_save_messages()
                else:
                    # Process with Claude
                    with st.spinner("Processing your question..."):
                        response = call_claude_with_restrictions(
                            st.session_state.anthropic_client,
                            prompt,
                            model=model,
                            max_tokens=max_tokens
                        )

                        if response:
                            if 'test case' in prompt.lower() or 'test cases' in prompt.lower():
                                if '|' in response or ':' in response:
                                    df = parse_structured_text_to_dataframe(response)
                                    if len(df) > 1:  # Only return if we got meaningful data
                                        st.markdown(df.to_html(escape=False), unsafe_allow_html=True)
                            else:
                                st.markdown(response)

                            assistant_message = {"role": "assistant", "content": response}
                            if show_filtering:
                                assistant_message["filter_info"] = "Approved and processed"
                            st.session_state.messages.append(assistant_message)

                            # 🔴 NEW: Auto-save after adding assistant message
                            if st.session_state.auto_save:
                                auto_save_messages()
                        else:
                            st.error("Failed to get response from the AI Assistant")


if st.button('Submit Request'):
    submit_prompt()


# Footer with examples
st.markdown("---")
st.markdown("### 💡 Example Questions You Can Ask:")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    **✅ Good Examples:**
    - "How do I optimize this Python function?"
    - "Explain machine learning model evaluation"
    - "What's a good marketing strategy for SaaS?"
    - "Help me debug this SQL query"
    """)

with col2:
    st.markdown("""
    **❌ Will Be Rejected:**
    - "What should I do about my health issue?"
    - "Give me legal advice about contracts"
    - "What do you think about current politics?"
    - "Help me with personal relationship problems"
    """)