from controller.load_documents import _load_data
from controller.vector_database import _qdrant
import os
from dotenv import load_dotenv
load_dotenv()


COLLECTION_NAME = os.getenv("COLLECTION_NAME")
docs  = _load_data.process_csv_to_docs("jobs.csv")
_qdrant.save_vector_db(docs ,COLLECTION_NAME )




