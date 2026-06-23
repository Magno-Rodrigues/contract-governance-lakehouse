import pandas as pd

from src.bronze.readers.base_reader import BaseReader
from src.core.data_cleaner import DataCleaner


class XLSBReader(BaseReader):
    """
    Reader responsável por ingestão de arquivos XLSB.

    Este reader é schema-agnostic: não assume nomes de colunas,
    abas, layout ou fornecedor. Isso é importante para fontes como
    NACT, cujo layout pode mudar conforme a terceirizada.
    """

    def read(self, source_path: str) -> pd.DataFrame:
        """
        Lê arquivo XLSB e retorna Pandas DataFrame normalizado tecnicamente.
        """

        df = pd.read_excel(
            source_path,
            engine="pyxlsb",
            dtype=str,
        )

        df = DataCleaner.remove_empty_rows(df)
        df = DataCleaner.fix_duplicate_columns(df)
        df = DataCleaner.normalize_columns(df)

        return df