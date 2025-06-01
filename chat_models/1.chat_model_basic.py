from langchain_anthropic import ChatAnthropic, ChatAnthropicMessages
from dotenv import load_dotenv

load_dotenv()

llm = ChatAnthropic(model= "claude-3-7-sonnet-20250219")
# messages=[ChatAnthropicMessages(content="What is LangChain?")]

output= llm.invoke("What is LangChain?")
print(output.content)

