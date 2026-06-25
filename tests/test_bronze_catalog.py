"""
Testes automatizados do BronzeCatalog.

Objetivo
--------
O BronzeCatalog é responsável por traduzir nomes de arquivos
recebidos da Landing em duas informações críticas para a Bronze:

1. source_type
   Determina qual reader deve ser utilizado
   (csv, xlsx ou xlsb).

2. dataset_name
   Define o nome lógico do dataset dentro do Data Lake.

Por que estes testes são importantes?
-------------------------------------

Toda execução batch da Bronze depende desse catálogo.

Se um novo arquivo for mapeado incorretamente:

- o reader errado será utilizado;
- o arquivo poderá falhar durante ingestão;
- ou poderá ser salvo no dataset incorreto.

Esses testes protegem o comportamento central do batch pipeline.
"""

from src.bronze.catalog import BronzeCatalog


def test_get_source_type_csv():
    """
    Valida identificação de arquivos CSV.

    O pipeline deve encaminhar arquivos .csv
    para o CSVReader.
    """

    result = BronzeCatalog.get_source_type(
        "arquivo.csv"
    )

    assert result == "csv"


def test_get_source_type_xlsx():
    """
    Valida identificação de arquivos Excel XLSX.

    O pipeline deve encaminhar arquivos .xlsx
    para o ExcelReader.
    """

    result = BronzeCatalog.get_source_type(
        "arquivo.xlsx"
    )

    assert result == "xlsx"


def test_get_source_type_xlsb():
    """
    Valida identificação de arquivos Excel binário XLSB.

    O formato XLSB é usado atualmente pelo NACT,
    que possui layouts variáveis dependendo
    da consultoria terceirizada.
    """

    result = BronzeCatalog.get_source_type(
        "arquivo.xlsb"
    )

    assert result == "xlsb"


def test_get_dataset_name_qec():
    """
    Valida mapeamento dos arquivos QEC.

    Arquivos QEC possuem numeração variável
    no nome do arquivo, mas todos devem
    apontar para o dataset lógico 'qec'.
    """

    result = BronzeCatalog.get_dataset_name(
        "QEC_5900055119_7_55_77.csv"
    )

    assert result == "qec"


def test_get_dataset_name_nact():
    """
    Valida identificação do dataset NACT.

    O dataset NACT é tratado de forma especial
    no projeto porque não pertence ao SGC
    e pode sofrer mudanças frequentes de layout.
    """

    result = BronzeCatalog.get_dataset_name(
        "202211_ADMIN.xlsb"
    )

    assert result == "nact"


def test_get_dataset_name_known_file():
    """
    Valida mapeamento de arquivos conhecidos.

    Garante que arquivos padronizados do SGC
    sejam enviados para o dataset correto.
    """

    result = BronzeCatalog.get_dataset_name(
        "ControleMedicoesPagamentos.csv"
    )

    assert result == "controle_medicoes_pagamentos"