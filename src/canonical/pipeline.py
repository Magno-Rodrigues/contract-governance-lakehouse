"""
Pipeline da camada Canonical.

A Canonical transforma dados da Bronze/origem em datasets padronizados
por conceito de negócio.

Para o NACT, fornecedores diferentes podem entregar layouts diferentes,
mas o resultado deve convergir para o mesmo dataset canônico:
canonical/entity=nact_contracts/
"""

import pandas as pd

from src.config.settings import Settings
from src.core.session import SparkFactory
from src.bronze.converters.pandas_to_spark import PandasToSparkConverter
from src.canonical.nact_transformer import NACTTransformer
from src.canonical.sgc_transformer import SGCTransformer


class CanonicalPipeline:
    """
    Pipeline mínimo da Canonical Layer.

    Responsabilidade:
    - ler arquivo NACT;
    - detectar layout;
    - aplicar transformer correto;
    - converter para Spark;
    - salvar Parquet canônico.
    """

    def __init__(self) -> None:
        self.spark = SparkFactory.create()

    def _detect_nact_layout(
        self,
        source_path: str,
    ) -> str:
        """
        Detecta layout NACT a partir da extensão e estrutura do arquivo.

        Regra atual:
        - .xlsb com aba RACT representa layout EY;
        - .xlsx tabular com coluna 'Número de contrato' representa Deloitte.
        """

        normalized_path = source_path.lower()

        if normalized_path.endswith(".xlsb"):
            return "ey_ract_v1"

        if normalized_path.endswith(".xlsx"):
            sample_df = pd.read_excel(
                source_path,
                sheet_name=0,
                header=None,
                dtype=str,
                nrows=5,
            )

            first_row_values = set(
                sample_df.iloc[0].dropna().astype(str).tolist()
            )

            if "Número de contrato" in first_row_values:
                return "deloitte_contracts_v1"

        raise ValueError(
            f"Layout NACT não reconhecido para arquivo: {source_path}"
        )

    def run_nact_contracts(
        self,
        source_path: str,
        snapshot_date: str,
    ) -> str:
        """
        Processa arquivo NACT para o dataset canonical_nact_contracts.

        Este método é independente de fornecedor.
        Ele detecta o layout e chama o transformer adequado.
        """

        layout = self._detect_nact_layout(
            source_path=source_path,
        )

        if layout == "ey_ract_v1":
            raw_df = pd.read_excel(
                source_path,
                sheet_name="RACT",
                engine="pyxlsb",
                header=None,
                dtype=str,
            )

            canonical_df = NACTTransformer.transform_ey_ract(
                raw_df=raw_df,
                snapshot_date=snapshot_date,
            )

        elif layout == "deloitte_contracts_v1":
            raw_df = pd.read_excel(
                source_path,
                sheet_name=0,
                header=None,
                dtype=str,
            )

            canonical_df = NACTTransformer.transform_deloitte_contracts(
                raw_df=raw_df,
                snapshot_date=snapshot_date,
            )

        else:
            raise ValueError(
                f"Layout NACT não suportado: {layout}"
            )

        spark_df = PandasToSparkConverter.convert(
            spark=self.spark,
            pandas_df=canonical_df,
        )

        output_path = (
            f"s3a://{Settings.BUCKET_NAME}/canonical/"
            f"entity=nact_contracts/"
            f"snapshot_date={snapshot_date}/"
        )

        spark_df.write.mode("overwrite").parquet(output_path)

        return output_path
        
    def run_sgc_contracts(
        self,
        source_path: str,
        snapshot_date: str,
    ) -> str:
        """
        Processa o AnaliticoProjeto.csv para o dataset canonical_sgc_contracts.

        O Analítico do SGC representa a visão executiva da carteira de contratos
        de uma gerência. Ele será a base principal para cruzamentos futuros com
        NACT, medições, RDO, QEC, subcontratadas e irregularidades.
        """

        raw_df = pd.read_csv(
            source_path,
            sep=";",
            dtype=str,
        )

        canonical_df = SGCTransformer.transform_analitico_projeto(
            raw_df=raw_df,
            snapshot_date=snapshot_date,
        )

        spark_df = PandasToSparkConverter.convert(
            spark=self.spark,
            pandas_df=canonical_df,
        )

        output_path = (
            f"s3a://{Settings.BUCKET_NAME}/canonical/"
            f"entity=sgc_contracts/"
            f"snapshot_date={snapshot_date}/"
        )

        spark_df.write.mode("overwrite").parquet(output_path)
        return output_path