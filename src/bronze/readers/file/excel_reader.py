from typing import Optional

import pandas as pd

from src.bronze.readers.base_reader import BaseReader
from src.core.data_cleaner import DataCleaner


class ExcelReader(BaseReader):
    """
    Reader responsável por ingestão de arquivos Excel XLSX.

    A Bronze lê Excel com Pandas porque XLSX não é um formato
    naturalmente distribuído para Spark.

    Regra:
    ------
    - não aplicar regra de negócio;
    - preservar valores como texto;
    - aplicar apenas limpeza técnica;
    - retornar Pandas DataFrame.
    """

    def __init__(
        self,
        sheet_name: Optional[str] = None
    ) -> None:
        """
        Inicializa o reader.

        Parameters
        ----------
        sheet_name : Optional[str]
            Nome da aba a ser lida. Se None, lê a primeira aba.
        """
        self.sheet_name = sheet_name

    def read(
        self,
        source_path: str
    ) -> pd.DataFrame:
        """
        Lê arquivo XLSX e retorna Pandas DataFrame normalizado.

        Parameters
        ----------
        source_path : str
            Caminho do arquivo XLSX.

        Returns
        -------
        pd.DataFrame
            DataFrame Pandas limpo tecnicamente.
        """

        df = pd.read_excel(
            source_path,
            sheet_name=0 if self.sheet_name is None else self.sheet_name,
            dtype=str,
            engine="openpyxl"
        )

        df = DataCleaner.remove_empty_rows(df)
        df = DataCleaner.normalize_columns(df)
        df = DataCleaner.fix_duplicate_columns(df)

        return df