"""
Pipeline da camada Canonical.

A Canonical transforma dados brutos da Bronze/arquivos origem em datasets
padronizados por conceito de negócio.

Nesta primeira versão, suportamos o NACT EY RACT gerando:
canonical/entity=nact_contracts/
"""

import pandas as pd

from src.config.settings import Settings
from src.core.session import SparkFactory
from src.bronze.converters.pandas_to_spark import PandasToSparkConverter
from src.canonical.nact_transformer import NACTTransformer


class CanonicalPipeline:
    """
    Pipeline mínimo da Canonical Layer.

    Mantemos esta classe simples: ela orquestra leitura, transformação,
    conversão para Spark e escrita em Parquet.
    """

    def __init__(self) -> None:
        self.spark = SparkFactory.create()

    def run_nact_ey_contracts(
        self,
        source_path: str,
        snapshot_date: str,
    ) -> str:
        """
        Processa NACT EY RACT para o dataset canonical_nact_contracts.
        """

        raw_df = pd.read_excel(
            source_path,
            sheet_name="RACT",
            engine="pyxlsb",
            header=None,
            dtype=str,
        )

        canonical_df = NACTTransformer.transform_ey_ract(
            raw_df=raw_df,
            snapshot_date=snapshot_date,
        )

        spark_df = PandasToSparkConverter.convert(
            spark=self.spark,
            pandas_df=canonical_df,
        )

        output_path = (
            f"s3a://{Settings.BUCKET_NAME}/canonical/"
            f"entity=nact_contracts/"
            f"snapshot_date={snapshot_date}/"
        )

        spark_df.write.mode("overwrite").parquet(output_path)

        return output_path