import os


class Settings:
    """
    Centraliza configurações globais do projeto.

    Nenhuma configuração de ambiente deve ficar hardcoded
    em notebooks ou pipelines.
    """

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
    BUCKET_NAME = "contracts"
    BRONZE_PIPELINE_VERSION = "bronze_v1"