from pathlib import Path
import os


# Diretório raiz do projeto dentro do container.
PROJECT_ROOT = Path("/app")

# Caminho local onde os snapshots RAW ficam montados.
RAW_LOCAL_PATH = PROJECT_ROOT / "data" / "raw_local" / "RAW"

# Configurações do MinIO/S3 compatível.
MINIO_ENDPOINT = os.getenv("S3_ENDPOINT", "http://minio:9000")
MINIO_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY_ID", "admin")
MINIO_SECRET_KEY = os.getenv("AWS_SECRET_ACCESS_KEY", "admin12345")
MINIO_REGION = os.getenv("AWS_REGION", "us-east-1")

# Bucket principal do lakehouse.
BUCKET_NAME = os.getenv("MINIO_BUCKET", "contracts")

# Prefixos das camadas no object storage.
LANDING_PREFIX = "landing"

# Caminho local para salvar metadados da Landing.
LANDING_METADATA_PATH = PROJECT_ROOT / "data" / "landing_metadata.csv"