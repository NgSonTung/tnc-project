from flask import Blueprint, request, current_app, Response
from src.models import User, Plug
from src.constants.http_status_codes import (
    HTTP_200_OK, HTTP_404_NOT_FOUND, HTTP_500_INTERNAL_SERVER_ERROR, HTTP_400_BAD_REQUEST, HTTP_401_UNAUTHORIZED
)
import datetime
import os
from werkzeug.security import check_password_hash, generate_password_hash
from flask_jwt_extended import jwt_required, create_access_token, create_refresh_token, get_jwt_identity, decode_token
from jwt import decode
import validators
from src.config.config import URL_PATH
from datetime import timedelta, datetime

auth = Blueprint("auth", __name__, url_prefix=f"{URL_PATH}/plug/api/v1/auth")
flask_env = os.environ.get("FLASK_ENV")


@auth.post("/login")
def login():
    try:
        if not request.is_json:
            return {"code": 400, "message": "Invalid JSON data"}, HTTP_400_BAD_REQUEST

        email = request.json.get("email", "")
        password = request.json.get("password", "")
        client_key = request.json.get("clientKey", "")

        if not client_key:
            return {"code": 400, "message": "Invalid client key"}, HTTP_200_OK
        plug = Plug.objects(client__key=client_key).first()
        if not plug:
            return {"code": 404, "message": "Plug not found"}, HTTP_404_NOT_FOUND
        if len(password) == 0 or password is None or len(email) == 0 or email is None:
            return {"code": 401, "message": "Invalid data"}, HTTP_401_UNAUTHORIZED

        user = User.objects(email=email).first()

        if user:
            is_correct_password = check_password_hash(user.password, password)
            if is_correct_password:
                refresh_token = create_refresh_token(identity=str(user.id))
                access_token = create_access_token(identity=str(user.id))

                current_datetime = datetime.utcnow()
                access_expire_time = current_datetime + \
                    current_app.config['JWT_ACCESS_TOKEN_EXPIRES']
                refresh_expire_time = current_datetime + \
                    current_app.config['JWT_REFRESH_TOKEN_EXPIRES']

                token_payload = {
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                    "access_expire_time": access_expire_time
                }
                return {"code": 200, "message": "Logged in successfully",
                        "data": token_payload}, HTTP_200_OK

            return {"code": 401, "message": "Email or password is incorrect"}, HTTP_401_UNAUTHORIZED
        return {"code": 404, "message": "User not found"}, HTTP_404_NOT_FOUND
    except Exception as e:
        return {"code": 401, "message": f"Failed to login error : {str(e)}"}, HTTP_500_INTERNAL_SERVER_ERROR


@auth.get("token/refresh")
def rftk():
    try:
        if not request.headers.get("refresh_token"):
            return {"code": 401, "message": "Invalid refresh_token"}, HTTP_401_UNAUTHORIZED
        decoded = decode_token(request.headers.get("refresh_token"))
        if decoded is None:
            return {"code": 401, "message": "Invalid refresh_token"}, HTTP_401_UNAUTHORIZED
        if datetime.fromtimestamp(decoded['exp']) < datetime.utcnow():
            return {"code": 401, "message": "Refresh token was expired"}, HTTP_401_UNAUTHORIZED
        new_token = create_access_token(identity=str(decoded['sub']))
        access_expire_time = datetime.utcnow(
        ) + current_app.config['JWT_ACCESS_TOKEN_EXPIRES']
        return {"code": 200, "message": "Refresh token successfully",
                "data": {
                    "access_token": new_token,
                    "access_expire_time": access_expire_time
                }}, HTTP_200_OK
    except Exception as e:
        return {"code": 401, "message": f"Failed to refresh token error : {str(e)}"}, HTTP_500_INTERNAL_SERVER_ERROR
