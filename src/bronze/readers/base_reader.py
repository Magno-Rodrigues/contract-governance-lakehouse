from abc import ABC, abstractmethod
from pyspark.sql import SparkSession, DataFrame


class BaseReader(ABC):
    """
    Classe abstrata base para todos os readers da Bronze Layer.

    Objetivo:
    --------
    Garantir que qualquer fonte de dados implementada
    siga a mesma interface de leitura.

    Isso permite que o pipeline Bronze seja desacoplado
    do tipo específico da fonte.

    Exemplos de implementações futuras:
        - CSVReader
        - ExcelReader
        - XLSBReader
        - APIReader
        - SAPReader
        - PostgresReader
        - SFTPReader
    """

    @abstractmethod
    def read(
        self,
        spark: SparkSession,
        source_path: str
    ) -> DataFrame:
        """
        Método obrigatório que cada reader deve implementar.

        Parameters
        ----------
        spark : SparkSession
            Sessão Spark ativa.

        source_path : str
            Caminho da origem de dados.

        Returns
        -------
        DataFrame
            Spark DataFrame contendo os dados lidos.
        """
        pass