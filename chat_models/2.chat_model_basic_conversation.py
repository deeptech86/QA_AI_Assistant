from langchain_anthropic import ChatAnthropic
from dotenv import load_dotenv
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

load_dotenv()

llm = ChatAnthropic(model= "claude-3-7-sonnet-20250219")
messages=[
    SystemMessage(content="You are a helpful assistant."),
    HumanMessage(content="What is LangChain?"),
    # AIMessage(content="LangChain is a framework for developing applications powered by language models.")
    HumanMessage(content="Is LangGraph part of LangChain?")
    ]

output= llm.invoke(messages)
print(output.content)