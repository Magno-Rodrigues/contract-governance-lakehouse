from typing import List

import pandas as pd

from src.bronze.readers.base_reader import BaseReader
from src.core.data_cleaner import DataCleaner


class CSVReader(BaseReader):
    """
    Reader responsável por ingestão resiliente de arquivos CSV.

    Estratégia:
    ----------
    - tenta múltiplos encodings;
    - detecta separador automaticamente;
    - preserva todos os valores como string;
    - aplica limpeza técnica para Bronze.
    """

    ENCODING_FALLBACKS: List[str] = [
        "utf-8-sig",
        "utf-8",
        "latin1",
        "ISO-8859-1",
        "cp1252",
    ]

    def read(self, source_path: str) -> pd.DataFrame:
        """
        Lê arquivo CSV com fallback de encoding e separador flexível.
        """

        last_error = None

        for encoding in self.ENCODING_FALLBACKS:
            try:
                df = pd.read_csv(
                    source_path,
                    encoding=encoding,
                    dtype=str,
                    sep=None,
                    engine="python",
                )
                break

            except Exception as error:
                last_error = error
                continue

        else:
            raise ValueError(
                f"Falha ao ler CSV: {source_path}. "
                f"Último erro: {last_error}"
            )

        df = DataCleaner.remove_empty_rows(df)
        df = DataCleaner.fix_duplicate_columns(df)
        df = DataCleaner.normalize_columns(df)

        return df