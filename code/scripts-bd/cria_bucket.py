import os
from pathlib import Path

import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv

# Caminho base do projeto (um nível acima da pasta scripts-bd)
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / "env.conf")

bucket = os.environ.get("SEAWEEDFS_BUCKET")

cliente = boto3.client(
    "s3",
    endpoint_url=os.environ.get("SEAWEEDFS_ENDPOINT"),
    aws_access_key_id=os.environ.get("SEAWEEDFS_ACCESS_KEY"),
    aws_secret_access_key=os.environ.get("SEAWEEDFS_SECRET_KEY"),
    region_name="us-east-1",
)

# Cria o bucket somente se ele ainda não existir
try:
    cliente.head_bucket(Bucket=bucket)
    print(f"O bucket {bucket} já existe.")
except ClientError:
    cliente.create_bucket(Bucket=bucket)
    print(f"Bucket {bucket} criado com sucesso.")
