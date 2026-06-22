from abc import ABC, abstractmethod
import pandas as pd


class BaseReader(ABC):
    """
    Interface base para todos os Readers.

    Responsabilidade:
    -----------------
    Ler a fonte e retornar Pandas DataFrame.

    Readers NÃO conhecem Spark.

    Spark entra apenas na camada de conversão.
    """

    @abstractmethod
    def read(
        self,
        source_path: str
    ) -> pd.DataFrame:
        """
        Lê a fonte e retorna Pandas DataFrame.

        Parameters
        ----------
        source_path : str
            Caminho da fonte de dados.

        Returns
        -------
        pd.DataFrame
            Dados carregados.
        """
        pass