"""
Testes do processamento batch da Bronze.

Objetivo
--------
Validar o comportamento operacional do pipeline Bronze em lote.

Este é o teste mais importante da Bronze porque garante
que o pipeline completo mantém seus contratos operacionais.

Contratos protegidos
--------------------

1. O batch deve processar todos os arquivos da Landing.
2. O manifest deve impedir reprocessamento desnecessário.
3. force_reprocess=True deve ignorar idempotência.
4. O retorno deve sempre ser um pandas.DataFrame.

Se este teste falhar, a Bronze inteira está comprometida.
"""

import pandas as pd

from src.bronze.batch import run_bronze_batch


def test_bronze_batch_returns_dataframe():
    """
    Valida contrato principal do batch.

    Toda execução batch deve retornar DataFrame contendo
    o resultado operacional da execução atual.
    """

    result = run_bronze_batch(
        force_reprocess=False
    )

    assert isinstance(result, pd.DataFrame)


def test_bronze_batch_skips_processed_files():
    """
    Valida mecanismo de idempotência.

    Como todos os arquivos já foram processados anteriormente,
    a execução sem force_reprocess deve retornar apenas SKIPPED.
    """

    result = run_bronze_batch(
        force_reprocess=False
    )

    statuses = result["status"].unique()

    assert len(statuses) == 1
    assert statuses[0] == "SKIPPED"


def test_bronze_batch_force_reprocess():
    """
    Valida reprocessamento forçado.

    force_reprocess=True deve ignorar o manifest
    e executar novamente todos os arquivos.
    """

    result = run_bronze_batch(
        force_reprocess=True
    )

    assert "SUCCESS" in result["status"].values