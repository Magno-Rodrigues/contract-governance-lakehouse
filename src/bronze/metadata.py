from datetime import datetime, timezone

from pyspark.sql import DataFrame
from pyspark.sql.functions import lit, monotonically_increasing_id


def enrich_with_bronze_metadata(
    df: DataFrame,
    snapshot_date: str,
    source_file: str,
    source_path: str,
    source_type: str,
    file_hash: str,
    pipeline_version: str = "bronze_v1",
) -> DataFrame:
    """
    Adiciona metadados técnicos obrigatórios ao DataFrame Bronze.

    A Bronze deve preservar rastreabilidade completa:
    - de qual snapshot veio;
    - de qual arquivo veio;
    - qual era o hash do arquivo;
    - quando foi processado;
    - qual versão do pipeline processou;
    - número técnico do registro.

    Importante:
    ----------
    Esses campos não são regras de negócio.
    São campos de governança, auditoria e lineage.
    """

    ingestion_timestamp = datetime.now(timezone.utc).isoformat()

    return (
        df
        # Snapshot lógico do arquivo de origem.
        .withColumn("_snapshot_date", lit(snapshot_date))

        # Nome original do arquivo.
        .withColumn("_source_file", lit(source_file))

        # Caminho original da fonte na Landing.
        .withColumn("_source_path", lit(source_path))

        # Tipo técnico da fonte: csv, xlsx, xlsb, api, database etc.
        .withColumn("_source_type", lit(source_type))

        # Hash SHA-256 calculado na Landing.
        .withColumn("_file_hash", lit(file_hash))

        # Timestamp UTC da ingestão Bronze.
        .withColumn("_bronze_ingestion_timestamp", lit(ingestion_timestamp))

        # Versão lógica do pipeline.
        .withColumn("_pipeline_version", lit(pipeline_version))

        # Identificador técnico do registro dentro do processamento.
        # Não deve ser usado como chave de negócio.
        .withColumn("_record_number", monotonically_increasing_id())
    )