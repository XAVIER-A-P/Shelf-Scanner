import boto3
from botocore.exceptions import NoCredentialsError
from app.config import settings
from fastapi import UploadFile

s3_client = boto3.client(
    's3',
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
)

async def upload_image_to_s3(file: UploadFile, filename: str) -> str:
    try:
        s3_client.upload_fileobj(
            file.file,
            settings.AWS_BUCKET_NAME,
            filename,
            ExtraArgs={'ACL':'public-red', 'ContentType': file.content_type}
        )
        return f"https://{settings.AWS_BUCKET_NAME}.s3.amazonaws.com/{filename}"
    except NoCredentialsError:
        raise Exception("AWS Credentials not aviliable")
    