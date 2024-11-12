from controllers.rag import _rag_qdrant, _history, _clean_data
import _prompts, _environments
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser


def query_detection(query):
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", _prompts.INTENT_DETECTION.format(query=str(query))),
            ("human", str(query)),
        ]
    )
    chain = (
            prompt | _environments.get_llm("gpt-4o-mini", temperature=0) | StrOutputParser()
    )
    results = chain.invoke({"input": str(query)})
    return results


def keyword_analysis(context, idea):
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                _prompts.KEYWORD_ANALYSIS.format(context=str(context), idea=str(idea)),
            ),
            ("human", str(context)),
        ]
    )
    chain = (
            prompt
            | _environments.get_llm("gpt-4o-mini", temperature=0.5)
            | StrOutputParser()
    )
    results = chain.invoke({"input": str(context)})
    return results


def simple_query(query, prompt):
    chain = (
            prompt | _environments.get_llm("gpt-4o-mini", temperature=0) | StrOutputParser()
    )
    results = chain.invoke({"input": str(query)})

    return results


def rewrite_query(query, prompt):
    chain = (
            prompt | _environments.get_llm("gpt-4o-mini", temperature=0) | StrOutputParser()
    )
    results = chain.invoke({"input": str(query)})

    return results
