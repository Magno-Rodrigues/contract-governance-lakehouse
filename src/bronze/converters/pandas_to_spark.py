import pandas as pd
from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.types import StructType, StructField, StringType


class PandasToSparkConverter:
    """
    Converte Pandas DataFrames em Spark DataFrames.

    Regra Bronze:
    --------------
    A Bronze preserva dados como texto bruto.
    A tipagem semântica será aplicada na Silver.
    """

    @staticmethod
    def convert(
        spark: SparkSession,
        pandas_df: pd.DataFrame
    ) -> DataFrame:
        """
        Converte Pandas DataFrame para Spark DataFrame com schema explícito.

        Estratégia:
        -----------
        - cria schema Spark com todas as colunas como StringType;
        - substitui valores nulos por None;
        - converte valores não nulos para string Python nativa;
        - evita inferência automática do Spark.
        """

        if pandas_df.empty:
            raise ValueError(
                "Não é possível converter DataFrame vazio."
            )

        safe_df = pandas_df.copy()

        # Substitui NaN/NaT/pd.NA por None.
        safe_df = safe_df.where(
            pd.notnull(safe_df),
            None
        )

        # Converte cada valor não nulo para string nativa.
        safe_df = safe_df.applymap(
            lambda value: str(value) if value is not None else None
        )

        # Schema explícito: Bronze armazena tudo como string.
        schema = StructType([
            StructField(
                column_name,
                StringType(),
                True
            )
            for column_name in safe_df.columns
        ])

        return spark.createDataFrame(
            safe_df,
            schema=schema
        )