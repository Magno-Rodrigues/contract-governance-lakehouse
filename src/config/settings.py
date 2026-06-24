import os
from pathlib import Path


class Settings:
    """
    Centraliza configurações globais do projeto.

    Nenhuma configuração de ambiente deve ficar hardcoded
    em notebooks ou pipelines.
    """

    # Project paths
    PROJECT_ROOT = Path("/app")
    RAW_LOCAL_PATH = PROJECT_ROOT / "data" / "raw_local" / "RAW"
    LANDING_METADATA_PATH = PROJECT_ROOT / "data" / "landing_metadata.csv"
    
    # Bronze logs
    BRONZE_EXECUTION_LOG_PATH = (
    PROJECT_ROOT / "data" / "bronze_execution_log.csv"
    )

    # MinIO / S3
    MINIO_ENDPOINT = os.getenv(
        "S3_ENDPOINT",
        "http://minio:9000"
    )

    AWS_ACCESS_KEY = os.getenv(
        "AWS_ACCESS_KEY_ID",
        "admin"
    )

    AWS_SECRET_KEY = os.getenv(
        "AWS_SECRET_ACCESS_KEY",
        "admin12345"
    )

    AWS_REGION = os.getenv(
        "AWS_REGION",
        "us-east-1"
    )

    # Spark
    SPARK_MASTER_URL = os.getenv(
        "SPARK_MASTER_URL",
        "spark://spark-master:7077"
    )

    SPARK_EXTRA_JARS = (
        "/opt/spark/jars_extra/"
        "hadoop-aws-3.3.4.jar,"
        "/opt/spark/jars_extra/"
        "aws-java-sdk-bundle-1.12.262.jar"
    )

    # Storage
    BUCKET_NAME = os.getenv(
        "MINIO_BUCKET",
        "contracts"
    )
    
    BRONZE_QUALITY_LOG_PATH = (
    PROJECT_ROOT / "data" / "bronze_quality_log.csv"
    )

    # Lakehouse prefixes
    LANDING_PREFIX = "landing"
    BRONZE_PREFIX = "bronze"

    # Pipeline versions
    BRONZE_PIPELINE_VERSION = "bronze_v1"
