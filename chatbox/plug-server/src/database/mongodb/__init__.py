import os
from mongoengine import connect
from dotenv import load_dotenv
load_dotenv()


def create_db_connection():
    db_host = "localhost"
    db_port = 27017
    db_name = os.environ.get("DB_NAME")

    # Establish the database connection
    connect(db=db_name, host=db_host, port=db_port)
