from src.bronze.readers.file.csv_reader import CSVReader


class ReaderRegistry:
    """
    Registry responsável por resolver
    Readers de acordo com o source_type.

    Registry NÃO faz descoberta.

    Apenas resolve implementação.
    """

    READER_MAPPING = {
        "csv": CSVReader,

        # futuro
        "xlsx": None,
        "xlsb": None,
        "json": None,
        "parquet": None,

        "api": None,
        "postgres": None,
        "oracle": None,
        "sap": None,
        "sftp": None
    }

    @classmethod
    def get_reader(
        cls,
        source_type: str
    ):
        """
        Resolve reader apropriado.
        """

        if source_type not in cls.READER_MAPPING:
            raise ValueError(
                f"Reader não encontrado para: {source_type}"
            )

        reader_class = cls.READER_MAPPING[source_type]

        if reader_class is None:
            raise NotImplementedError(
                f"Reader {source_type} ainda não implementado."
            )

        return reader_class