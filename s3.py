import boto3
from botocore.client import Config
from config import ACCESS_KEY_ID, ACCESS_SECRET_KEY, BUCKET_NAME

s3 = boto3.resource(
    's3',
    aws_access_key_id=ACCESS_KEY_ID,
    aws_secret_access_key=ACCESS_SECRET_KEY,
    config=Config(signature_version='s3v4')
)


def upload_to_s3(img_name):
    try:
        file = open(f'temp_media/{img_name}', 'rb')
        s3.Bucket(BUCKET_NAME).put_object(Key=img_name, Body=file, ACL='public-read')
    except Exception:
        print("Upload to s3 error")
