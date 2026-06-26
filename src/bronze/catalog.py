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
    def get_dataset_name(
        cls,
        source_file: str,
        source_path: str = None,
    ) -> str:
        """
        Resolve o dataset Bronze.

        A pasta NACT define o domínio do dado.
        Isso é mais robusto que depender do nome ou extensão do arquivo,
        pois o fornecedor pode mudar layout, padrão de nome e formato.
        """

        normalized_path = str(source_path or "").replace("\\", "/").upper()

        if "/NACT/" in normalized_path:
            return "nact"

        if source_file.startswith("QEC_"):
            return "qec"

        if source_file in cls.DATASET_MAPPING:
            return cls.DATASET_MAPPING[source_file]

        return (
            Path(source_file)
            .stem
            .lower()
            .replace(" ", "_")
            .replace("-", "_")
        )