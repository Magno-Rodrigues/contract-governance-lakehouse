"""
Transformer canônico do NACT.

Objetivo
--------
Transformar o NACT bruto da Bronze em um dataset canônico,
independente do layout original do fornecedor.

Nesta primeira versão, suportamos o layout atual da EY.

Regra central
-------------
O campo contract_number é a chave de integração entre NACT e SGC.
"""

from typing import Optional

import pandas as pd

from src.core.normalization import normalize_contract_number


class NACTTransformer:
    """
    Transformer responsável por padronizar o NACT.

    A Bronze preserva o arquivo bruto.
    A Canonical interpreta o layout e cria um schema técnico comum.
    """

    HEADER_MARKER = "ID Contrato"

    @staticmethod
    def _find_header_row(df: pd.DataFrame) -> int:
        """
        Localiza a linha onde começa o cabeçalho real do NACT.

        No layout EY, a tabela útil começa na linha que contém
        o texto 'ID Contrato' em alguma coluna.
        """

        for index, row in df.iterrows():
            row_values = row.astype(str).tolist()

            if any(value.strip() == NACTTransformer.HEADER_MARKER for value in row_values):
                return index

        raise ValueError(
            "Não foi possível localizar a linha de cabeçalho do NACT."
        )

    @staticmethod
    def transform_ey_ract(
        raw_df: pd.DataFrame,
        snapshot_date: str,
    ) -> pd.DataFrame:
        """
        Transforma a aba RACT do layout EY em dataset canônico.

        Retorno mínimo:
        - contract_number
        - contract_number_raw
        - supplier_cnpj
        - supplier_name
        - business_unit
        """

        header_row = NACTTransformer._find_header_row(raw_df)

        data_df = raw_df.iloc[header_row:].copy()

        data_df.columns = data_df.iloc[0]
        data_df = data_df.iloc[1:].reset_index(drop=True)

        
        canonical_df = pd.DataFrame()

        canonical_df["nact_internal_id"] = data_df["ID Contrato"]

        canonical_df["contract_number_raw"] = data_df["Contrato"]

        canonical_df["contract_number"] = canonical_df[
            "contract_number_raw"
        ].apply(
            normalize_contract_number
        )

        canonical_df["supplier_cnpj"] = data_df["CNPJ"]

        canonical_df["supplier_name"] = data_df["Razão Social"]

        canonical_df["operation_location"] = data_df["Unidade"]

        canonical_df["source_vendor"] = "EY"
        canonical_df["source_layout"] = "ey_ract_v1"
        canonical_df["canonical_entity"] = "nact_contracts"
        canonical_df["snapshot_date"] = snapshot_date
        canonical_df["processed_at"] = pd.Timestamp.utcnow().isoformat()

        canonical_df = canonical_df.dropna(
            subset=["contract_number"]
        )

        return canonical_df