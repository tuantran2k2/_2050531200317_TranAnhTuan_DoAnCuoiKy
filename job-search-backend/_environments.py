from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from dotenv import load_dotenv

from openai import OpenAI

load_dotenv()

########################################################################################

# embeddings_model
embeddings_model = OpenAIEmbeddings()

def custom_llm(model="gpt-4o", temperature=0):
    custom_llm = ChatOpenAI(model=model, temperature=temperature)
    return custom_llm
