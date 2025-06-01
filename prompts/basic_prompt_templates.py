from langchain_anthropic import ChatAnthropic
from dotenv import load_dotenv
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate, HumanMessagePromptTemplate

load_dotenv()



llm = ChatAnthropic(model= "claude-3-7-sonnet-20250219")
# template ="Tell me a joke about {topic} doing {action}."
# prompt_template = ChatPromptTemplate.from_template(template)

# prompt =  prompt_template.invoke({"topic":"cats", "action":"dancing"}) 

# response = llm.invoke(prompt)
# print(response.content)

messages =[
    ("system", "You are a comedian who tells jokes about about {topic}."),
    ("human", "Tell me a joke doing {action}."),
 
]

prompt_template = ChatPromptTemplate.from_messages(messages)
prompt = prompt_template.invoke({"topic":"cats", "action":"dancing"})
print(prompt)
response = llm.invoke(prompt)
print(response.content)


