from pathlib import Path


class ReaderRegistry:
    """
    Registry responsável por decidir qual Reader
    será usado para cada tipo de fonte.

    O objetivo é desacoplar o pipeline Bronze
    dos formatos específicos de dados.

    O pipeline nunca chama CSVReader diretamente.

    Ele pergunta ao Registry:
        'qual reader deve processar este arquivo?'
    """

    # Mapeamento inicial de extensões para readers.
    # Futuramente isso pode ser movido para catálogo externo.
    READER_MAPPING = {
        ".csv": "CSVReader",
        ".xlsx": "ExcelReader",
        ".xlsb": "XLSBReader",
        ".json": "JSONReader",
        ".parquet": "ParquetReader"
    }

    @classmethod
    def get_reader_name(
        cls,
        source_file: str
    ) -> str:
        """
        Retorna o nome do Reader apropriado
        baseado na extensão do arquivo.

        Parameters
        ----------
        source_file : str
            Nome do arquivo de origem.

        Returns
        -------
        str
            Nome do reader responsável.
        """

        file_extension = Path(source_file).suffix.lower()

        if file_extension not in cls.READER_MAPPING:
            raise ValueError(
                f"Nenhum reader registrado para extensão: {file_extension}"
            )

        return cls.READER_MAPPING[file_extension]