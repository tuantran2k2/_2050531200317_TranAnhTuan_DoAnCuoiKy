# qdrant_client.py
from langchain_qdrant import Qdrant
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from qdrant_client.http import models
import os
from dotenv import load_dotenv


load_dotenv()

# Lấy các biến môi trường từ file .env
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
QDRANT_URL = os.getenv("QDRANT_URL")
COLLECTION_NAME = os.getenv("COLLECTION_NAME")
VECTOR_SIZE = os.getenv("VECTOR_SIZE")
QDRANT_SERVER = os.getenv("QDRANT_SERVER")

embeddings_model = OpenAIEmbeddings()

def save_vector_db(docs, collection_name, point_ids):
    qdrant_doc = Qdrant.from_documents(
        documents=docs,
        embedding=embeddings_model,
        url=QDRANT_SERVER,
        prefer_grpc=False,
        collection_name=collection_name,
        api_key=QDRANT_API_KEY,
        ids=point_ids,
    )

    return qdrant_doc


def load_vector_db(collection_names):
    try:
        client = Qdrant.from_existing_collection(
            embedding=embeddings_model,
            collection_name=collection_names,
            url=QDRANT_SERVER,
            api_key=QDRANT_API_KEY,
        )
        return client
    except Exception:
        a = "None"
        return a