from dotenv import load_dotenv
import threading
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from controllers.rag import _clean_data
from pathlib import Path
import _environments, _prompts ,_constants
from database._qdrant  import load_vector_db
from controllers.rag import _rag_qdrant
from langchain_openai import OpenAIEmbeddings, ChatOpenAI

load_dotenv()


############################################################################################################
# Chatbot truy vấn toàn văn
def chatbot_rag_crewai(
    query,k,collection_id,ma_KH,id_cv
):
    db = load_vector_db(_constants.COLLECTION)

    
    retriever = _rag_qdrant.retriever_question(db, query, _constants.COLLECTION , k )
   

    contexts = _clean_data.validate_and_fix_braces(retriever)
    
    file_dir = Path(f"./files/data/{ma_KH}")
    file_dir.mkdir(parents=True, exist_ok=True)
    
    # Tạo đường dẫn file với tên theo định dạng yêu cầu
    file_path = file_dir / f"{id_cv}_{collection_id}_listCV.txt"

    # Lưu file vào thư mục
    with file_path.open("wb") as buffer:
        buffer.write(contexts.encode('utf-8'))  # Ghi nội dung file từ bộ nhớ

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                _prompts.JOBS_CV.format(
                Context=str(contexts), query=str(query)
                ),
            ),
            ("human", str(query)),
        ]
    )

    chain = (
        prompt
        | _environments.custom_llm()
        | StrOutputParser()
    )
    
    answer = chain.invoke({"input": str(query)})

    return answer
