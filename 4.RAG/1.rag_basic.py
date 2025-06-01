from dotenv import load_dotenv
from langchain.prompts import ChatPromptTemplate
from langchain.schema.output_parser import StrOutputParser
from langchain.schema.runnable import RunnableBranch
from langchain_anthropic import ChatAnthropic
import voyageai
import os
from langchain.vectorstores import Chroma

llm = voyageai.Client(model="voyage-3.5")
# This will automatically use the environment variable VOYAGE_API_KEY.
# Alternatively, you can use vo = voyageai.Client(api_key="<your secret key>")

# Prepare Data
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
file_path = os.path.join(parent_dir, "resources", "story1.txt")
#Chroma directory
db_directory = os.path.join(parent_dir, "resources", "chroma_db")
persitant_directory = os.path.join(db_directory, "chroma_db","db")


if not os.path.exists(db_directory):
    os.makedirs(db_directory)

# if not os.path.exists(persistant_directory):
#     os.makedirs(persistant_directory)


# Load the text file
with open(file_path, "r") as file:
    documents = file.readlines()

#Split the documents into chunks




# Embed the documents
documents_embeddings = vo.embed(
    documents,llm , input_type="document"
).embeddings