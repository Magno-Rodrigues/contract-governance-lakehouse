"""
Transformer canônico do NACT.

Objetivo
--------
Transformar relatórios NACT, vindos de fornecedores diferentes, em um
schema canônico único.

A Bronze preserva o arquivo bruto.
A Canonical interpreta o layout e padroniza os campos relevantes.

Regra central
-------------
contract_number é a chave de integração entre NACT e SGC.
"""

import pandas as pd

from src.core.normalization import normalize_contract_number


class NACTTransformer:
    """
    Padroniza relatórios NACT para o dataset canônico nact_contracts.

    Atualmente suporta:
    - EY RACT
    - Deloitte Monitoramento Mensal Consolidado
    """

    HEADER_MARKER = "ID Contrato"

    @staticmethod
    def _find_header_row(df: pd.DataFrame) -> int:
        """
        Localiza a linha de cabeçalho real em layouts semiestruturados.

        No layout EY, o arquivo possui linhas institucionais antes da tabela.
        A tabela útil começa na linha que contém 'ID Contrato'.
        """

        for index, row in df.iterrows():
            row_values = row.astype(str).tolist()

            if any(value.strip() == NACTTransformer.HEADER_MARKER for value in row_values):
                return index

        raise ValueError(
            "Não foi possível localizar a linha de cabeçalho do NACT."
        )

    @staticmethod
    def _add_common_metadata(
        canonical_df: pd.DataFrame,
        source_vendor: str,
        source_layout: str,
        snapshot_date: str,
    ) -> pd.DataFrame:
        """
        Adiciona metadados comuns do dataset canônico.

        Esses campos permitem rastrear origem, layout e data de processamento,
        independentemente do fornecedor do relatório.
        """

        canonical_df["source_vendor"] = source_vendor
        canonical_df["source_layout"] = source_layout
        canonical_df["canonical_entity"] = "nact_contracts"
        canonical_df["snapshot_date"] = snapshot_date
        canonical_df["processed_at"] = pd.Timestamp.utcnow().isoformat()

        return canonical_df

    @staticmethod
    def transform_ey_ract(
        raw_df: pd.DataFrame,
        snapshot_date: str,
    ) -> pd.DataFrame:
        """
        Transforma a aba RACT do layout EY em nact_contracts.

        O layout EY é semiestruturado:
        - possui linhas de título/metadados antes da tabela;
        - exige detecção da linha de cabeçalho;
        - usa 'Contrato' como campo bruto do contrato.
        """

        header_row = NACTTransformer._find_header_row(raw_df)

        data_df = raw_df.iloc[header_row:].copy()
        data_df.columns = data_df.iloc[0]
        data_df = data_df.iloc[1:].reset_index(drop=True)

        canonical_df = pd.DataFrame()

        canonical_df["nact_internal_id"] = data_df["ID Contrato"]
        canonical_df["contract_number_raw"] = data_df["Contrato"]
        canonical_df["contract_number"] = canonical_df["contract_number_raw"].apply(
            normalize_contract_number
        )
        canonical_df["supplier_cnpj"] = data_df["CNPJ"]
        canonical_df["supplier_name"] = data_df["Razão Social"]
        canonical_df["operation_location"] = data_df["Unidade"]

        # Campos já disponíveis no layout Deloitte, mas ainda não extraídos
        # do layout EY nesta primeira versão.
        #
        # Mantê-los no schema garante que todos os fornecedores gerem
        # o mesmo dataset canônico: nact_contracts.
        canonical_df["supplier_role"] = None
        canonical_df["competence"] = None
        canonical_df["compliance_score"] = None
        canonical_df["pending_issues_summary"] = None

        canonical_df = NACTTransformer._add_common_metadata(
            canonical_df=canonical_df,
            source_vendor="EY",
            source_layout="ey_ract_v1",
            snapshot_date=snapshot_date,
        )

        canonical_df = canonical_df.dropna(subset=["contract_number"])

        return canonical_df

    @staticmethod
    def transform_deloitte_contracts(
        raw_df: pd.DataFrame,
        snapshot_date: str,
    ) -> pd.DataFrame:
        """
        Transforma o layout Deloitte em nact_contracts.

        O layout Deloitte já vem tabular desde a primeira linha.
        A Canonical seleciona campos úteis para integração e indicadores,
        sem replicar todas as colunas do relatório original.
        """

        data_df = raw_df.copy()
        data_df.columns = data_df.iloc[0]
        data_df = data_df.iloc[1:].reset_index(drop=True)

        canonical_df = pd.DataFrame()

        canonical_df["nact_internal_id"] = None
        canonical_df["contract_number_raw"] = data_df["Número de contrato"]
        canonical_df["contract_number"] = canonical_df["contract_number_raw"].apply(
            normalize_contract_number
        )
        canonical_df["supplier_cnpj"] = data_df["CNPJ"]
        canonical_df["supplier_name"] = data_df["Razão Social"]
        canonical_df["operation_location"] = data_df["Localidade"]
        canonical_df["supplier_role"] = data_df["Papel"]
        canonical_df["competence"] = data_df["Competência"]
        canonical_df["compliance_score"] = data_df["Nota"]
        canonical_df["pending_issues_summary"] = data_df[
            "Pendências Atuais/Anteriores"
        ]

        canonical_df = NACTTransformer._add_common_metadata(
            canonical_df=canonical_df,
            source_vendor="Deloitte",
            source_layout="deloitte_contracts_v1",
            snapshot_date=snapshot_date,
        )

        canonical_df = canonical_df.dropna(subset=["contract_number"])

        return canonical_df