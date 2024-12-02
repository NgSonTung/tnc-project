import os
from flask import Blueprint, request, make_response, current_app
from werkzeug.security import check_password_hash, generate_password_hash
from flask_jwt_extended import create_access_token, create_refresh_token, set_access_cookies, set_refresh_cookies
from jwt import decode
from datetime import timedelta, datetime
from src.constants.http_status_codes import HTTP_200_OK, HTTP_200_OK, HTTP_200_OK, HTTP_500_INTERNAL_SERVER_ERROR, \
    HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND
from src.models import User, Plug, Subscription, Client
from src.config.config import URL_PATH
from src.helper.uuid import generate_uuid
from bson import ObjectId

demo_auth = Blueprint("demo_auth", __name__,
                      url_prefix=f"{URL_PATH}/web/api/v1/demo/auth")

FLASK_ENV = os.environ.get("FLASK_ENV")


@demo_auth.post("/login")
def login():
    try:
        token = request.headers.get('Authorization')

        if not token:
            # create user
            user_name = generate_uuid(10)
            email = f"{generate_uuid(10)}@gmail.com"
            password = generate_uuid(10)
            password_hash = generate_password_hash(password)

            user: User = User(
                userName=user_name,
                email=email,
                password=password_hash,
                trial=True
            ).save()

            token_payload = {
                "email": email,
                "password": password
            }

            session_token = create_access_token(
                identity=token_payload, expires_delta=timedelta(days=7))

            user_json = user.to_json()

            access_token = create_access_token(identity=str(
                user.id), expires_delta=timedelta(days=1))
            refresh_token = create_refresh_token(
                identity=str(user.id), expires_delta=timedelta(days=7))

            current_datetime = datetime.utcnow()
            access_expire_time = current_datetime + timedelta(days=1)
            refresh_expire_time = current_datetime + timedelta(days=7)

            user_json["accessExpireTime"] = access_expire_time
            user_json["refreshExpireTime"] = refresh_expire_time
            user_json["token"] = session_token

            # Create plug
            plug_name = "Plug 1"

            subscription: Subscription = Subscription.objects(
                id=ObjectId(user.subscriptionId)).first()
            features = subscription.features

            Plug(features=features, model='gpt-4',
                 plugName=plug_name, userId=user.id, userKey=None, client=Client()).save()
            response = make_response(
                {"code": 200, "message": "Logged in successfully", "data": user_json}, HTTP_200_OK)

            set_access_cookies(
                response, access_token, max_age=timedelta(days=1))
            set_refresh_cookies(
                response, refresh_token, max_age=timedelta(days=7))

            return response, HTTP_200_OK
        else:
            token = token.split('Bearer ')[1]

            decoded_token = decode(
                token, current_app.config['JWT_SECRET_KEY'], algorithms=["HS256"])
            data_decoded = decoded_token.get("sub")

            email = data_decoded.get("email", "")

            password = data_decoded.get("password", "")

            if len(password) == 0 or password is None or len(email) == 0 or email is None:
                return {"code": 400, "message": "Invalid data"}, HTTP_400_BAD_REQUEST

            user: User = User.objects(email=email).first()
            if user:

                is_correct_password = check_password_hash(
                    user.password, password)

                if is_correct_password:
                    user_json = user.to_json()

                    access_token = create_access_token(identity=str(
                        user.id), expires_delta=timedelta(days=1))
                    refresh_token = create_refresh_token(
                        identity=str(user.id), expires_delta=timedelta(days=7))

                    current_datetime = datetime.utcnow()
                    access_expire_time = current_datetime + timedelta(days=1)
                    refresh_expire_time = current_datetime + timedelta(days=7)

                    user_json["accessExpireTime"] = access_expire_time
                    user_json["refreshExpireTime"] = refresh_expire_time

                    response = make_response(
                        {"code": 200, "message": "Logged in successfully", "data": user_json}, HTTP_200_OK)

                    set_access_cookies(
                        response, access_token, max_age=current_app.config['JWT_ACCESS_TOKEN_EXPIRES'].total_seconds())
                    set_refresh_cookies(
                        response, refresh_token, max_age=current_app.config['JWT_REFRESH_TOKEN_EXPIRES'].total_seconds())

                    return response, HTTP_200_OK

                return {"code": 400, "message": "Email or password is incorrect"}, HTTP_400_BAD_REQUEST
            return {"code": 404, "message": "User not found"}, HTTP_404_NOT_FOUND

    except Exception as e:
        return {"code": 500, "message": f"Failed to login error : {str(e)}"}, HTTP_500_INTERNAL_SERVER_ERROR
