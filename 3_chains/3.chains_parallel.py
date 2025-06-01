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
    ("system", "You are a stock reviewer who reviews companies to invest ."),
    ("human", "Review whether to invest in stock {company_name} ."),
 
]

prompt_template = ChatPromptTemplate.from_messages(messages)
# prompt = prompt_template.invoke({"company_name":"Tesla"})


pros_chain = (
        RunnableLambda(lambda x: f"Pros of investing in {x}")| llm | StrOutputParser()
)

cons_chain = (
        RunnableLambda(lambda x: f"Cons of investing in {x}")| llm | StrOutputParser()
)


def combine_pros_and_cons(pros, cons):
    return f"Pros: {pros}\nCons: {cons}"


chain = (
    prompt_template | 
    llm | 
    StrOutputParser() | 
    RunnableParallel(
        branches=
        {
            "pros": pros_chain,
            "cons": cons_chain
        }
    ) | 
    RunnableLambda(lambda x: print(x) or combine_pros_and_cons(x["branches"]["pros"],x["branches"]["cons"] ) )
)


response = chain.invoke({"company_name":"Tesla"})

# print(StrOutputParser())

print(response)