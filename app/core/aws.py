from botocore.exceptions import BotoCoreError, ClientError
import boto3
from app.core.config import get_settings


def get_s3_client():
    settings = get_settings()
    kwargs = {'region_name': settings.aws_region}
    if settings.aws_access_key_id and settings.aws_secret_access_key:
        kwargs['aws_access_key_id'] = settings.aws_access_key_id
        kwargs['aws_secret_access_key'] = settings.aws_secret_access_key
    return boto3.client('s3', **kwargs)


def upload_and_sign(key: str, body: str) -> str:
    settings = get_settings()
    if not settings.s3_bucket:
        raise RuntimeError('S3 is not configured')
    client = get_s3_client()
    try:
        client.put_object(Bucket=settings.s3_bucket, Key=key, Body=body.encode('utf-8'), ContentType='text/csv')
        return client.generate_presigned_url('get_object', Params={'Bucket': settings.s3_bucket, 'Key': key}, ExpiresIn=3600)
    except (BotoCoreError, ClientError) as exc:
        raise RuntimeError('Failed to upload statement') from exc
