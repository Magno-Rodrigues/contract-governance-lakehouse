from datetime import datetime, timezone
import pandas as pd

from src.config.settings import Settings
from src.bronze.catalog import BronzeCatalog
from src.bronze.pipeline import BronzePipeline
from src.bronze.execution_logger import BronzeExecutionLogger


def run_bronze_batch() -> pd.DataFrame:
    """
    Executa ingestão Bronze em lote usando landing_metadata.csv.

    A função:
    - lê metadados da Landing;
    - gera execution_id único para o batch;
    - identifica source_type;
    - resolve dataset_name;
    - executa BronzePipeline para cada arquivo;
    - registra sucesso/falha por arquivo.
    """

    landing_metadata_df = pd.read_csv(Settings.LANDING_METADATA_PATH)

    pipeline = BronzePipeline()
    execution_id = BronzeExecutionLogger.generate_execution_id()

    results = []

    for _, row in landing_metadata_df.iterrows():
        start_time = datetime.now(timezone.utc)

        source_file = row["source_file"]
        snapshot_date = row["snapshot_date"]

        try:
            source_type = BronzeCatalog.get_source_type(source_file=source_file)
            dataset_name = BronzeCatalog.get_dataset_name(source_file=source_file)

            output_path = pipeline.run(
                source_path=row["source_path"],
                source_type=source_type,
                dataset_name=dataset_name,
                snapshot_date=snapshot_date,
                source_file=source_file,
                file_hash=row["file_hash"],
            )

            end_time = datetime.now(timezone.utc)

            execution_record = BronzeExecutionLogger.build_execution_record(
                execution_id=execution_id,
                source_file=source_file,
                dataset_name=dataset_name,
                bronze_status="SUCCESS",
                start_time=start_time,
                end_time=end_time,
                error_message=None,
            )

            execution_record.update(
                {
                    "snapshot_date": snapshot_date,
                    "source_type": source_type,
                    "bronze_path": output_path,
                }
            )

            results.append(execution_record)

        except Exception as error:
            end_time = datetime.now(timezone.utc)

            execution_record = BronzeExecutionLogger.build_execution_record(
                execution_id=execution_id,
                source_file=source_file,
                dataset_name=None,
                bronze_status="FAILED",
                start_time=start_time,
                end_time=end_time,
                error_message=str(error),
            )

            execution_record.update(
                {
                    "snapshot_date": snapshot_date,
                    "source_type": None,
                    "bronze_path": None,
                }
            )

            results.append(execution_record)

        # Converte lista de resultados em DataFrame final.
        result_df = pd.DataFrame(results)

        # Garante existência da pasta data/.
        Settings.BRONZE_EXECUTION_LOG_PATH.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        # Persiste log local de execução.
        result_df.to_csv(
            Settings.BRONZE_EXECUTION_LOG_PATH,
            index=False,
            encoding="utf-8",
        )

        return result_df