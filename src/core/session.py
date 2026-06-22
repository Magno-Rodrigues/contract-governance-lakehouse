from pyspark.sql import SparkSession

from src.config.settings import Settings


class SparkFactory:
    """
    Factory responsável por criar SparkSession.

    Centralizar configuração evita duplicação
    entre notebooks e pipelines.
    """

    @staticmethod
    def create() -> SparkSession:
        """
        Cria sessão Spark padronizada do projeto.
        """

        spark = (
            SparkSession.builder

            .appName("contract-lakehouse")

            .master(
                Settings.SPARK_MASTER_URL
            )

            .config(
                "spark.jars",
                Settings.SPARK_EXTRA_JARS
            )

            .config(
                "spark.driver.extraClassPath",
                "/opt/spark/jars_extra/*"
            )

            .config(
                "spark.executor.extraClassPath",
                "/opt/spark/jars_extra/*"
            )

            .config(
                "spark.hadoop.fs.s3a.endpoint",
                Settings.MINIO_ENDPOINT
            )

            .config(
                "spark.hadoop.fs.s3a.access.key",
                Settings.AWS_ACCESS_KEY
            )

            .config(
                "spark.hadoop.fs.s3a.secret.key",
                Settings.AWS_SECRET_KEY
            )

            .config(
                "spark.hadoop.fs.s3a.path.style.access",
                "true"
            )

            .config(
                "spark.hadoop.fs.s3a.connection.ssl.enabled",
                "false"
            )

            .config(
                "spark.hadoop.fs.s3a.impl",
                "org.apache.hadoop.fs.s3a.S3AFileSystem"
            )

            .getOrCreate()
        )

        return spark