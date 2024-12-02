"""Pandas Excel reader.

Pandas parser for .xlsx files.

"""
from typing import Any, Dict, List, Optional, Union
from llama_index.readers.base import BaseReader
from llama_index.readers.schema.base import Document
from src.routes.ws import progressUpdate

import pandas as pd
import io


class PandasExcelReader(BaseReader):
    r"""Pandas-based CSV parser.

    Parses CSVs using the separator detection from Pandas `read_csv`function.
    If special parameters are required, use the `pandas_config` dict.

    Args:

        pandas_config (dict): Options for the `pandas.read_excel` function call.
            Refer to https://pandas.pydata.org/docs/reference/api/pandas.read_excel.html
            for more information. Set to empty dict by default, this means defaults will be used.

    """

    def __init__(
        self,
        *args: Any,
        pandas_config: Optional[dict] = None,
        concat_rows: bool = True,
        row_joiner: str = "\n",
        **kwargs: Any
    ) -> None:
        """Init params."""
        super().__init__(*args, **kwargs)
        self._pandas_config = pandas_config or {}
        self._concat_rows = concat_rows
        self._row_joiner = row_joiner if row_joiner else "\n"

    def load_data(
        self,
        file,
        include_sheetname: bool = True,
        sheet_name: Optional[Union[str, int, list]] = None,
        extra_info: Optional[Dict] = None,
        context_item=None,
        room=None
    ) -> List[Document]:
        """Parse file and extract values from a specific column.

        Args:
            file (Path): The path to the Excel file to read.
            include_sheetname (bool): Whether to include the sheet name in the output.
            sheet_name (Union[str, int, None]): The specific sheet to read from, default is None which reads all sheets.
            extra_info (Dict): Additional information to be added to the Document object.

        Returns:
            List[Document]: A list of`Document objects containing the values from the specified column in the Excel file.
        """

        # map to table
        fp = io.BufferedReader(file)

        df = pd.read_excel(fp)

        progressUpdate(context_item=context_item.to_json(),
                       progress=30, is_file=True, message='', room=room)

        # Strip column names
        df.columns = df.columns.str.strip()

        # Drop 'index' column if it exists
        if 'index' in df.columns:
            df.drop('index', axis=1, inplace=True)

        # Drop null rows
        df.dropna(axis=0, how='all', inplace=True)

        # Replace double quotes
        df.replace('"', '', regex=True, inplace=True)

        # Replace single quotes
        df.replace("'", '', regex=True, inplace=True)

        # Remove double quotes from header
        df.columns = df.columns.str.replace('"', '')

        # Remove single quotes from header
        df.columns = df.columns.str.replace("'", '')

        df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)

        column_names = df.columns.tolist()

        return df, column_names
