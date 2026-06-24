from datetime import datetime, timezone

import pandas as pd

from src.config.settings import Settings
from src.bronze.catalog import BronzeCatalog
from src.bronze.pipeline import BronzePipeline
from src.bronze.execution_logger import BronzeExecutionLogger
from src.bronze.quality_logger import BronzeQualityLogger


def run_bronze_batch(force_reprocess: bool = False) -> pd.DataFrame:
    """
    Executa ingestão Bronze em lote usando landing_metadata.csv.

    Regras:
    - lê todos os arquivos registrados na Landing;
    - pula arquivos já processados com mesmo hash, salvo force_reprocess=True;
    - registra SUCCESS, FAILED ou SKIPPED por arquivo;
    - retorna apenas a execução atual;
    - persiste histórico acumulado no bronze_execution_log.csv.
    """

    landing_metadata_df = pd.read_csv(Settings.LANDING_METADATA_PATH)

    existing_log_df = BronzeExecutionLogger.load_existing_log()
    execution_id = BronzeExecutionLogger.generate_execution_id()
    pipeline = BronzePipeline()

    results = []
    quality_records = []

    for _, row in landing_metadata_df.iterrows():
        start_time = datetime.now(timezone.utc)

        source_file = row["source_file"]
        snapshot_date = row["snapshot_date"]
        file_hash = row["file_hash"]

        try:
            source_type = BronzeCatalog.get_source_type(source_file)
            dataset_name = BronzeCatalog.get_dataset_name(source_file)

            already_processed = BronzeExecutionLogger.was_successfully_processed(
                existing_log_df=existing_log_df,
                source_file=source_file,
                snapshot_date=snapshot_date,
                file_hash=file_hash,
            )

            if already_processed and not force_reprocess:
                end_time = datetime.now(timezone.utc)

                results.append(
                    BronzeExecutionLogger.build_execution_record(
                        execution_id=execution_id,
                        source_file=source_file,
                        snapshot_date=snapshot_date,
                        source_type=source_type,
                        dataset_name=dataset_name,
                        file_hash=file_hash,
                        status="SKIPPED",
                        start_time=start_time,
                        end_time=end_time,
                        bronze_path=None,
                        error_message=None,
                    )
                )

                continue

            output_path = pipeline.run(
                source_path=row["source_path"],
                source_type=source_type,
                dataset_name=dataset_name,
                snapshot_date=snapshot_date,
                source_file=source_file,
                file_hash=file_hash,
            )

            end_time = datetime.now(timezone.utc)

            
            if source_file == "Relatorio_geral_irregularidades.csv":
                quality_records.append(
                    BronzeQualityLogger.build_record(
                        source_file=source_file,
                        snapshot_date=snapshot_date,
                        source_path=row["source_path"],
                        issue_type="BAD_CSV_LINE_SKIPPED",
                        issue_description=(
                            "CSV contained at least one malformed line skipped by pandas "
                            "during Bronze ingestion. Current known case: line 479."
                        ),
                        line_number=479,
                        severity="WARNING",
                    )
            )
            

            results.append(
                BronzeExecutionLogger.build_execution_record(
                    execution_id=execution_id,
                    source_file=source_file,
                    snapshot_date=snapshot_date,
                    source_type=source_type,
                    dataset_name=dataset_name,
                    file_hash=file_hash,
                    status="SUCCESS",
                    start_time=start_time,
                    end_time=end_time,
                    bronze_path=output_path,
                    error_message=None,
                )
            )

        except Exception as error:
            end_time = datetime.now(timezone.utc)

            results.append(
                BronzeExecutionLogger.build_execution_record(
                    execution_id=execution_id,
                    source_file=source_file,
                    snapshot_date=snapshot_date,
                    source_type=None,
                    dataset_name=None,
                    file_hash=file_hash,
                    status="FAILED",
                    start_time=start_time,
                    end_time=end_time,
                    bronze_path=None,
                    error_message=str(error),
                )
            )

    current_run_df = pd.DataFrame(results)

    BronzeExecutionLogger.append_execution_log(current_run_df)
    BronzeQualityLogger.append_quality_log(quality_records)

    return current_run_df