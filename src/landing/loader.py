from datetime import datetime, timezone
from pathlib import Path

import boto3
import pandas as pd

from src.config.settings import Settings
from src.landing.metadata import discover_raw_files


def create_s3_client():
    """
    Cria cliente S3 compatível com MinIO.

    A Landing usa boto3 porque trabalha com cópia de arquivos
    brutos, sem transformação tabular.
    """
    return boto3.client(
        "s3",
        endpoint_url=Settings.MINIO_ENDPOINT,
        aws_access_key_id=Settings.AWS_ACCESS_KEY,
        aws_secret_access_key=Settings.AWS_SECRET_KEY,
        region_name=Settings.AWS_REGION,
    )


def ensure_bucket_exists(s3_client, bucket_name: str) -> None:
    """
    Garante que o bucket existe antes do upload.
    """
    existing_buckets = [
        bucket["Name"]
        for bucket in s3_client.list_buckets()["Buckets"]
    ]

    if bucket_name not in existing_buckets:
        s3_client.create_bucket(Bucket=bucket_name)


def upload_file_to_landing(
    s3_client,
    row: pd.Series,
    bucket_name: str,
) -> dict:
    """
    Envia um arquivo local para a Landing Zone no MinIO.

    Regra da Landing:
    - não altera conteúdo;
    - não renomeia arquivo original;
    - não aplica regra de negócio;
    - preserva snapshot e caminho original.
    """
    source_path = Path(row["source_path"])
    landing_key = row["landing_key"]

    s3_client.upload_file(
        Filename=str(source_path),
        Bucket=bucket_name,
        Key=landing_key,
    )

    result = row.to_dict()
    result["upload_status"] = "SUCCESS"
    result["uploaded_at"] = datetime.now(timezone.utc).isoformat()
    result["error_message"] = None

    return result


def run_landing_pipeline() -> pd.DataFrame:
    """
    Executa o pipeline completo da Landing Zone.

    Etapas:
    1. cria cliente S3/MinIO;
    2. garante bucket;
    3. descobre arquivos RAW;
    4. envia arquivos para Landing;
    5. salva metadados locais.
    """
    s3_client = create_s3_client()
    ensure_bucket_exists(s3_client, Settings.BUCKET_NAME)

    files_df = discover_raw_files(
        raw_path=Settings.RAW_LOCAL_PATH,
        bucket_name=Settings.BUCKET_NAME,
        landing_prefix=Settings.LANDING_PREFIX,
    )

    upload_results = []

    for _, row in files_df.iterrows():
        try:
            upload_results.append(
                upload_file_to_landing(
                    s3_client=s3_client,
                    row=row,
                    bucket_name=Settings.BUCKET_NAME,
                )
            )

        except Exception as error:
            failed_result = row.to_dict()
            failed_result["upload_status"] = "FAILED"
            failed_result["uploaded_at"] = datetime.now(timezone.utc).isoformat()
            failed_result["error_message"] = str(error)

            upload_results.append(failed_result)

    metadata_df = pd.DataFrame(upload_results)

    Settings.LANDING_METADATA_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    metadata_df.to_csv(
        Settings.LANDING_METADATA_PATH,
        index=False,
        encoding="utf-8",
    )

    return metadata_df


if __name__ == "__main__":
    result_df = run_landing_pipeline()

    print("Landing pipeline finalizado.")
    print(result_df["upload_status"].value_counts())
    print(f"Metadados salvos em: {Settings.LANDING_METADATA_PATH}")