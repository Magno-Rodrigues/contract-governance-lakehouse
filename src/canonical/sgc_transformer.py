"""
Transformer canônico do SGC.

Objetivo
--------
Padronizar datasets extraídos do SGC para entidades canônicas.

Nesta primeira versão, transformamos o AnaliticoProjeto.csv em:
canonical/entity=sgc_contracts/

O Analítico é a melhor base inicial porque representa a visão executiva
da carteira de contratos de uma gerência.
"""

import pandas as pd

from src.core.normalization import normalize_contract_number


class SGCTransformer:
    """
    Padroniza arquivos do SGC em entidades canônicas.

    A Bronze preserva os dados como vieram.
    A Canonical seleciona e renomeia campos relevantes para integração,
    indicadores e cruzamentos futuros.
    """

    @staticmethod
    def transform_analitico_projeto(
        raw_df: pd.DataFrame,
        snapshot_date: str,
    ) -> pd.DataFrame:
        """
        Transforma AnaliticoProjeto.csv em canonical_sgc_contracts.

        O objetivo é criar a entidade base de contratos da carteira,
        usando contract_number como chave comum com NACT, QEC, medições,
        subcontratadas, pendências e irregularidades.
        """
        raw_df = SGCTransformer._normalize_columns(raw_df)
        
        canonical_df = pd.DataFrame()

        canonical_df["contract_number_raw"] = raw_df["contrato"]
        canonical_df["contract_number"] = canonical_df[
            "contract_number_raw"
        ].apply(
            normalize_contract_number
        )

        canonical_df["supplier_name"] = raw_df.get("fornecedor")
        canonical_df["contract_description"] = raw_df.get("objeto_contratual")
        canonical_df["project_area"] = raw_df.get("projeto_area_de_operacao_vale")

        canonical_df["currency"] = raw_df.get("moeda")
        canonical_df["total_value"] = raw_df.get("valor_total")
        canonical_df["po_value"] = raw_df.get("po")
        canonical_df["total_tacs"] = raw_df.get("total_tacs")
        canonical_df["total_claims"] = raw_df.get("total_pleitos")
        canonical_df["total_adjustments"] = raw_df.get("total_reajustes")
        canonical_df["total_advance"] = raw_df.get("total_adiantamento")
        canonical_df["measured_value"] = raw_df.get("valor_medicoes")
        canonical_df["remaining_to_measure"] = raw_df.get("saldo_a_medir")
        canonical_df["contractual_block"] = raw_df.get("bloqueio_contratual")
        canonical_df["remaining_to_pay"] = raw_df.get("saldo_a_pagar")
        canonical_df["remaining_percentage"] = raw_df.get("saldo")

        canonical_df["start_date"] = raw_df.get("prazo_inicio")
        canonical_df["end_date"] = raw_df.get("prazo_fim")
        canonical_df["remaining_days"] = raw_df.get("saldo_em_dias")

        canonical_df["manager_name"] = raw_df.get("gestor")
        canonical_df["administrator_name"] = raw_df.get("administrador")
        canonical_df["inspector_name"] = raw_df.get("fiscal")
        canonical_df["measurement_inspector_name"] = raw_df.get("tecnico_de_medicao")

        canonical_df["source_system"] = "SGC"
        canonical_df["source_dataset"] = "analitico_projeto"
        canonical_df["canonical_entity"] = "sgc_contracts"
        canonical_df["snapshot_date"] = snapshot_date
        canonical_df["processed_at"] = pd.Timestamp.utcnow().isoformat()

        canonical_df = canonical_df.dropna(
            subset=["contract_number"]
        )

        return canonical_df
    
    @staticmethod
    def _normalize_columns(
        df: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Normaliza nomes de colunas do SGC para padrão técnico.

        Exemplo:
        'DESCRIÇÃO DO CONTRATO' -> 'descricao_do_contrato'
        'PROJETO/ÁREA DE OPERAÇÃO VALE' -> 'projeto_area_de_operacao_vale'
        """

        normalized_df = df.copy()

        normalized_df.columns = (
            normalized_df.columns
            .str.strip()
            .str.lower()
            .str.normalize("NFKD")
            .str.encode("ascii", errors="ignore")
            .str.decode("utf-8")
            .str.replace("/", "_", regex=False)
            .str.replace("%", "percentual", regex=False)
            .str.replace(" ", "_", regex=False)
            .str.replace(".", "", regex=False)
        )

        return normalized_df