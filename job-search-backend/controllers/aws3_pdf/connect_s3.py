import boto3
from loguru import logger

import _constants

from dotenv import load_dotenv
import os

load_dotenv()

AWS_REGION = os.getenv("AWS_DEFAULT_REGION")

SUPPORT_FILE_TYPES = {
    "application/pdf": "pdf",
}

AWS_BUCKET = _constants.AWS_BUCKET_NAME

s3 = boto3.resource("s3")
bucket = s3.Bucket(AWS_BUCKET)


async def s3_upload(contents: bytes, key: str, mime_type: str):
    if mime_type not in SUPPORT_FILE_TYPES:
        raise ValueError(f"Unsupported file type: {mime_type}")

    logger.info(f"Uploading {key} to S3")
    bucket.put_object(Key=key, Body=contents, ContentType=mime_type)
    file_url = f"https://{AWS_BUCKET}.s3.{AWS_REGION}.amazonaws.com/{key}"
    logger.info(f"File uploaded successfully: {file_url}")
    return file_url
