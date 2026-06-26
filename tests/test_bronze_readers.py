"""
Testes automatizados dos Readers da Bronze.

Objetivo
--------
Validar contratos mínimos dos readers responsáveis por arquivos locais.

A Bronze aceita arquivos de múltiplos formatos, mas todos os readers
devem obedecer ao mesmo contrato:

- receber um source_path;
- retornar um pandas.DataFrame;
- normalizar nomes de colunas;
- remover linhas completamente vazias;
- preservar os dados sem aplicar regra de negócio.

Importante
----------
Estes testes são unitários. Portanto, não devem depender de arquivos reais
em /app/data/raw_local.

Arquivos reais são validados nos notebooks e em testes de integração.
"""

import pandas as pd
import pytest

from src.bronze.readers.file.csv_reader import CSVReader
from src.bronze.readers.file.excel_reader import ExcelReader
from src.bronze.readers.file.xlsb_reader import XLSBReader


def test_csv_reader_returns_dataframe(tmp_path):
    """
    Valida que o CSVReader lê um arquivo CSV simples e retorna DataFrame.

    O arquivo é criado em tempo de teste para evitar dependência de paths
    locais ou snapshots específicos do projeto.
    """

    source_path = tmp_path / "sample.csv"

    source_path.write_text(
        "contrato;valor\n5900055119;100\n",
        encoding="utf-8",
    )

    df = CSVReader().read(str(source_path))

    assert isinstance(df, pd.DataFrame)
    assert not df.empty


def test_csv_reader_normalizes_columns(tmp_path):
    """
    Valida normalização técnica de colunas CSV.

    A coluna original possui acento, espaço e caractere especial.
    Na Bronze, ela deve chegar como nome técnico padronizado.
    """

    source_path = tmp_path / "sample_columns.csv"

    source_path.write_text(
        "PROJETO/ÁREA DE OPERAÇÃO VALE;VALOR TOTAL\n"
        "Vitória;100\n",
        encoding="utf-8",
    )

    df = CSVReader().read(str(source_path))

    assert "projeto_area_de_operacao_vale" in df.columns
    assert "valor_total" in df.columns


def test_excel_reader_returns_dataframe(tmp_path):
    """
    Valida que o ExcelReader lê um XLSX simples e retorna DataFrame.

    O arquivo é criado dinamicamente para manter o teste independente
    dos dados reais do projeto.
    """

    source_path = tmp_path / "sample.xlsx"

    pd.DataFrame(
        [{"contrato": "5900055119", "valor": "100"}]
    ).to_excel(
        source_path,
        index=False,
    )

    df = ExcelReader().read(str(source_path))

    assert isinstance(df, pd.DataFrame)
    assert not df.empty


@pytest.mark.skip(
    reason=(
        "XLSB é formato binário difícil de gerar em teste unitário. "
        "Validado via notebooks/testes de integração com arquivo real."
    )
)
def test_xlsb_reader_returns_dataframe():
    """
    Valida leitura básica de XLSB real.

    Este teste fica marcado como skip porque depende de fixture binária real.
    """

    df = XLSBReader().read("tests/fixtures/sample.xlsb")

    assert isinstance(df, pd.DataFrame)
    assert not df.empty


@pytest.mark.skip(
    reason=(
        "XLSB é formato binário difícil de gerar em teste unitário. "
        "Validado via notebooks/testes de integração com arquivo real."
    )
)
def test_xlsb_reader_preserves_raw_layout():
    """
    Valida que o XLSBReader preserva layout bruto.

    A Bronze não interpreta layout de negócio.
    A Canonical Layer é responsável por interpretar estruturas específicas.
    """

    df = XLSBReader().read("tests/fixtures/sample.xlsb")

    assert any(column.startswith("unnamed_") for column in df.columns)