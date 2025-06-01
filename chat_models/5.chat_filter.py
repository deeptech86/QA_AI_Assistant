import streamlit as st
import anthropic
from typing import List, Dict, Tuple
import os
import re
import pandas as pd

# Page configuration
st.set_page_config(
    page_title="Restricted Claude Chat",
    page_icon="🔒",
    layout="wide"
)

# Configuration: Define allowed topics and restrictions
ALLOWED_TOPICS = {
    "programming": ["code", "programming", "python", "javascript", "software", "debugging", "algorithm","quality Assurance","testing", "test cases", "automation", "unit tests", "integration tests", "test automation"],
    "data_science": ["data", "analysis", "statistics", "machine learning", "pandas", "numpy", "visualization"],
   
}

FORBIDDEN_TOPICS = [
    "medical advice", "legal advice", "personal information", "harmful content",
    "violence", "illegal activities", "personal relationships", "politics"
]

# System prompt to constrain Claude's behavior
SYSTEM_PROMPT = """You are a specialized AI assistant focused ONLY on helping with:
1. Writing Test Cases for software applications
2. Programming and software development escpecially generating automation code snippets
3. Data science and analytics

The Test Cases you generate should be clear, concise, and follow best practices in the below prescribed format:
FORMAT FOR TEST CASE WRITING:
- **Test Case ID**: A unique identifier for the test case
- **Test Case Description**: A brief description of what the test case is testing
- **Preconditions**: Any setup required before executing the test case
- **Test Steps**: Step-by-step instructions to execute the test case
- **Expected Result**: The expected outcome of the test case
The response for the Test Cases should be in below markdown format :
```markdown
col1, col2,col3, col4,col5 = st.columns(5)
| Test Case ID | Test Case Description | Preconditions | Test Steps | Expected Result |

STRICT RULES:
- ONLY answer questions related to these three topics
- If asked about anything else, politely decline and redirect to allowed topics
- Do not provide medical, legal, or personal advice
- Do not discuss politics, personal relationships, or controversial topics
- If unsure whether a topic is allowed, err on the side of caution and decline

Response format for forbidden topics:
"I'm sorry, but I can only help with programming or data science realted to NGS. Could you ask me something about one of these areas instead?"

Be helpful and detailed for allowed topics, but strict about the boundaries."""

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
            return False, f"Contains forbidden topic: {forbidden}"
    
    # Check for allowed topics
    found_topics = []
    for category, keywords in ALLOWED_TOPICS.items():
        for keyword in keywords:
            if keyword.lower() in text_lower:
                found_topics.append(category)
                break
    
    if found_topics:
        return True, f"Allowed topics found: {', '.join(found_topics)}"
    
    # If no specific topics found, apply more flexible rules
    # Check for programming-related patterns
    code_patterns = [
        r'\bdef\s+\w+\(', r'\bclass\s+\w+', r'\bimport\s+\w+', 
        r'\bfunction\s+\w+', r'[{}();]', r'\b(if|else|for|while)\b'
    ]
    
    for pattern in code_patterns:
        if re.search(pattern, text_lower):
            return True, "Contains code-like content"
    
    # If nothing matches, it's likely not allowed
    return False, "No allowed topics detected"

def filter_user_input(user_input: str) -> Tuple[bool, str]:
    """
    Pre-filter user input before sending to Claude
    Returns: (should_process, message)
    """
    # Basic checks
    if len(user_input.strip()) < 3:
        return False, "Please provide a more detailed question."
    
    # Check topic allowance
    is_allowed, reason = check_topic_allowed(user_input)
    
    if not is_allowed:
        return False, f"I can only help with programming,  or data science. {reason}"
    
    # if 'test case' in user_input.lower():
    #     return True, "Input approved"
    # print(f"User input passed pre-filter: {user_input}")
    
    return True, "Input approved"


def parse_structured_text_to_dataframe(response: str) -> pd.DataFrame:
    """
    Parse structured text response (like tables or lists) into DataFrame
    """
    lines = response.strip().split('\n')
    # lines = response.split(':')[1].split('markdown')[1].splitlines()[3:]
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
                    # df_row=[]
                    # for cell in row:
                    #     if '<br' in cell:
                    #         df_row.append(cell.replace('<br>', '\n'))
                    #     else:
                    #         df_row.append(cell)
                    # data.append(df_row)
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
            return "I apologize, but I cannot provide information on that topic. Please ask me about programming or data science instead."
        
        return response_text
        
    except anthropic.APIError as e:
        st.error(f"API Error: {e}")
        return None
    except Exception as e:
        st.error(f"Unexpected error: {e}")
        return None

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

if "anthropic_client" not in st.session_state:
    st.session_state.anthropic_client = get_anthropic_client()

# Sidebar configuration
with st.sidebar:
    st.title("🔒 QA Assistant_5")
    
    st.markdown("### Allowed GH Topics:")
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
    
    # Clear conversation button
    if st.button("Clear Conversation"):
        st.session_state.messages = []
        st.rerun()

# Main interface
st.title("🔒 QA Agent Assistant_5")
st.markdown("**This AI assistant only answers questions about Programming, Data Science, and Business topics.**")

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
            "Generate API Test Code",
            "Convert Existing Code"
            ""
        )
    )

if main_option == "Generate Unit Test in Java":
    repo_location = st.text_input("Enter the git or local repo location:")

if main_option == "Generate Selenium Code":
        sub_option = st.selectbox("Select language:", [
            "Java",
            "Python",
            "JavaScript",
            "C#"
        ])

if main_option == "Generate TestComplete Code":
        sub_option = st.selectbox("Select language:", [
            "Java",
            "Python",
            "JavaScript",
            "C#"
        ])

if main_option == "Generate API Test Code":
        sub_option = st.selectbox("Select language:", [
            "Java",
            "Python",
            "JavaScript",
        ])

if main_option == "Convert Existing Code":
        sub_option = st.selectbox("Select language:", [
            "Java Selenium to Playwright Javascript",
            "Python Selenium to Playwright Javascript",
            "JavaScript Playwright to Cypress JavaScript",
        ])
        repo_location = st.text_input("Enter the git or local repo location:")

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if show_filtering and "filter_info" in message:
            st.caption(f"Filter info: {message['filter_info']}")

# Chat input
if prompt := st.chat_input("Enter details about the action to be performed.5.chat."):
    # Pre-filter the input
    should_process, filter_message = filter_user_input(prompt)
    # st.write(f"Should Proccess message: {should_process}")
    # Add user message to chat history
    user_message = {"role": "user", "content": prompt}
    if show_filtering:
        user_message["filter_info"] = filter_message
    
    st.session_state.messages.append(user_message)
    
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
        else:
            # Process with Claude
            with st.spinner("Processing your question..."):
                response = call_claude_with_restrictions(
                    st.session_state.anthropic_client,
                    prompt,
                    model=model,
                    max_tokens=max_tokens
                )
                if 'test case' in prompt.lower() or 'test cases' in prompt.lower():


                    if '|' in response or ':' in response:
                        df = parse_structured_text_to_dataframe(response)
                        if len(df) > 1:  # Only return if we got meaningful data
                                st.markdown(df.to_html(escape=False), unsafe_allow_html=True)
                                # st.dataframe(df)
                elif response:
                    st.markdown(response)
                    assistant_message = {"role": "assistant", "content": response}
                    if show_filtering:
                        assistant_message["filter_info"] = "Approved and processed"
                    st.session_state.messages.append(assistant_message)
                else:
                    st.error("Failed to get response from Claude")

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