from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
import time
import uuid

import pandas as pd
from pandas.errors import EmptyDataError

from src.config.settings import Settings
from src.bronze.catalog import BronzeCatalog
from src.bronze.pipeline import BronzePipeline


def _generate_execution_id() -> str:
    """Gera um ID único para rastrear uma execução batch da Bronze."""
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    short_uuid = str(uuid.uuid4())[:8]
    return f"bronze_{timestamp}_{short_uuid}"


def _read_csv_if_exists(path: Path) -> pd.DataFrame:
    """
    Lê um CSV de controle se ele existir.

    Retorna DataFrame vazio quando:
    - o arquivo não existe;
    - o arquivo existe, mas está vazio;
    - o arquivo foi criado parcialmente por execução interrompida.
    """
    if not path.exists():
        return pd.DataFrame()

    try:
        return pd.read_csv(path)
    except EmptyDataError:
        return pd.DataFrame()


def _already_processed(
    manifest_df: pd.DataFrame,
    source_file: str,
    snapshot_date: str,
    file_hash: str,
) -> bool:
    """
    Verifica idempotência usando o manifest operacional.

    O manifest representa o estado atual dos arquivos já processados.
    Ele é mais adequado para idempotência do que o execution log,
    que cresce como histórico de auditoria.
    """
    if manifest_df.empty:
        return False

    required_columns = {"source_file", "snapshot_date", "file_hash"}

    if not required_columns.issubset(manifest_df.columns):
        return False

    matched_df = manifest_df[
        (manifest_df["source_file"] == source_file)
        & (manifest_df["snapshot_date"] == snapshot_date)
        & (manifest_df["file_hash"] == file_hash)
    ]

    return not matched_df.empty


def _execute_with_retry(operation, max_retries: int, delay_seconds: int, **kwargs):
    """
    Executa uma operação com retry simples.

    Em ambiente distribuído, falhas transitórias podem ocorrer por:
    - indisponibilidade temporária do Spark worker;
    - timeout de escrita no object storage;
    - instabilidade momentânea de rede;
    - lock temporário de arquivo.

    O retry evita marcar como FAILED uma execução que falhou por motivo
    temporário de infraestrutura.
    """
    last_error = None

    for attempt in range(max_retries):
        try:
            return operation(**kwargs), attempt

        except Exception as error:
            last_error = error

            if attempt < max_retries - 1:
                time.sleep(delay_seconds)

    raise last_error


def _build_execution_record(
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
) -> Dict[str, Any]:
    """Cria um registro padronizado para o execution log."""
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
        "duration_seconds": (end_time - start_time).total_seconds(),
        "retry_count": retry_count,
        "bronze_path": bronze_path,
        "error_message": error_message,
    }


