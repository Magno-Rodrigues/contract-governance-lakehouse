from pathlib import Path


class BronzeCatalog:
    """
    Catálogo técnico da Bronze.

    Responsável por transformar informações da Landing
    em metadados necessários para ingestão Bronze.
    """

    DATASET_MAPPING = {
        "ControleMedicoesPagamentos.csv": "controle_medicoes_pagamentos",
        "Exportação_bm_acompanhamento.xlsx": "controle_medicoes_andamento",
        "Controle_Subcontratadas.xlsx": "controle_subcontratadas",
        "AnaliticoProjeto.csv": "analitico_projeto",
        "Relatorio_geral_irregularidades.csv": "relatorio_geral_irregularidades",
    }

    @classmethod
    def get_source_type(cls, source_file: str) -> str:
        """
        Retorna o source_type a partir da extensão do arquivo.
        """
        extension = Path(source_file).suffix.lower().replace(".", "")

        if extension == "xlsx":
            return "xlsx"

        if extension == "xlsb":
            return "xlsb"

        if extension == "csv":
            return "csv"

        raise ValueError(f"Extensão não suportada: {extension}")

    @classmethod
    def get_dataset_name(cls, source_file: str) -> str:
        """
        Resolve nome técnico do dataset Bronze.
        """

        if source_file.startswith("QEC_"):
            return "qec"

        if source_file.endswith("_ADMIN.xlsb"):
            return "nact"

        if source_file in cls.DATASET_MAPPING:
            return cls.DATASET_MAPPING[source_file]

        # Fallback técnico para arquivos ainda não mapeados.
        return (
            Path(source_file)
            .stem
            .lower()
            .replace(" ", "_")
            .replace("-", "_")
        )