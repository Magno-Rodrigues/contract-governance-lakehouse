from datetime import datetime, timezone
import uuid


class BronzeExecutionLogger:
    """
    Responsável por gerar metadados de execução
    do pipeline Bronze.
    """

    @staticmethod
    def generate_execution_id() -> str:
        """
        Gera identificador único da execução.
        """

        timestamp = datetime.now(
            timezone.utc
        ).strftime(
            "%Y%m%d_%H%M%S"
        )

        short_uuid = str(
            uuid.uuid4()
        )[:8]

        return f"bronze_{timestamp}_{short_uuid}"

    @staticmethod
    def build_execution_record(
        execution_id: str,
        source_file: str,
        dataset_name: str,
        bronze_status: str,
        start_time: datetime,
        end_time: datetime,
        error_message: str = None
    ) -> dict:
        """
        Cria registro técnico de execução.
        """

        duration_seconds = (
            end_time - start_time
        ).total_seconds()

        return {
            "execution_id": execution_id,
            "source_file": source_file,
            "dataset_name": dataset_name,
            "status": bronze_status,
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "duration_seconds": duration_seconds,
            "error_message": error_message
        }