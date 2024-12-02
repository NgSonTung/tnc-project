import os
import chromadb
from dotenv import load_dotenv

load_dotenv()


class ChromaClient:
    _instance = None

    def __new__(cls):
        flask_env = os.environ.get("FLASK_ENV")
        if flask_env == "development":
            if cls._instance is None:
                if os.environ.get("CHROMA_URL_DOCKER") == "your_chromadb_url":
                    cls._instance = chromadb.PersistentClient(
                        path=os.environ.get('CHROMA_DB_PATH'))
                else:
                    cls._instance = chromadb.HttpClient(
                        host=os.environ["CHROMA_URL_DOCKER"], port=os.environ["CHROMA_PORT"])
            return cls._instance
        elif flask_env == "production":
            if cls._instance is None:
                cls._instance = chromadb.HttpClient(
                    host=os.environ["CHROMA_URL"], port=os.environ["CHROMA_PORT"])
            return cls._instance
        elif flask_env == "staging":
            if cls._instance is None:
                cls._instance = chromadb.HttpClient(
                    host=os.environ["CHROMA_URL_STAGING"], port=os.environ["CHROMA_PORT"])
            return cls._instance
        elif flask_env == "docker" and os.environ["CHROMA_URL_DOCKER"] != "your_chromadb_url":
            if cls._instance is None:
                cls._instance = chromadb.HttpClient(
                    host=os.environ["CHROMA_URL_DOCKER"], port=os.environ["CHROMA_PORT"])
            return cls._instance
        elif flask_env == "docker" and os.environ["CHROMA_URL_DOCKER"] == "your_chromadb_url":
            if cls._instance is None:
                cls._instance = chromadb.PersistentClient(
                    path=os.environ.get('CHROMA_DB_PATH'))
            return cls._instance
