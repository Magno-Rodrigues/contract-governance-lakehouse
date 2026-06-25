import pandas as pd

from src.config.settings import Settings
from src.bronze.batch_processor import BronzeBatchProcessor
from src.bronze.execution_logger import BronzeExecutionLogger
from src.bronze.manifest import BronzeProcessedManifest
from src.bronze.pipeline import BronzePipeline
from src.bronze.quality_logger import BronzeQualityLogger


def run_bronze_batch(force_reprocess: bool = False) -> pd.DataFrame:
    """
    Executa ingestão Bronze em lote.

    O batch é intencionalmente simples:
    - carrega metadados da Landing;
    - cria dependências principais;
    - processa cada arquivo;
    - persiste logs operacionais;
    - atualiza manifest dos arquivos processados.
    """

    landing_metadata_df = pd.read_csv(Settings.LANDING_METADATA_PATH)

    execution_id = BronzeExecutionLogger.generate_execution_id()
    processed_manifest_df = BronzeProcessedManifest.load()
    pipeline = BronzePipeline()

    processor = BronzeBatchProcessor(
        pipeline=pipeline,
        processed_manifest_df=processed_manifest_df,
        execution_id=execution_id,
        force_reprocess=force_reprocess,
    )

    results = [
        processor.process(row)
        for _, row in landing_metadata_df.iterrows()
    ]

    current_run_df = pd.DataFrame(results)

    successful_records = current_run_df[
        current_run_df["status"] == "SUCCESS"
    ]

    manifest_records = [
        BronzeProcessedManifest.build_record(
            source_file=row["source_file"],
            snapshot_date=row["snapshot_date"],
            source_type=row["source_type"],
            dataset_name=row["dataset_name"],
            file_hash=row["file_hash"],
            bronze_path=row["bronze_path"],
            pipeline_version=Settings.BRONZE_PIPELINE_VERSION,
        )
        for _, row in successful_records.iterrows()
    ]

    quality_records = BronzeBatchProcessor.build_quality_records(
        result_df=current_run_df
    )

    BronzeExecutionLogger.append_execution_log(current_run_df)
    BronzeProcessedManifest.upsert(manifest_records)
    BronzeQualityLogger.append_quality_log(quality_records)

    return current_run_df