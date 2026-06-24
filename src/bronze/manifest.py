from datetime import datetime, timezone
from typing import Dict, Any, List

import pandas as pd

from src.config.settings import Settings



class BronzeProcessedManifest:
    """
    Manifest operacional da Bronze Layer.

    Diferença importante:
    ---------------------
    execution_log registra histórico completo de execuções.

    processed_manifest registra o estado atual dos arquivos já processados
    com sucesso.

    A idempotência deve consultar o manifest, não o execution_log.
    """

    @staticmethod
    def load() -> pd.DataFrame:
        """
        Carrega o manifest atual.

        Se ainda não existir, retorna DataFrame vazio.
        """
        manifest_path = Settings.BRONZE_PROCESSED_MANIFEST_PATH

        if not manifest_path.exists():
            return pd.DataFrame()

        return pd.read_csv(manifest_path)

    @staticmethod
    def was_processed(
        manifest_df: pd.DataFrame,
        source_file: str,
        snapshot_date: str,
        file_hash: str,
    ) -> bool:
        """
        Verifica se um arquivo já foi processado com sucesso.

        Critério:
        - mesmo source_file;
        - mesmo snapshot_date;
        - mesmo file_hash.
        """
        if manifest_df.empty:
            return False

        required_columns = {
            "source_file",
            "snapshot_date",
            "file_hash",
        }

        if not required_columns.issubset(manifest_df.columns):
            return False

        matched_df = manifest_df[
            (manifest_df["source_file"] == source_file)
            & (manifest_df["snapshot_date"] == snapshot_date)
            & (manifest_df["file_hash"] == file_hash)
        ]

        return not matched_df.empty

    @staticmethod
    def build_record(
        source_file: str,
        snapshot_date: str,
        source_type: str,
        dataset_name: str,
        file_hash: str,
        bronze_path: str,
        pipeline_version: str,
    ) -> Dict[str, Any]:
        """
        Cria registro de arquivo processado com sucesso.
        """
        return {
            "source_file": source_file,
            "snapshot_date": snapshot_date,
            "source_type": source_type,
            "dataset_name": dataset_name,
            "file_hash": file_hash,
            "bronze_path": bronze_path,
            "pipeline_version": pipeline_version,
            "processed_at": datetime.now(timezone.utc).isoformat(),
        }

    @staticmethod
    def upsert(records: List[Dict[str, Any]]) -> None:
        """
        Atualiza o manifest com registros processados com sucesso.

        Regra:
        ------
        Para o mesmo source_file + snapshot_date + file_hash,
        mantém apenas um registro.

        Isso impede crescimento desnecessário do manifest e mantém o arquivo
        como representação do estado atual da Bronze.
        """
        if not records:
            return

        current_df = pd.DataFrame(records)

        manifest_path = Settings.BRONZE_PROCESSED_MANIFEST_PATH
        manifest_path.parent.mkdir(parents=True, exist_ok=True)

        existing_df = BronzeProcessedManifest.load()

        if existing_df.empty:
            final_df = current_df
        else:
            final_df = pd.concat(
                [existing_df, current_df],
                ignore_index=True,
            )

            final_df = final_df.drop_duplicates(
                subset=[
                    "source_file",
                    "snapshot_date",
                    "file_hash",
                ],
                keep="last",
            )

        final_df.to_csv(
            manifest_path,
            index=False,
            encoding="utf-8",
        )