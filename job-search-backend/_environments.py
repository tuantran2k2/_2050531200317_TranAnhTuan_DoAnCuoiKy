from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from dotenv import load_dotenv

from openai import OpenAI

load_dotenv()

########################################################################################

# embeddings_model
embeddings_model = OpenAIEmbeddings()

# llm
llm_4o_00_temperature = ChatOpenAI(model="gpt-4o", temperature=0)
llm_4o_05_temperature = ChatOpenAI(model="gpt-4o", temperature=0.5)
llm_4o_10_temperature = ChatOpenAI(model="gpt-4o", temperature=1)
llm_4o_15_temperature = ChatOpenAI(model="gpt-4o", temperature=1.5)


def get_llm(model="gpt-4o", temperature=0.5):
    if model == "gpt-4o":
        if temperature == 0:
            return llm_4o_00_temperature
        elif temperature == 0.5:
            return llm_4o_05_temperature
        elif temperature == 1:
            return llm_4o_10_temperature
        elif temperature == 1.5:
            return llm_4o_15_temperature
        else:
            return ChatOpenAI(model=model, temperature=temperature)
    else:
        return ChatOpenAI(model=model, temperature=temperature)
