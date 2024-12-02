import os
import re
from dotenv import load_dotenv
from sqlalchemy import create_engine
from llama_index import SQLDatabase

load_dotenv()
sqlite_path = os.environ.get('SQLITE_DB_PATH')


class SQLiteConnection:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            if not os.path.exists(sqlite_path):
                os.makedirs(sqlite_path)
            engine = create_engine(
                f"sqlite:///{sqlite_path}/structured.sqlite3")
            cls._instance = SQLDatabase(engine)
        return cls._instance

    @staticmethod
    def format_table_name(name):
        file_name_without_extension, file_extension = os.path.splitext(name)
        # Remove special characters
        formatted_file_name = re.sub(
            r'[^a-zA-Z0-9 ]', '', file_name_without_extension)
        # Lowercase and replace spaces with underscores
        formatted_file_name = re.sub(
            r'\s+', '_', formatted_file_name.lower())
        return formatted_file_name
