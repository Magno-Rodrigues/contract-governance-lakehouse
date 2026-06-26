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

def test_transform_deloitte_contracts_normalizes_contract_number():
    """
    Valida transformação mínima do layout Deloitte.

    O layout Deloitte já vem tabular desde a primeira linha.
    A Canonical deve mapear 'Número de contrato' para contract_number
    e preservar os campos úteis para indicadores.
    """

    raw_df = pd.DataFrame(
        [
            [
                "Status do contrato",
                "Localidade",
                "Número de contrato",
                "Razão Social",
                "CNPJ",
                "Papel",
                "Competência",
                "Nota",
                "Pendências Atuais/Anteriores",
            ],
            [
                "Vigente",
                "VITÓRIA",
                "5900101005",
                "Fornecedor Deloitte A",
                "27.126.997/0001-87",
                "CONTRATADA",
                "Outubro/2023",
                "56%",
                "10 / 6",
            ],
        ]
    )

    result = NACTTransformer.transform_deloitte_contracts(
        raw_df=raw_df,
        snapshot_date="2024-02-01_0800",
    )

    assert result.iloc[0]["contract_number_raw"] == "5900101005"
    assert result.iloc[0]["contract_number"] == "5900101005"
    assert result.iloc[0]["supplier_name"] == "Fornecedor Deloitte A"
    assert result.iloc[0]["operation_location"] == "VITÓRIA"
    assert result.iloc[0]["supplier_role"] == "CONTRATADA"
    assert result.iloc[0]["competence"] == "Outubro/2023"
    assert result.iloc[0]["compliance_score"] == "56%"
    assert result.iloc[0]["pending_issues_summary"] == "10 / 6"
    assert result.iloc[0]["source_vendor"] == "Deloitte"
    assert result.iloc[0]["source_layout"] == "deloitte_contracts_v1"
    assert result.iloc[0]["canonical_entity"] == "nact_contracts"