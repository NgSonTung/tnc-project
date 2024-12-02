from gevent import monkey
monkey.patch_all()
from src.constants.http_status_codes import HTTP_401_UNAUTHORIZED
from src.database.chromadb import ChromaClient
from src.database.sqlite import SQLiteConnection
from flask_cors import CORS
from flask_jwt_extended import JWTManager
import src.database.mongodb as mongo
from src.routes import (
    live_demo,
    auth,
    demo_auth,
    demo_context_base,
    plug,
    payment,
    admin_context_base,
    admin_subscription,
    admin_plug, admin_user,
    context_base,
    image,
    subscription,
    socketio,
    user,
    client,
    history,
    guest,
    message,
    websocket
)
from flask import Flask
import nomic


def create_app(test_cofig=None):

    app = Flask(__name__)
    if test_cofig is None:
        app.config.from_pyfile('config/config.py')
    else:
        app.config.from_mapping(test_cofig)

    # Create Chroma client
    chroma_client = ChromaClient()
    # Store the Chroma client in the Flask application context
    app.config['CHROMA_CLIENT'] = chroma_client

    # Create SQLite connection
    sqlite_connection = SQLiteConnection()
    # Store the Chroma client in the Flask application context
    app.config['SQLITE_CONNECTION'] = sqlite_connection
    nomic.login(app.config["NOMIC_API_KEY"])
    mongo.create_db_connection()

    CORS(app, resources={
        r"/*": {"origins": ["*"]}}, supports_credentials=True)
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

    app.register_blueprint(demo_context_base)
    app.register_blueprint(demo_auth)
    app.register_blueprint(auth)
    app.register_blueprint(plug)
    app.register_blueprint(payment)
    app.register_blueprint(context_base)
    app.register_blueprint(admin_plug)
    app.register_blueprint(admin_context_base)
    app.register_blueprint(admin_subscription)
    app.register_blueprint(subscription)
    app.register_blueprint(admin_user)
    app.register_blueprint(live_demo)
    app.register_blueprint(image)
    app.register_blueprint(user)
    app.register_blueprint(client)
    app.register_blueprint(history)
    app.register_blueprint(guest)
    app.register_blueprint(message)
    app.register_blueprint(websocket)

    socketio.init_app(app)

    return app
