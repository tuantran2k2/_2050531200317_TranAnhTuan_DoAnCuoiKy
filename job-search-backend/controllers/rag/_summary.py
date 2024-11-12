import os
import aiohttp
import base64
import asyncio
from langchain.prompts import ChatPromptTemplate
from langchain.schema.output_parser import StrOutputParser
from openai import OpenAI

from models import _constants, _environments, _prompts


# Xử lý Table
def summary_table(table):
    prompt = ChatPromptTemplate.from_template(_prompts.SUMMARY_TABLE)

    # Summary chain
    summarize_chain = (
            prompt
            | _environments.get_llm(model="gpt-4o-mini", temperature=0)
            | StrOutputParser()
    )
    table_summaries = summarize_chain.invoke(table)

    # print("Table: ", table)
    # print("Table summaries: ", table_summaries)
    # print("\n\n\n")

    return table_summaries


# Xử lý Images
def encode_image(image_path):
    """Lấy chuỗi base64 từ ảnh"""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


async def fetch(session, url, headers, payload):
    async with session.post(url, headers=headers, json=payload) as response:
        return await response.json()


async def image_summarize_url(url, prompt):
    """Image summary"""
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer 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",
    }

    payloadBase64 = {
        "model": "gpt-4o-mini",
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {"url": url},
                    },
                ],
            }
        ],
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(
                "https://gateway.ai.cloudflare.com/v1/797c69b132e958625fd4f54400ceb86d/mekong-ai/openai/chat/completions",
                headers=headers,
                json=payloadBase64,
        ) as response:
            if response.status == 200:
                try:
                    data = await response.json()
                except Exception as e:
                    print(f"image_summarize Error decoding JSON: {e}")
                    return "NULL"

                # Kiểm tra dữ liệu để tránh lỗi KeyError
                if isinstance(data, dict):
                    if (
                            "choices" in data
                            and isinstance(data["choices"], list)
                            and data["choices"]
                    ):
                        return (
                            data["choices"][0].get("message", {}).get("content", "NULL")
                        )
            else:
                print(
                    f"image_summarize Request failed with status code: {response.status}"
                )
                return "NULL"

    return "NULL"


async def image_summarize(img_base64, prompt):
    """Image summary"""
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer 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",
    }

    payloadBase64 = {
        "model": "gpt-4o-mini",
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{img_base64}"},
                    },
                ],
            }
        ],
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(
                "https://gateway.ai.cloudflare.com/v1/797c69b132e958625fd4f54400ceb86d/mekong-ai/openai/chat/completions",
                headers=headers,
                json=payloadBase64,
        ) as response:
            if response.status == 200:
                try:
                    data = await response.json()
                except Exception as e:
                    print(f"image_summarize Error decoding JSON: {e}")
                    return "NULL"

                # Kiểm tra dữ liệu để tránh lỗi KeyError
                if isinstance(data, dict):
                    if (
                            "choices" in data
                            and isinstance(data["choices"], list)
                            and data["choices"]
                    ):
                        return (
                            data["choices"][0].get("message", {}).get("content", "NULL")
                        )
            else:
                print(
                    f"image_summarize Request failed with status code: {response.status}"
                )
                return "NULL"

    return "NULL"


client = OpenAI(api_key="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")


async def image_summary_openai(img_url):
    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": _prompts.POST_SUMMARY_IMAGE,
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": img_url,
                        },
                    }
                ],
            }
        ],
        max_tokens=500,
    )
    print("??? " + response.choices[0])
    print("????? " + response.choices[0].message.content)
    return response.choices[0].message.content


async def process_image(img_file, path):
    img_path = os.path.join(path, img_file)
    base64_image = encode_image(img_path)
    summary = await image_summarize(base64_image, _prompts.SUMMARY_IMAGE)
    return base64_image, summary, img_file


async def generate_img_summaries(path):
    """
    Tạo các chuỗi base64 cho các ảnh
    path: Đường dẫn tới thư mục chứa các file .jpg được tách ra bởi Unstructured

    """
    img_base64_list = []
    image_summaries = []
    list_file_name = []

    # Tạo danh sách các tác vụ cho từng ảnh
    tasks = []
    for img_file in sorted(os.listdir(path)):
        if img_file.endswith(".jpg"):
            tasks.append(process_image(img_file, path))

    # Chạy các tác vụ song song
    results = await asyncio.gather(*tasks)

    # Lưu trữ kết quả
    for base64_image, summary, img_file in results:
        list_file_name.append(img_file)
        img_base64_list.append(base64_image)
        image_summaries.append(summary)

    return img_base64_list, image_summaries, list_file_name


async def __generate_img_summaries(path):
    img_base64_list, image_summaries, list_file_name = await generate_img_summaries(
        path
    )
    return img_base64_list, image_summaries, list_file_name


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
