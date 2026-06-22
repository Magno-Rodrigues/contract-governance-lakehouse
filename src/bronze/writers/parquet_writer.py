from pyspark.sql import DataFrame


class BronzeParquetWriter:
    """
    Writer responsável por persistir DataFrames Bronze em Parquet.

    A escrita fica isolada em uma classe própria para evitar que o pipeline
    conheça detalhes de persistência.

    No futuro, poderíamos trocar ou expandir o writer para:
    - Delta Lake;
    - Iceberg;
    - Hudi;
    - tabelas externas no Glue Catalog;
    - escrita particionada avançada.
    """

    def __init__(self, bucket_name: str, bronze_prefix: str = "bronze"):
        """
        Inicializa o writer com bucket e prefixo da camada Bronze.

        Parameters
        ----------
        bucket_name : str
            Nome do bucket no MinIO/S3.

        bronze_prefix : str
            Prefixo da camada Bronze dentro do bucket.
        """
        self.bucket_name = bucket_name
        self.bronze_prefix = bronze_prefix

    def build_output_path(
        self,
        dataset_name: str,
        snapshot_date: str,
        source_type: str,
    ) -> str:
        """
        Monta o caminho de destino da tabela Bronze.

        Estrutura proposta:
            s3a://bucket/bronze/source_type=csv/dataset=nome/snapshot_date=...

        Essa estrutura facilita:
        - auditoria;
        - reprocessamento por snapshot;
        - filtros por dataset;
        - evolução futura para catálogo cloud.
        """

        return (
            f"s3a://{self.bucket_name}/"
            f"{self.bronze_prefix}/"
            f"source_type={source_type}/"
            f"dataset={dataset_name}/"
            f"snapshot_date={snapshot_date}/"
        )

    def write(
        self,
        df: DataFrame,
        dataset_name: str,
        snapshot_date: str,
        source_type: str,
        mode: str = "overwrite",
    ) -> str:
        """
        Escreve o DataFrame Bronze em Parquet.

        Parameters
        ----------
        df : DataFrame
            DataFrame Spark enriquecido com metadados Bronze.

        dataset_name : str
            Nome técnico do dataset.

        snapshot_date : str
            Snapshot do arquivo processado.

        source_type : str
            Tipo técnico da fonte.

        mode : str
            Modo de escrita Spark. Inicialmente usamos overwrite para
            permitir reprocessar o mesmo snapshot durante desenvolvimento.

        Returns
        -------
        str
            Caminho final onde o Parquet foi gravado.
        """

        output_path = self.build_output_path(
            dataset_name=dataset_name,
            snapshot_date=snapshot_date,
            source_type=source_type,
        )

        (
            df.write
            .mode(mode)
            .parquet(output_path)
        )

        return output_path