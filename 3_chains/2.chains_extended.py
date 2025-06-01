from langchain_anthropic import ChatAnthropic
from dotenv import load_dotenv
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate, HumanMessagePromptTemplate
from langchain_core.runnables import RunnableLambda,RunnableParallel
from langchain.schema.output_parser import StrOutputParser

load_dotenv()



llm = ChatAnthropic(model= "claude-3-7-sonnet-20250219")
# template ="Tell me a joke about {topic} doing {action}."
# prompt_template = ChatPromptTemplate.from_template(template)

# prompt =  prompt_template.invoke({"topic":"cats", "action":"dancing"}) 

# response = llm.invoke(prompt)
# print(response.content)

messages =[
    ("system", "You are a comdeian who jokes ."),
    ("human", "Tell me a joke about {company_name} ."),
 
]

prompt_template = ChatPromptTemplate.from_messages(messages)
# prompt = prompt_template.invoke({"company_name":"Tesla"})




upperCase =  RunnableLambda(lambda x: x.upper())
wordCount = RunnableLambda(lambda x: f"{len(x.split())}\n{x}")


chain = prompt_template | llm | StrOutputParser() | upperCase | wordCount


response = chain.invoke({"company_name":"Tesla"})

# print(StrOutputParser())

print(response)