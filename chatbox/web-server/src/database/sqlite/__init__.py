import sqlite3
import os
import re
from dotenv import load_dotenv


load_dotenv()
sqlite_path = os.environ.get('SQLITE_DB_PATH')


class SQLiteConnection:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            if not os.path.exists(sqlite_path):
                os.makedirs(sqlite_path)
            cls._instance = sqlite3.connect(
                f'{sqlite_path}/structured.sqlite3')
        return cls._instance

    @staticmethod
    def delete_tables_sw(connection, starts_with):
        cursor = connection.cursor()
        try:
            cursor.execute("BEGIN TRANSACTION;")

            # Find matching tables
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name LIKE ?;", (f'{starts_with}%',))
            matching_tables = cursor.fetchall()
            print(matching_tables)
            # Delete matching tables
            for table in matching_tables:
                cursor.execute(f'DROP TABLE IF EXISTS "{table[0]}";')

            # Commit the transaction
            cursor.execute("COMMIT;")
        except Exception as e:
            cursor.execute("ROLLBACK;")

    @staticmethod
    def delete_tables_by_name(connection, name):
        cursor = connection.cursor()
        sanitized_name = name.replace('"', '""')
        try:
            cursor.execute("BEGIN TRANSACTION;")
            cursor.execute(f'DROP TABLE IF EXISTS "{sanitized_name}";')

            cursor.execute("COMMIT;")
        except Exception as e:
            cursor.execute("ROLLBACK;")

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
