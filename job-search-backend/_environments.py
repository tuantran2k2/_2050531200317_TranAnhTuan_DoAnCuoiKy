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

llm_4o_mini_0_temperature = ChatOpenAI(model="gpt-4o-mini", temperature=0)
llm_4o_mini_05_temperature = ChatOpenAI(model="gpt-4o-mini", temperature=0.5)
llm_4o_mini_10_temperature = ChatOpenAI(model="gpt-4o-mini", temperature=1)

llm_35 = ChatOpenAI(model="gpt-3.5-turbo-16k", temperature=0.5)

# llm stream
llm_4o_00_stream_temperature = ChatOpenAI(model="gpt-4o", temperature=0, streaming=True)
llm_4o_05_stream_temperature = ChatOpenAI(model="gpt-4o", temperature=0.5, streaming=True)
llm_4o_10_stream_temperature = ChatOpenAI(model="gpt-4o", temperature=1, streaming=True)
llm_4o_15_stream_temperature = ChatOpenAI(model="gpt-4o", temperature=1.5, streaming=True)

llm_4o_mini_0_stream_temperature = ChatOpenAI(model="gpt-4o-mini", temperature=0, streaming=True)
llm_4o_mini_05_stream_temperature = ChatOpenAI(model="gpt-4o-mini", temperature=0.5, streaming=True)
llm_4o_mini_10_stream_temperature = ChatOpenAI(model="gpt-4o-mini", temperature=1, streaming=True)


def custom_llm(model="gpt-4o", temperature=0.5):
    custom_llm = ChatOpenAI(model=model, temperature=temperature)
    return custom_llm


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

    elif model == "gpt-4o-mini":
        if temperature == 0:
            return llm_4o_mini_0_temperature
        elif temperature == 0.5:
            return llm_4o_mini_05_temperature
        elif temperature == 1:
            return llm_4o_mini_10_temperature
        else:
            return ChatOpenAI(model=model, temperature=temperature)

    elif model == "gpt-3.5-turbo-16k":
        return llm_35


    else:
        return ChatOpenAI(model=model, temperature=temperature)


def get_llm_stream(model="gpt-4o", temperature=0.5):
    if model == "gpt-4o":
        if temperature == 0:
            return llm_4o_00_stream_temperature
        elif temperature == 0.5:
            return llm_4o_05_stream_temperature
        elif temperature == 1:
            return llm_4o_10_stream_temperature
        elif temperature == 1.5:
            return llm_4o_15_stream_temperature
        else:
            return ChatOpenAI(model=model, temperature=temperature, streaming=True)

    elif model == "gpt-4o-mini":
        if temperature == 0:
            return llm_4o_mini_0_stream_temperature
        elif temperature == 0.5:
            return llm_4o_mini_05_stream_temperature
        elif temperature == 1:
            return llm_4o_mini_10_stream_temperature
        else:
            return ChatOpenAI(model=model, temperature=temperature, streaming=True)

    else:
        return ChatOpenAI(model=model, temperature=temperature, streaming=True)
