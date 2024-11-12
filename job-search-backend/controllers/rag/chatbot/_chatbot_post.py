from dotenv import load_dotenv
import threading
from langchain_openai import OpenAIEmbeddings, ChatOpenAI

from concurrent.futures import ThreadPoolExecutor, as_completed
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from controllers.rag import _clean_data
from controllers.vector_databases import _qdrant

from models import _environments, _prompts, _constants, _ultils
from controllers.rag import _rag_qdrant, _re_write_query
import gspread
from google.oauth2.service_account import Credentials
import json
import asyncio
import re

load_dotenv()


# Load
# _comment_1 = _ultils.read_content_from_file("files/comments/post_data_4_AI.json")
# _comment_2 = _ultils.read_content_from_file("files/comments/post_data_prompt.json")
# _comment_3 = _ultils.read_content_from_file("files/comments/post_data_chatgpt.json")


############################################################################################################
# Chatbot Post
def chatbot():
    # _comments = [_comment_1, _comment_2, _comment_3]
    #
    # comments = _clean_data.validate_and_fix_braces(_comments)
    comments = ""

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                _prompts.CHATBOT_POST.format(
                    IDENTITY=_prompts.CHATBOT_IDENTITY_TRUC_LINH,
                    # context=str(contexts),
                    comments=comments,
                    # procedure=_prompts.CHATBOT_INTERACTIVE_PROCEDURE,
                ),
            )
        ]
    )

    chain = (
            prompt
            | _environments.get_llm(model="gpt-4o", temperature=1)
            | StrOutputParser()
    )
    answer = chain.invoke({"input": ""})

    print("========================================================")
    print(answer)
    print("========================================================\n")

    return answer


# Mini bot
def mini_bot(query, context):
    context_content = _clean_data.validate_and_fix_braces(context["page_content"])

    context = str(context_content)
    contexts = _clean_data.validate_and_fix_braces(context)

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                _prompts.CHATBOT_INTERACTIVE_MINI_BOT.format(
                    context=str(contexts), query=str(query)
                ),
            ),
            ("human", str(query)),
        ]
    )
    chain = (
            prompt
            | _environments.get_llm(model="gpt-4o-mini", temperature=0)
            | StrOutputParser()
    )
    answer = chain.invoke({"input": str(query)})
    return answer


# Chạy bots song song
def run_bots_in_parallel(bot_params_list):
    results = []
    max_workers = len(bot_params_list)
    if max_workers == 0:
        max_workers = 5

    def task(params):
        keyword, query, context = params

        return mini_bot(query, context)

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_params = {
            executor.submit(task, params): params for params in bot_params_list
        }
        for future in as_completed(future_to_params):
            try:
                result = future.result()
                results.append(result)
            except Exception as exc:
                print(
                    f"Generated an exception run_bots_in_parallel: {exc}, Params: {future_to_params[future]}"
                )
                pass

    return results
