import boto3
import os
from botocore.exceptions import NoCredentialsError
from dotenv import load_dotenv
import uuid

load_dotenv()

ACCESS_KEY = os.getenv("AWS_ACCESS_KEY_ID")
SECRET_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
BUCKET_NAME = os.getenv("AWS_BUCKET_NAME")
REGION = os.getenv("AWS_REGION", "us-east-1")

s3_client = boto3.client(
    's3',
    aws_access_key_id=ACCESS_KEY,
    aws_secret_access_key=SECRET_KEY,
    region_name=REGION
)

def generate_presigned_url(file_name: str, file_type: str):
    """
    Generates a pre-signed URL so frontend can upload directly to S3.
    This is more secure and faster than sending files through the backend.
    """
    unique_filename = f"uploads/{uuid.uuid4()}-{file_name}"
    
    try:
        # Generate the presigned URL for PUT requests
        presigned_url = s3_client.generate_presigned_url(
            'put_object',
            Params={
                'Bucket': BUCKET_NAME,
                'Key': unique_filename,
                'ContentType': file_type
            },
            ExpiresIn=300 # 5 minutes
        )
        
        # The public URL where the file will be accessible
        file_url = f"https://{BUCKET_NAME}.s3.{REGION}.amazonaws.com/{unique_filename}"
        
        return {"upload_url": presigned_url, "file_url": file_url}
        
    except NoCredentialsError:
        return None