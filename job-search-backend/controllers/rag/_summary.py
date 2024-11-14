import os
import aiohttp
import base64
import asyncio
from langchain.prompts import ChatPromptTemplate
from langchain.schema.output_parser import StrOutputParser
from openai import OpenAI

import _constants, _environments, _prompts


def summary_history(answer):
    # Tóm tắt câu trả lời
    summary_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", _prompts.SUMMARY_HISTORY),
            ("human", answer),
        ]
    )

    summary_chain = (
            summary_prompt
            | _environments.get_llm(model="gpt-4o-mini", temperature=0)
            | StrOutputParser()
    )
    summary = summary_chain.invoke({"input": answer})

    return summary
