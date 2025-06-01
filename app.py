import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

# Load environment variables
load_dotenv()

def main():
    # Initialize LLM
    llm = ChatOpenAI(
        temperature=0.7,
        openai_api_key=os.getenv("OPENAI_API_KEY")
    )
    
    # Create prompt template
    prompt = PromptTemplate(
        input_variables=["question"],
        template="Answer the following question: {question}"
    )
    
    # Create chain
    chain = LLMChain(llm=llm, prompt=prompt)
    
    # Example usage
    response = chain.run(question="What is LangChain?")
    print(response)

if __name__ == "__main__":
    main()
