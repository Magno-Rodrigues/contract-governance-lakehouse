from src.bronze.readers.file.csv_reader import CSVReader
from src.bronze.readers.file.excel_reader import ExcelReader
from src.bronze.readers.file.xlsb_reader import XLSBReader


class ReaderRegistry:
    """
    Registry responsável por resolver readers de acordo com o source_type.
    """

    READER_MAPPING = {
        "csv": CSVReader,
        "xlsx": ExcelReader,
        "xlsb": XLSBReader,
        "json": None,
        "parquet": None,
        "api": None,
        "postgres": None,
        "oracle": None,
        "sap": None,
        "sftp": None,
    }

    @classmethod
    def get_reader(cls, source_type: str):
        """
        Resolve reader apropriado para o source_type informado.
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