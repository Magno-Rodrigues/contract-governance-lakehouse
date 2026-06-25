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

Esses testes protegem a consistência entre CSVReader, ExcelReader e XLSBReader.
"""

import pandas as pd

from src.bronze.readers.file.csv_reader import CSVReader
from src.bronze.readers.file.excel_reader import ExcelReader
from src.bronze.readers.file.xlsb_reader import XLSBReader


def test_csv_reader_returns_dataframe():
    """
    Valida leitura básica de CSV real do projeto.

    Este teste garante que o CSVReader continua capaz de ler
    arquivos operacionais do SGC e retornar pandas.DataFrame.
    """

    source_path = (
        "/app/data/raw_local/RAW/2024-07-13_0800/"
        "CONTROLE DE MEDICOES E PAGAMENTOS/"
        "ControleMedicoesPagamentos.csv"
    )

    df = CSVReader().read(source_path)

    assert isinstance(df, pd.DataFrame)
    assert not df.empty


def test_csv_reader_normalizes_columns():
    """
    Valida normalização técnica de colunas CSV.

    A coluna original possui acento e separador especial.
    Na Bronze, ela deve chegar como nome técnico padronizado.
    """

    source_path = (
        "/app/data/raw_local/RAW/2024-07-13_0800/"
        "CONTROLE DE MEDICOES E PAGAMENTOS/"
        "ControleMedicoesPagamentos.csv"
    )

    df = CSVReader().read(source_path)

    assert "projeto_area_de_operacao_vale" in df.columns


def test_excel_reader_returns_dataframe():
    """
    Valida leitura básica de XLSX real do projeto.

    O ExcelReader usa pandas/openpyxl porque XLSX não é formato
    nativo distribuído para Spark.
    """

    source_path = (
        "/app/data/raw_local/RAW/2024-07-13_0800/"
        "CONTROLE DE MEDICOES EM ANDAMENTO/"
        "Exportação_bm_acompanhamento.xlsx"
    )

    df = ExcelReader().read(source_path)

    assert isinstance(df, pd.DataFrame)
    assert not df.empty


def test_xlsb_reader_returns_dataframe():
    """
    Valida leitura básica de XLSB real do projeto.

    O XLSBReader é importante para o NACT, fonte externa com
    layout dependente de fornecedor.
    """

    source_path = (
        "/app/data/raw_local/RAW/2024-07-13_0800/"
        "NACT/"
        "202211_ADMIN.xlsb"
    )

    df = XLSBReader().read(source_path)

    assert isinstance(df, pd.DataFrame)
    assert not df.empty


def test_xlsb_reader_preserves_raw_layout():
    """
    Valida que o XLSBReader não tenta inferir layout de negócio.

    O NACT possui cabeçalhos e seções antes da tabela real.
    Na Bronze, isso deve ser preservado de forma schema-agnostic.
    A Canonical Layer será responsável por interpretar o layout.
    """

    source_path = (
        "/app/data/raw_local/RAW/2024-07-13_0800/"
        "NACT/"
        "202211_ADMIN.xlsb"
    )

    df = XLSBReader().read(source_path)

    assert any(column.startswith("unnamed_") for column in df.columns)