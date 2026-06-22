import re
import unicodedata
from typing import List

import pandas as pd


class DataCleaner:
    """
    Classe utilitária responsável por limpeza técnica de DataFrames.

    Importante:
    ----------
    Esta classe NÃO aplica regra de negócio.

    Apenas normalização técnica necessária
    para ingestão segura na Bronze Layer.
    """

    @staticmethod
    def normalize_column_name(column_name: str) -> str:
        """
        Normaliza nome de coluna.

        Exemplo:

            Número Contrato
                ↓

            numero_contrato
        """

        # Remove acentos.
        normalized = unicodedata.normalize(
            "NFKD",
            column_name
        ).encode(
            "ASCII",
            "ignore"
        ).decode(
            "utf-8"
        )

        # Lowercase.
        normalized = normalized.lower()

        # Espaços viram underscore.
        normalized = normalized.replace(" ", "_")

        # Substitui qualquer sequência de caracteres não alfanuméricos por underscore.
        normalized = re.sub(
            r"[^a-zA-Z0-9]+",
            "_",
            normalized
        )

        # Remove underscores duplicados.
        normalized = re.sub(
            r"_+",
            "_",
            normalized
        )

        # Remove underscores no início e no fim.
        normalized = normalized.strip("_")

        return normalized

    @classmethod
    def normalize_columns(
        cls,
        df: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Normaliza todos os nomes das colunas.
        """

        df.columns = [
            cls.normalize_column_name(col)
            for col in df.columns
        ]

        return df

    @staticmethod
    def remove_empty_rows(
        df: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Remove linhas completamente vazias.
        """

        return df.dropna(how="all")

    @staticmethod
    def fix_duplicate_columns(
        df: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Renomeia colunas duplicadas.

        Exemplo:

            valor
            valor

        vira:

            valor
            valor_1
        """

        columns = pd.Series(df.columns)

        for duplicated in columns[
            columns.duplicated()
        ].unique():

            duplicated_indexes = columns[
                columns == duplicated
            ].index.tolist()

            for i, index in enumerate(
                duplicated_indexes
            ):
                if i == 0:
                    continue

                columns[index] = f"{duplicated}_{i}"

        df.columns = columns

        return df