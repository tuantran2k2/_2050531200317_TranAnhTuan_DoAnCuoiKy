from dotenv import load_dotenv
import threading
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from controllers.rag import _clean_data

import _environments, _prompts ,_constants
from database._qdrant  import load_vector_db
from controllers.rag import _rag_qdrant
from langchain_openai import OpenAIEmbeddings, ChatOpenAI

load_dotenv()


############################################################################################################
# Chatbot truy vấn toàn văn
def chatbot_rag_crewai(
    query
):
    print(query)
    db = load_vector_db(_constants.COLLECTION)
    
    print(db)
    
    retriever = _rag_qdrant.retriever_question(db, query, _constants.COLLECTION)
   

    contexts = _clean_data.validate_and_fix_braces(retriever)

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
        | _environments.get_llm(model="gpt-4o", temperature=0.7)
        | StrOutputParser()
    )
    
    answer = chain.invoke({"input": str(query)})

    return answer
