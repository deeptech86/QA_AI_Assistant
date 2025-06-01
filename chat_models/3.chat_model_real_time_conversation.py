from langchain_anthropic import ChatAnthropic
from dotenv import load_dotenv
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

load_dotenv()

chat_history = []

llm = ChatAnthropic(model= "claude-3-7-sonnet-20250219")

system_message = SystemMessage(content="You are a helpful assistant.")
chat_history.append(system_message)

while True:
    query=input("you:")
    if query.lower() == "exit":
        break
    else:
        human_message = HumanMessage(content=query)
        chat_history.append(human_message)
        output= llm.invoke(chat_history)
        AI_Message = AIMessage(content=output.content)
        print("AI:", output.content)
        chat_history.append(AI_Message)
        


