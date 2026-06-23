from datetime import datetime, timezone
import pandas as pd

from src.config.settings import Settings
from src.bronze.catalog import BronzeCatalog
from src.bronze.pipeline import BronzePipeline


def run_bronze_batch() -> pd.DataFrame:
    """
    Executa ingestão Bronze em lote usando landing_metadata.csv.

    A função:
    - lê metadados da Landing;
    - identifica source_type;
    - resolve dataset_name;
    - executa BronzePipeline para cada arquivo;
    - registra sucesso/falha por arquivo.
    """

    landing_metadata_df = pd.read_csv(
        Settings.LANDING_METADATA_PATH
    )

    pipeline = BronzePipeline()

    results = []

    for _, row in landing_metadata_df.iterrows():
        source_file = row["source_file"]

        try:
            source_type = BronzeCatalog.get_source_type(
                source_file=source_file
            )

            dataset_name = BronzeCatalog.get_dataset_name(
                source_file=source_file
            )

            output_path = pipeline.run(
                source_path=row["source_path"],
                source_type=source_type,
                dataset_name=dataset_name,
                snapshot_date=row["snapshot_date"],
                source_file=source_file,
                file_hash=row["file_hash"],
            )

            results.append(
                {
                    "source_file": source_file,
                    "snapshot_date": row["snapshot_date"],
                    "source_type": source_type,
                    "dataset_name": dataset_name,
                    "bronze_path": output_path,
                    "bronze_status": "SUCCESS",
                    "error_message": None,
                    "processed_at": datetime.now(timezone.utc).isoformat(),
                }
            )

        except Exception as error:
            results.append(
                {
                    "source_file": source_file,
                    "snapshot_date": row.get("snapshot_date"),
                    "source_type": None,
                    "dataset_name": None,
                    "bronze_path": None,
                    "bronze_status": "FAILED",
                    "error_message": str(error),
                    "processed_at": datetime.now(timezone.utc).isoformat(),
                }
            )

    return pd.DataFrame(results)