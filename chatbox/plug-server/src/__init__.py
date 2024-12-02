from werkzeug.middleware.proxy_fix import ProxyFix
from flask import Flask
from src.routes import plug_chat, client_chat, auth
import src.database.mongodb as mongo
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from src.database.chromadb import ChromaClient
from src.constants.http_status_codes import HTTP_401_UNAUTHORIZED
from src.database.sqlite import SQLiteConnection
import nomic


def create_app(test_cofig=None):

    app = Flask(__name__)

    if test_cofig is None:
        app.config.from_pyfile('config/config.py')
    else:
        app.config.from_mapping(test_cofig)

    # Create Chroma client
    chroma_client = ChromaClient()

    # Create SQLite connection
    sqlite_connection = SQLiteConnection()
    # Store the Chroma client in the Flask application context
    app.config['SQLITE_CONNECTION'] = sqlite_connection

    # Store the Chroma client in the Flask application context
    app.config['CHROMA_CLIENT'] = chroma_client

    mongo.create_db_connection()
    nomic.login(app.config["NOMIC_API_KEY"])

    CORS(app, resources={r"/*": {"origins": ["http://100.24.32.199", "http://localhost:4200",
         "http://127.0.0.1:4200", "https://www.2gai.ai", "http://54.209.193.185:8001", "http://100.25.30.108:8001", "http://localhost:63342", "*"]}}, supports_credentials=True)
    jwt = JWTManager(app)

    @jwt.expired_token_loader
    def my_expired_token_callback(jwt_header, jwt_payload):
        return {"code": 401, "message": str(jwt_payload)}, HTTP_401_UNAUTHORIZED

    @jwt.invalid_token_loader
    def my_invalid_token_callback(jwt_header, jwt_payload):
        return {"code": 401, "message": str(jwt_payload)}, HTTP_401_UNAUTHORIZED

    @jwt.unauthorized_loader
    def my_unauthorized_loader(jwt_payload):
        return {"code": 401, "message": str(jwt_payload)}, HTTP_401_UNAUTHORIZED

    @jwt.revoked_token_loader
    def handle_revoked_token(jwt_header, jwt_payload):
        return {"code": 401, "message": str(jwt_payload)}, HTTP_401_UNAUTHORIZED

    app.register_blueprint(plug_chat)
    app.register_blueprint(client_chat)
    app.register_blueprint(auth)
    app.wsgi_app = ProxyFix(
        app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1
    )

    return app
