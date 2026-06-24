from datetime import datetime, timezone
from typing import Optional, List, Dict, Any

import pandas as pd

from src.config.settings import Settings


class BronzeQualityLogger:
    """
    Logger técnico de qualidade da Bronze Layer.

    Registra anomalias técnicas toleradas durante a ingestão,
    como linhas inválidas em CSV, layout inesperado ou leitura parcial.

    Este logger não aplica regra de negócio.
    Ele existe para auditoria operacional da ingestão.
    """

    @staticmethod
    def build_record(
        source_file: str,
        snapshot_date: str,
        issue_type: str,
        issue_description: str,
        source_path: Optional[str] = None,
        line_number: Optional[int] = None,
        severity: str = "WARNING",
    ) -> Dict[str, Any]:
        """
        Cria um registro padronizado de qualidade técnica.
        """
        return {
            "logged_at": datetime.now(timezone.utc).isoformat(),
            "source_file": source_file,
            "snapshot_date": snapshot_date,
            "source_path": source_path,
            "issue_type": issue_type,
            "issue_description": issue_description,
            "line_number": line_number,
            "severity": severity,
        }

    @staticmethod
    def append_quality_log(records: List[Dict[str, Any]]) -> None:
        """
        Persiste registros de qualidade acumulando histórico.
        """
        if not records:
            return

        current_df = pd.DataFrame(records)

        log_path = Settings.BRONZE_QUALITY_LOG_PATH
        log_path.parent.mkdir(parents=True, exist_ok=True)

        if log_path.exists():
            existing_df = pd.read_csv(log_path)
            final_df = pd.concat(
                [existing_df, current_df],
                ignore_index=True,
            )
        else:
            final_df = current_df

        final_df.to_csv(
            log_path,
            index=False,
            encoding="utf-8",
        )