def _build_manifest_record(
    execution_record: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Cria registro do manifest operacional.

    O manifest guarda apenas arquivos processados com sucesso,
    representando o estado atual da Bronze.
    """
    return {
        "source_file": execution_record["source_file"],
        "snapshot_date": execution_record["snapshot_date"],
        "source_type": execution_record["source_type"],
        "dataset_name": execution_record["dataset_name"],
        "file_hash": execution_record["file_hash"],
        "bronze_path": execution_record["bronze_path"],
        "pipeline_version": Settings.BRONZE_PIPELINE_VERSION,
        "processed_at": datetime.now(timezone.utc).isoformat(),
    }


def _build_quality_records(current_run_df: pd.DataFrame) -> List[Dict[str, Any]]:
    """
    Registra anomalias técnicas conhecidas da ingestão Bronze.

    Hoje sabemos que o dataset Relatorio_geral_irregularidades.csv possui
    uma linha malformada descartada pelo pandas durante leitura CSV.

    Isso mantém a Bronze resiliente sem esconder a anomalia.
    No futuro, esse registro deve vir diretamente do CSVReader.
    """
    quality_records: List[Dict[str, Any]] = []

    success_df = current_run_df[current_run_df["status"] == "SUCCESS"]

    irregularities_df = success_df[
        success_df["source_file"] == "Relatorio_geral_irregularidades.csv"
    ]

    for _, row in irregularities_df.iterrows():
        quality_records.append(
            {
                "logged_at": datetime.now(timezone.utc).isoformat(),
                "source_file": row["source_file"],
                "snapshot_date": row["snapshot_date"],
                "source_path": None,
                "issue_type": "BAD_CSV_LINE_SKIPPED",
                "issue_description": (
                    "CSV contained at least one malformed line skipped "
                    "during Bronze ingestion. Current known case: line 479."
                ),
                "line_number": 479,
                "severity": "WARNING",
            }
        )

    return quality_records


def _append_csv(path: Path, current_df: pd.DataFrame) -> None:
    """
    Persiste logs acumulando histórico.

    Usado para execution log e quality log.
    """
    if current_df.empty:
        return

    path.parent.mkdir(parents=True, exist_ok=True)

    existing_df = _read_csv_if_exists(path)

    if existing_df.empty:
        final_df = current_df
    else:
        final_df = pd.concat([existing_df, current_df], ignore_index=True)

    final_df.to_csv(path, index=False, encoding="utf-8")


def _upsert_manifest(records: List[Dict[str, Any]]) -> None:
    """
    Atualiza o manifest mantendo apenas um registro por arquivo/hash.

    Chave lógica:
    - source_file
    - snapshot_date
    - file_hash
    """
    if not records:
        return

    manifest_path = Settings.BRONZE_PROCESSED_MANIFEST_PATH
    manifest_path.parent.mkdir(parents=True, exist_ok=True)

    current_df = pd.DataFrame(records)
    existing_df = _read_csv_if_exists(manifest_path)

    if existing_df.empty:
        final_df = current_df
    else:
        final_df = pd.concat([existing_df, current_df], ignore_index=True)
        final_df = final_df.drop_duplicates(
            subset=["source_file", "snapshot_date", "file_hash"],
            keep="last",
        )

    final_df.to_csv(manifest_path, index=False, encoding="utf-8")


def _process_file(
    row: pd.Series,
    pipeline: BronzePipeline,
    manifest_df: pd.DataFrame,
    execution_id: str,
    force_reprocess: bool,
) -> Dict[str, Any]:
    """
    Processa um único arquivo da Landing.

    Essa função concentra a decisão operacional por arquivo:
    - descobrir tipo;
    - resolver dataset;
    - verificar idempotência;
    - executar BronzePipeline com retry;
    - retornar registro de execução.
    """
    start_time = datetime.now(timezone.utc)

    source_file = row["source_file"]
    snapshot_date = row["snapshot_date"]
    file_hash = row["file_hash"]

    try:
        source_type = BronzeCatalog.get_source_type(source_file)
        dataset_name = BronzeCatalog.get_dataset_name(source_file)

        if (
            not force_reprocess
            and _already_processed(
                manifest_df=manifest_df,
                source_file=source_file,
                snapshot_date=snapshot_date,
                file_hash=file_hash,
            )
        ):
            return _build_execution_record(
                execution_id=execution_id,
                source_file=source_file,
                snapshot_date=snapshot_date,
                source_type=source_type,
                dataset_name=dataset_name,
                file_hash=file_hash,
                status="SKIPPED",
                start_time=start_time,
                end_time=datetime.now(timezone.utc),
                retry_count=0,
            )

        output_path, retry_count = _execute_with_retry(
            operation=pipeline.run,
            max_retries=Settings.BRONZE_MAX_RETRIES,
            delay_seconds=Settings.BRONZE_RETRY_DELAY_SECONDS,
            source_path=row["source_path"],
            source_type=source_type,
            dataset_name=dataset_name,
            snapshot_date=snapshot_date,
            source_file=source_file,
            file_hash=file_hash,
        )

        return _build_execution_record(
            execution_id=execution_id,
            source_file=source_file,
            snapshot_date=snapshot_date,
            source_type=source_type,
            dataset_name=dataset_name,
            file_hash=file_hash,
            status="SUCCESS",
            start_time=start_time,
            end_time=datetime.now(timezone.utc),
            bronze_path=output_path,
            retry_count=retry_count,
        )

    except Exception as error:
        return _build_execution_record(
            execution_id=execution_id,
            source_file=source_file,
            snapshot_date=snapshot_date,
            source_type=None,
            dataset_name=None,
            file_hash=file_hash,
            status="FAILED",
            start_time=start_time,
            end_time=datetime.now(timezone.utc),
            error_message=str(error),
            retry_count=0,
        )


def run_bronze_batch(force_reprocess: bool = False) -> pd.DataFrame:
    """
    Executa ingestão Bronze em lote.

    Fluxo:
    1. lê landing_metadata.csv;
    2. carrega o manifest operacional;
    3. processa cada arquivo;
    4. grava execution log;
    5. grava quality log;
    6. atualiza manifest com sucessos;
    7. retorna somente a execução atual.

    Parâmetros
    ----------
    force_reprocess:
        Se False, arquivos já processados são marcados como SKIPPED.
        Se True, todos os arquivos são reprocessados.
    """
    landing_metadata_df = pd.read_csv(Settings.LANDING_METADATA_PATH)

    execution_id = _generate_execution_id()
    manifest_df = _read_csv_if_exists(Settings.BRONZE_PROCESSED_MANIFEST_PATH)
    pipeline = BronzePipeline()

    results = [
        _process_file(
            row=row,
            pipeline=pipeline,
            manifest_df=manifest_df,
            execution_id=execution_id,
            force_reprocess=force_reprocess,
        )
        for _, row in landing_metadata_df.iterrows()
    ]

    current_run_df = pd.DataFrame(results)

    success_df = current_run_df[current_run_df["status"] == "SUCCESS"]

    manifest_records = [
        _build_manifest_record(row.to_dict())
        for _, row in success_df.iterrows()
    ]

    quality_records = _build_quality_records(current_run_df)

    _append_csv(Settings.BRONZE_EXECUTION_LOG_PATH, current_run_df)
    _append_csv(Settings.BRONZE_QUALITY_LOG_PATH, pd.DataFrame(quality_records))
    _upsert_manifest(manifest_records)

    return current_run_df