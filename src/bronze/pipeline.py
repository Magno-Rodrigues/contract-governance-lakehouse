from pyspark.sql import DataFrame

from src.core.session import SparkFactory
from src.config.settings import Settings
from src.bronze.registry import ReaderRegistry
from src.bronze.converters.pandas_to_spark import PandasToSparkConverter
from src.bronze.metadata import enrich_with_bronze_metadata
from src.bronze.writers.parquet_writer import BronzeParquetWriter


class BronzePipeline:
    """
    Pipeline principal da Bronze Layer.

    Responsabilidade:
    -----------------
    Orquestrar leitura, conversão, enriquecimento de metadados
    e escrita em Parquet.

    Importante:
    -----------
    O pipeline não conhece detalhes de CSV, Excel, API ou banco.
    Ele delega a leitura para o ReaderRegistry.
    """

    def __init__(self) -> None:
        """
        Inicializa dependências do pipeline Bronze.
        """

        self.spark = SparkFactory.create()

        self.writer = BronzeParquetWriter(
            bucket_name=Settings.BUCKET_NAME,
            bronze_prefix="bronze"
        )

    def run(
        self,
        source_path: str,
        source_type: str,
        dataset_name: str,
        snapshot_date: str,
        source_file: str,
        file_hash: str,
    ) -> str:
        """
        Executa ingestão Bronze para uma fonte.

        Parameters
        ----------
        source_path : str
            Caminho local ou remoto da fonte.

        source_type : str
            Tipo técnico da fonte: csv, xlsx, xlsb, api, postgres etc.

        dataset_name : str
            Nome técnico do dataset na Bronze.

        snapshot_date : str
            Snapshot de referência da fonte.

        source_file : str
            Nome original do arquivo ou identificador da fonte.

        file_hash : str
            Hash SHA-256 calculado na Landing.

        Returns
        -------
        str
            Caminho onde o Parquet Bronze foi gravado.
        """

        # Resolve reader correto com base no source_type.
        reader_class = ReaderRegistry.get_reader(source_type)

        # Instancia o reader.
        reader = reader_class()

        # Lê origem e retorna Pandas DataFrame.
        pandas_df = reader.read(source_path)

        # Converte Pandas DataFrame para Spark DataFrame.
        spark_df: DataFrame = PandasToSparkConverter.convert(
            spark=self.spark,
            pandas_df=pandas_df
        )

        # Adiciona metadados técnicos da Bronze.
        bronze_df = enrich_with_bronze_metadata(
            df=spark_df,
            snapshot_date=snapshot_date,
            source_file=source_file,
            source_path=source_path,
            source_type=source_type,
            file_hash=file_hash,
            pipeline_version=Settings.BRONZE_PIPELINE_VERSION,
        )

        # Escreve Parquet na camada Bronze.
        output_path = self.writer.write(
            df=bronze_df,
            dataset_name=dataset_name,
            snapshot_date=snapshot_date,
            source_type=source_type,
            mode="overwrite"
        )

        return output_path