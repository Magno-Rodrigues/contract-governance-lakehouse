from pathlib import Path
from datetime import datetime, timezone
import hashlib
import pandas as pd


def calculate_file_hash(file_path: Path) -> str:
    """
    Calcula o hash SHA-256 do conteúdo do arquivo.

    Esse hash permite rastrear mudanças reais no conteúdo,
    mesmo quando o nome do arquivo permanece igual.
    """
    sha256 = hashlib.sha256()

    with file_path.open("rb") as file:
        for block in iter(lambda: file.read(8192), b""):
            sha256.update(block)

    return sha256.hexdigest()


def discover_raw_files(
    raw_path: Path,
    bucket_name: str,
    landing_prefix: str,
) -> pd.DataFrame:
    """
    Descobre arquivos disponíveis na pasta RAW local.

    Convenção esperada:
        RAW/{snapshot_date}/{tipo_relatorio}/{arquivo}

    Exemplo:
        RAW/2026-06-13_0800/NACT/202211_ADMIN.xlsb
    """
    records = []

    if not raw_path.exists():
        raise FileNotFoundError(f"Pasta RAW não encontrada: {raw_path}")

    for file_path in raw_path.rglob("*"):
        # Ignora diretórios.
        if not file_path.is_file():
            continue

        relative_path = file_path.relative_to(raw_path)

        # A primeira pasta abaixo de RAW representa o snapshot.
        snapshot_date = relative_path.parts[0]

        # Preserva toda a estrutura original abaixo do snapshot.
        landing_key = (
            f"{landing_prefix}/"
            f"snapshot_date={snapshot_date}/"
            f"{'/'.join(relative_path.parts[1:])}"
        )

        records.append(
            {
                "snapshot_date": snapshot_date,
                "source_file": file_path.name,
                "source_path": str(file_path),
                "relative_path": str(relative_path),
                "landing_bucket": bucket_name,
                "landing_key": landing_key,
                "file_extension": file_path.suffix.lower(),
                "file_size_bytes": file_path.stat().st_size,
                "file_hash": calculate_file_hash(file_path),
                "discovered_at": datetime.now(timezone.utc).isoformat(),
            }
        )

    return pd.DataFrame(records)