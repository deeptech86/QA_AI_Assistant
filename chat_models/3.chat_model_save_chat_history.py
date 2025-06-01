from langchain_anthropic import ChatAnthropic
# from pydantic import BaseModel
from dotenv import load_dotenv
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_google_firestore  import FirestoreChatMessageHistory
from google.cloud import firestore
from google.auth import compute_engine
import streamlit as st



load_dotenv()

PROJECT_ID = "langchain-backend"
SESSION_ID = "anthropic-session_3"
COLLECTION_ID = "chat_history"


st.title("Test Case Generator")
load_dotenv()

chat_history = []
st.session_state.messages = []



# Save chat history to a file
# Initialize Firebase Client
print("Initialize Firebase Client")
# client = firestore.Client(project=PROJECT_ID,credentials=compute_engine.Credentials())
# client = FirestoreClient(project_id=PROJECT_ID)


chat_history = FirestoreChatMessageHistory( 
    session_id=SESSION_ID,
    collection=COLLECTION_ID)

print("chat history initialized")
st.write("Chat History:")

print("current chat history:", chat_history.messages)

llm = ChatAnthropic(model= "claude-3-7-sonnet-20250219")

system_message = SystemMessage(content="You are a helpful assistant.")
chat_history.add_message(system_message)

while True:
    human_input=input("you:")
    if human_input.lower() == "exit":
        break
    else:
        
        chat_history.add_user_message(human_input)
        AI_response = llm.invoke(chat_history.messages)
        chat_history.add_ai_message(AI_response.content)
        print("AI:", AI_response.content)


# streamlit_chat_history = chat_history.messages

