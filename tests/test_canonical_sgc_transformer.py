"""
Testes do transformer canônico do SGC.

Estes testes protegem a criação da entidade base de contratos do SGC:
canonical_sgc_contracts.
"""

import pandas as pd

from src.canonical.sgc_transformer import SGCTransformer


def test_transform_analitico_projeto_normalizes_contract_number():
    """
    Valida transformação mínima do AnaliticoProjeto.

    O contrato deve ser normalizado para contract_number,
    que será a chave de integração com NACT e demais fontes.
    """

    raw_df = pd.DataFrame(
        [
            {
                "contrato": "5900055119",
                "fornecedor": "Fornecedor SGC A",
                "objeto_contratual": "Serviço de engenharia",
                "projeto_area_de_operacao_vale": "Vitória",
                "moeda": "BRL",
                "valor_total": "1000000",
                "saldo_a_medir": "250000",
            }
        ]
    )

    result = SGCTransformer.transform_analitico_projeto(
        raw_df=raw_df,
        snapshot_date="2024-07-13_0800",
    )

    assert result.iloc[0]["contract_number"] == "5900055119"
    assert result.iloc[0]["supplier_name"] == "Fornecedor SGC A"
    assert result.iloc[0]["contract_description"] == "Serviço de engenharia"
    assert result.iloc[0]["source_system"] == "SGC"
    assert result.iloc[0]["canonical_entity"] == "sgc_contracts"
    assert result.iloc[0]["snapshot_date"] == "2024-07-13_0800"