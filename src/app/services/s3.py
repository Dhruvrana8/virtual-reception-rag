import boto3
from botocore.exceptions import NoCredentialsError
from fastapi import UploadFile
from ..config import settings

def upload_file_to_s3(file: UploadFile, filename: str):
    s3 = boto3.client(
        's3',
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_REGION
    )

    try:
        s3.upload_fileobj(file.file, settings.S3_BUCKET_NAME, filename)
        return f"https://{settings.S3_BUCKET_NAME}.s3.amazonaws.com/{filename}"
    except NoCredentialsError:
        return None
