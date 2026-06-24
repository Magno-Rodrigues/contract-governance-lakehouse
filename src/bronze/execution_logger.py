from datetime import datetime, timezone
from pathlib import Path
from typing import Optional
import uuid

import pandas as pd

from src.config.settings import Settings


class BronzeExecutionLogger:
    """
    Logger técnico da Bronze Layer.

    Responsabilidades:
    - gerar execution_id único;
    - montar registros de execução por arquivo;
    - carregar histórico de execuções anteriores;
    - verificar idempotência;
    - persistir log acumulado sem apagar histórico.
    """

    @staticmethod
    def generate_execution_id() -> str:
        """
        Gera um identificador único para cada execução batch.
        """
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        short_uuid = str(uuid.uuid4())[:8]

        return f"bronze_{timestamp}_{short_uuid}"

    @staticmethod
    def load_existing_log() -> pd.DataFrame:
        """
        Carrega o histórico de execução já existente.

        Se o arquivo ainda não existir, retorna DataFrame vazio.
        """
        log_path = Settings.BRONZE_EXECUTION_LOG_PATH

        if not log_path.exists():
            return pd.DataFrame()

        return pd.read_csv(log_path)

    @staticmethod
    def was_successfully_processed(
        existing_log_df: pd.DataFrame,
        source_file: str,
        snapshot_date: str,
        file_hash: str,
    ) -> bool:
        """
        Verifica se o mesmo arquivo já foi processado com sucesso.

        Critério de idempotência:
        - mesmo source_file;
        - mesmo snapshot_date;
        - mesmo file_hash;
        - status SUCCESS.
        """
        if existing_log_df.empty:
            return False

        required_columns = {
            "source_file",
            "snapshot_date",
            "file_hash",
            "status",
        }

        if not required_columns.issubset(existing_log_df.columns):
            return False

        matched_df = existing_log_df[
            (existing_log_df["source_file"] == source_file)
            & (existing_log_df["snapshot_date"] == snapshot_date)
            & (existing_log_df["file_hash"] == file_hash)
            & (existing_log_df["status"] == "SUCCESS")
        ]

        return not matched_df.empty

    @staticmethod
    def build_execution_record(
        execution_id: str,
        source_file: str,
        snapshot_date: str,
        source_type: Optional[str],
        dataset_name: Optional[str],
        file_hash: str,
        status: str,
        start_time: datetime,
        end_time: datetime,
        bronze_path: Optional[str] = None,
        error_message: Optional[str] = None,
        retry_count: int = 0,
    ) -> dict:
        """
        Monta um registro padronizado de execução por arquivo.
        """
        duration_seconds = (end_time - start_time).total_seconds()

        return {
            "execution_id": execution_id,
            "source_file": source_file,
            "snapshot_date": snapshot_date,
            "source_type": source_type,
            "dataset_name": dataset_name,
            "file_hash": file_hash,
            "status": status,
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "duration_seconds": duration_seconds,
            "bronze_path": bronze_path,
            "error_message": error_message,
            "retry_count": retry_count,
        }

    @staticmethod
    def append_execution_log(current_run_df: pd.DataFrame) -> None:
        """
        Persiste o log da execução atual acumulando com histórico anterior.

        Importante:
        - não sobrescreve histórico;
        - mantém rastreabilidade entre execuções;
        - permite idempotência baseada em execuções passadas.
        """
        log_path = Settings.BRONZE_EXECUTION_LOG_PATH
        log_path.parent.mkdir(parents=True, exist_ok=True)

        existing_log_df = BronzeExecutionLogger.load_existing_log()

        if existing_log_df.empty:
            final_log_df = current_run_df
        else:
            final_log_df = pd.concat(
                [existing_log_df, current_run_df],
                ignore_index=True,
            )

        final_log_df.to_csv(
            log_path,
            index=False,
            encoding="utf-8",
        )