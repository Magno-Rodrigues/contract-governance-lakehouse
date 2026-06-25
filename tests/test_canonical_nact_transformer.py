"""
Testes do transformer canônico do NACT.

Estes testes protegem a regra mais importante da Canonical:
transformar o layout bruto do fornecedor em um schema comum
baseado em contract_number.
"""

import pandas as pd

from src.canonical.nact_transformer import NACTTransformer


def test_transform_ey_ract_normalizes_contract_number():
    """
    Valida transformação mínima do layout EY.

    O contrato bruto vem com prefixo VALE.
    A Canonical deve preservar o valor bruto e criar contract_number
    somente com os dígitos.
    """

    raw_df = pd.DataFrame(
        [
            ["Título", None, None, None, None],
            ["Competência:", "2023-01", None, None, None],
            ["ID Contrato", "Contrato", "CNPJ", "Razão Social", "Unidade"],
            ["1", "VALE5900052656", "12345678000199", "Fornecedor A", "ES"],
        ]
    )

    result = NACTTransformer.transform_ey_ract(
    raw_df=raw_df,
    snapshot_date="2026-06-06_0800",
)

    assert result.iloc[0]["contract_number_raw"] == "VALE5900052656"
    assert result.iloc[0]["contract_number"] == "5900052656"
    assert result.iloc[0]["supplier_cnpj"] == "12345678000199"
    
    assert result.iloc[0]["source_vendor"] == "EY"
    assert result.iloc[0]["source_layout"] == "ey_ract_v1"
    assert result.iloc[0]["canonical_entity"] == "nact_contracts"
    
    assert result.iloc[0]["nact_internal_id"] == "1"
    assert result.iloc[0]["operation_location"] == "ES"
    assert result.iloc[0]["snapshot_date"] == "2026-06-06_0800"
    assert "processed_at" in result.columns