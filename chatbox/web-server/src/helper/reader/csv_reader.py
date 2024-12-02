"""Tabular parser.

Contains parsers for tabular data files.

"""
from typing import Any, Dict, List, Optional
from llama_index.readers.base import BaseReader
from llama_index.schema import Document
from src.routes.ws import progressUpdate

import pandas as pd
import io


class CSVReader(BaseReader):
    """CSV parser.

    Args:
        concat_rows (bool): whether to concatenate all rows into one document.
            If set to False, a Document will be created for each row.
            True by default.

    """

    def __init__(self, *args: Any, concat_rows: bool = True, **kwargs: Any) -> None:
        """Init params."""
        super().__init__(*args, **kwargs)
        self._concat_rows = concat_rows

    def load_data(
        self, file, extra_info: Optional[Dict] = None, context_item=None, room=None
    ):
        """Parse file.

        Returns:
            Union[str, List[str]]: a string or a List of strings.

        """
        try:
            import csv
        except ImportError:
            raise ImportError("csv module is required to read CSV files.")
        file_data = file.read()
        decoded_data = file_data.decode('utf-8')

        # map to table
        fp = io.StringIO(decoded_data)
        df = pd.read_csv(fp, engine='python',
                         quoting=csv.QUOTE_MINIMAL, encoding='utf-8')

        if context_item:
            progressUpdate(context_item=context_item.to_json(), progress=30,
                           is_file=True, message='', room=room)

        df.columns = df.columns.str.strip()

        # drop column index if exist
        if 'index' in df.columns:
            df.drop('index', axis=1, inplace=True)

        # drop null rows
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


class PandasCSVReader(BaseReader):
    r"""Pandas-based CSV parser.

    Parses CSVs using the separator detection from Pandas `read_csv`function.
    If special parameters are required, use the `pandas_config` dict.

    Args:
        concat_rows (bool): whether to concatenate all rows into one document.
            If set to False, a Document will be created for each row.
            True by default.

        col_joiner (str): Separator to use for joining cols per row.
            Set to ", " by default.

        row_joiner (str): Separator to use for joining each row.
            Only used when `concat_rows=True`.
            Set to "\n" by default.

        pandas_config (dict): Options for the `pandas.read_csv` function call.
            Refer to https://pandas.pydata.org/docs/reference/api/pandas.read_csv.html
            for more information.
            Set to empty dict by default, this means pandas will try to figure
            out the separators, table head, etc. on its own.

    """

    def __init__(
        self,
        *args: Any,
        concat_rows: bool = True,
        col_joiner: str = ", ",
        row_joiner: str = "\n",
        pandas_config: dict = {},
        **kwargs: Any
    ) -> None:
        """Init params."""
        super().__init__(*args, **kwargs)
        self._concat_rows = concat_rows
        self._col_joiner = col_joiner
        self._row_joiner = row_joiner
        self._pandas_config = pandas_config

    def load_data(
        self, file, extra_info: Optional[Dict] = None
    ) -> List[Document]:
        """Parse file."""
        import io
        file_data = file.read()
        fp = io.BytesIO(file_data)
        df = pd.read_csv(fp, **self._pandas_config)

        text_list = df.apply(
            lambda row: (self._col_joiner).join(row.astype(str).tolist()), axis=1
        ).tolist()

        if self._concat_rows:
            return [
                Document(
                    text=(self._row_joiner).join(text_list), metadata=extra_info or {}
                )
            ]
        else:
            return [
                Document(text=text, metadata=extra_info or {}) for text in text_list
            ]
