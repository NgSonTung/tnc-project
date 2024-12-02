import os
import requests
from flask import Blueprint, request, make_response, current_app, redirect
from werkzeug.security import check_password_hash, generate_password_hash
from flask_jwt_extended import jwt_required, create_access_token, create_refresh_token, get_jwt_identity, \
    set_access_cookies, set_refresh_cookies, unset_jwt_cookies, get_jwt, decode_token
from jwt import decode
import validators
from datetime import timedelta, datetime
from src.constants.http_status_codes import HTTP_200_OK, HTTP_200_OK, HTTP_200_OK, HTTP_500_INTERNAL_SERVER_ERROR, \
    HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND
from src.models import User, Plug
from src.config.config import JWT_SECRET_KEY, URL_PATH
from src.helper.smtp_mail import send_mail_smtp

from src.template.mail_template import (
    main_mail_template, main_mail_template_non_button)

auth = Blueprint("auth", __name__, url_prefix=f"{URL_PATH}/web/api/v1/auth")

FLASK_ENV = os.environ.get("FLASK_ENV")
WEBSITE_URL = os.getenv('URL_API_FE')


@auth.post("/register")
def register():
    try:
        if not request.is_json:
            return {"code": 400, "message": "Invalid JSON data"}, HTTP_400_BAD_REQUEST

        userName = request.json.get("userName", "")
        email = request.json.get("email", "")
        password = request.json.get("password", "")
        callback = request.json.get("callback", "")
        email = email.encode("ascii", "ignore").decode()
        user_id = request.json.get("userId", None)

        # Validations
        if len(password) == 0 or password is None or len(userName) == 0 or userName is None or len(
                email) == 0 or email is None:
            return {"code": 400, "message": "Invalid data"}, HTTP_400_BAD_REQUEST

        if len(password) < 6:
            return {"code": 400, "message": "Password is too short"}, HTTP_400_BAD_REQUEST

        if len(userName) < 3:
            return {"code": 400, "message": "Username is too short"}, HTTP_400_BAD_REQUEST

        if len(userName) > 20:
            return {"code": 400, "message": "Username is too long"}, HTTP_400_BAD_REQUEST

        if not userName.isalnum() or " " in userName:
            return {"code": 400, "message": "Username should be alphanumeric and no spaces"}, HTTP_400_BAD_REQUEST

        if not validators.email(email):
            return {"code": 400, "message": "Email is not valid"}, HTTP_400_BAD_REQUEST
        old_user: User = User.objects(email=email).first()
        if User.objects(email=email).first() is not None:
            if not old_user.liveDemo:
                return {"code": 400, "message": "Email is taken"}, HTTP_400_BAD_REQUEST

        if User.objects(userName=userName).first() is not None:
            return {"code": 400, "message": "Username is taken"}, HTTP_400_BAD_REQUEST

        receiver_email = f"{email}"
        # create token for verify email
        tokenPayload = {
            "userName": userName,
            "email": email,
            "password": password,
            "callback": callback
        }
        if user_id:
            tokenPayload["user_id"] = user_id
        expires_in = timedelta(minutes=5)
        token_verify_email = create_access_token(
            identity=tokenPayload, expires_delta=expires_in)
        # create message
        subject = "Verify Email"

        title = f"Click on the button below to verify your email address."
        ps = "If this email was not intend for you feel free to delete it."
        url_verify_email = current_app.config['BASE_URL'] + \
            "auth/register/verify_email/?token="
        print(current_app.config['BASE_URL'] +
              "auth/register/verify_email/?token=")
        html_content = main_mail_template(
            subject, f"Thank you for signing up, {userName}!", title, "", url_verify_email +
            token_verify_email,
            "Verify Email", ps)
        send_mail_smtp(receiver_email, subject,
                       html_content.replace('\u200b', ''))

        return {"code": 200, "message": "A verification email has been sent"}, HTTP_200_OK
    except Exception as e:
        return {"code": 500, "message": str(e)}, HTTP_500_INTERNAL_SERVER_ERROR


@auth.get("/register/verify_email/")
def verify_email():
    try:
        query_params = request.args.get("token")
        if query_params is None:
            return {"code": 400, "message": "Token missing in query parameters"}, HTTP_400_BAD_REQUEST

        decoded_token = decode(
            query_params, JWT_SECRET_KEY, algorithms=["HS256"])

        expiration_time = decoded_token.get("exp")
        current_time = datetime.utcnow()

        if expiration_time is None or expiration_time < current_time.timestamp():
            return {"code": 400, "message": "Token has expired"}, HTTP_400_BAD_REQUEST
        data_user_decode = decoded_token.get("sub")

        user_name = data_user_decode.get("userName")
        email = data_user_decode.get("email")
        password = data_user_decode.get("password")
        callback = data_user_decode.get("callback")
        user_id = data_user_decode.get("user_id", None)
        password_hash = generate_password_hash(password)
        if user_id:
            user: User = User.objects(id=user_id).first()
            user.userName = user_name
            user.email = email
            password_hash = generate_password_hash(password)
            user.password = password_hash
            user.trial = False
            user.save()
        else:
            user: User = User.objects(email=email).first()
            if user:
                if user.liveDemo:
                    # return redirect(callback+query_params)
                    Plug.objects(userId=user.id).delete()
                    user.delete()
                else:
                    return redirect(callback)

            user = User(
                userName=user_name,
                email=email,
                password=password_hash,
            ).save()
        if user:
            subject = "Sign up success"

            content = f"You have successfully created your WebAI Pilot account with the following email address: <b>{email}<b>"
            ps = "If you have any question or comments just email admin@2gai.ai. We would love to hear from you!"
            html_content = main_mail_template_non_button(
                subject, f"Welcome {user.userName}!", "", content, ps)

            send_mail_smtp(user.email, subject, html_content)
        # return the redirect
        response = make_response(redirect(callback))
        unset_jwt_cookies(response)
        return response

    except Exception as e:
        return {"code": 500, "message": str(e)}, HTTP_500_INTERNAL_SERVER_ERROR


@auth.post("/login/reset_password")
def reset_password():
    try:
        if not request.is_json:
            return {"code": 400, "message": "Invalid JSON data"}, HTTP_400_BAD_REQUEST

        email = request.json.get("email", "")
        callback = request.json.get("callback", "")
        if len(email) == 0 or email is None:
            return {"code": 400, "message": "Invalid data"}, HTTP_400_BAD_REQUEST

        if not validators.email(email):
            return {"code": 400, "message": "Email is not valid"}, HTTP_400_BAD_REQUEST

        user: User = User.objects(email=email).first()

        if not user:
            return {"code": 400, "message": "User not found"}, HTTP_400_BAD_REQUEST

        # create token for verify email
        token_payload = {"userName": user.userName, "email": user.email}
        expires_in = timedelta(minutes=5)
        token_forgot_password = create_access_token(
            identity=token_payload, expires_delta=expires_in)
        # create message
        subject = "Reset Password"
        receiver_email = f"{email}"
        # in this part add the link to redirect to the reset password page
        # example: {base_url}/resetPassword?token={tokenForgotPassword}
        title = "A request has been received to change the password for your 2GAI account."
        content = "If it wasn’t you please disregard this email and make sure you can still login to your account. If it was you, then confirm the password change"
        ps = "If you did not initiate this request, please contact us immediately at admin@2ai.ai"

        html_content = main_mail_template(
            subject, f"Hello {user.userName},", title, content, callback + token_forgot_password, "Reset Password", ps)

        send_mail_smtp(receiver_email, subject, html_content)
        return {"code": 200, "message": "A restore email has been sent"}, HTTP_200_OK

    except Exception as e:
        return {"code": 500, "message": str(e)}, HTTP_500_INTERNAL_SERVER_ERROR


@auth.post("/login/reset_password/")
def handle_reset_password():
    try:
        request_data = request.get_json()

        if not request_data:
            return {"code": 400, "message": "Invalid JSON data"}, HTTP_400_BAD_REQUEST

        # validate new password and confirm new password
        new_password = request_data.get("newPassword", "")
        confirm_new_password = request_data.get("confirmNewPassword", "")

        if len(new_password) == 0 or new_password is None or len(
                confirm_new_password) == 0 or confirm_new_password is None:
            return {"code": 400, "message": "Invalid data"}, HTTP_400_BAD_REQUEST

        if new_password != confirm_new_password:
            return {"code": 400, "message": "Password don't match"}, HTTP_400_BAD_REQUEST

        # validate token
        token_reset_password = request.args.get('token')

        if token_reset_password is None:
            return {"code": 400, "message": "Token missing in query parameters"}, HTTP_400_BAD_REQUEST

        decoded_token = decode(token_reset_password,
                               JWT_SECRET_KEY, algorithms=["HS256"])
        expiration_time = decoded_token.get("exp")
        current_time = datetime.utcnow()

        if expiration_time is None or expiration_time < current_time.timestamp():
            return {"code": 400, "message": "Token has expired"}, HTTP_400_BAD_REQUEST

        data_user_decode = decoded_token.get("sub")
        email = data_user_decode.get("email")
        user: User = User.objects(email=email).first()

        if not user:
            return {"code": 400, "message": "User not found"}, HTTP_400_BAD_REQUEST

        user.password = generate_password_hash(new_password)
        user.save()
        response = make_response(
            {"code": 200, "message": "Reset password susscessfully"}, HTTP_200_OK)
        unset_jwt_cookies(response)

        return response

    except Exception as e:
        return {"code": 500, "message": str(e)}, HTTP_500_INTERNAL_SERVER_ERROR


@auth.post("/login/change_password")
@jwt_required()
def change_password():
    try:
        user_id = get_jwt_identity()
        user: User = User.objects(id=user_id).first()
        if not user:
            return {"code": 400, "message": "User not found"}, HTTP_400_BAD_REQUEST

        request_data = request.get_json()
        if request_data is None:
            return {"code": 400, "message": "Invalid JSON data"}, HTTP_400_BAD_REQUEST

        new_password = request_data.get("newPassword", "")
        old_password = request_data.get("oldPassword", "")
        confirm_new_password = request_data.get("confirmNewPassword", "")
        if len(new_password) == 0 or new_password is None or len(
                confirm_new_password) == 0 or confirm_new_password is None:
            return {"code": 400, "message": "Invalid data"}, HTTP_400_BAD_REQUEST
        if new_password != confirm_new_password:
            return {"code": 400, "message": "Password don't match"}, HTTP_400_BAD_REQUEST
        if len(old_password) == 0 or old_password is None:
            return {"code": 400, "message": "Invalid data"}, HTTP_400_BAD_REQUEST
        if old_password == new_password:
            return {"code": 400, "message": "New password can't be the same as old password"}, HTTP_400_BAD_REQUEST
        if check_password_hash(user.password, old_password) == False:
            return {"code": 400, "message": "Old password is incorrect"}, HTTP_400_BAD_REQUEST

        if not user:
            return {"code": 400, "message": "User not found"}, HTTP_400_BAD_REQUEST
        user.password = generate_password_hash(new_password)
        user.save()

        response = make_response(
            {"code": 200, "message": "Change password susscessfully"}, HTTP_200_OK)
        unset_jwt_cookies(response)
        return response
    except Exception as e:
        return {"code": 500, "message": str(e)}, HTTP_500_INTERNAL_SERVER_ERROR


@auth.get("/login/change_password/")
def handle_change_password():
    try:
        token_change_password = request.args.get('token')

        if token_change_password is None:
            return {"code": 400, "message": "Invalid JSON data"}, HTTP_400_BAD_REQUEST

        decoded_token = decode(token_change_password,
                               JWT_SECRET_KEY, algorithms=["HS256"])
        expiration_time = decoded_token.get("exp")
        current_time = datetime.utcnow()

        if expiration_time is None or expiration_time < current_time.timestamp():
            return {"code": 400, "message": "Token has expired"}, HTTP_400_BAD_REQUEST

        data_user_decode = decoded_token.get("sub")
        email = data_user_decode.get("email")
        new_password = data_user_decode.get("newPassword")
        user: User = User.objects(email=email).first()
        if not user:
            return {"code": 400, "message": "User not found"}, HTTP_400_BAD_REQUEST
        user.password = new_password
        user.save()
        response = make_response(
            {"code": 200, "message": "Change password susscessfully"}, HTTP_200_OK)
        unset_jwt_cookies(response)
        return response
    except Exception as e:
        return {"code": 500, "message": str(e)}, HTTP_500_INTERNAL_SERVER_ERROR


@auth.post("/login")
def login():
    try:
        if not request.is_json:
            return {"code": 400, "message": "Invalid JSON data"}, HTTP_400_BAD_REQUEST

        email = request.json.get("email", "")
        password = request.json.get("password", "")

        if len(password) == 0 or password is None or len(email) == 0 or email is None:
            return {"code": 400, "message": "Invalid data"}, HTTP_400_BAD_REQUEST

        user: User = User.objects(email=email).first()

        if user:
            is_correct_password = check_password_hash(user.password, password)
            user_json = user.to_json()
            if is_correct_password:
                refresh_token = create_refresh_token(identity=str(user.id))
                access_token = create_access_token(identity=str(user.id))

                current_datetime = datetime.utcnow()
                access_expire_time = current_datetime + \
                    current_app.config['JWT_ACCESS_TOKEN_EXPIRES']
                refresh_expire_time = current_datetime + \
                    current_app.config['JWT_REFRESH_TOKEN_EXPIRES']

                user_json["accessExpireTime"] = access_expire_time
                user_json["refreshExpireTime"] = refresh_expire_time

                response = make_response(
                    {"code": 200, "message": "Logged in successfully", "data": user_json}, HTTP_200_OK)

                set_access_cookies(
                    response, access_token, max_age=current_app.config['JWT_ACCESS_TOKEN_EXPIRES'].total_seconds())
                set_refresh_cookies(
                    response, refresh_token, max_age=current_app.config['JWT_REFRESH_TOKEN_EXPIRES'].total_seconds())

                return response

            return {"code": 400, "message": "Email or password is incorrect"}, HTTP_400_BAD_REQUEST
        return {"code": 404, "message": "User not found"}, HTTP_404_NOT_FOUND

    except Exception as e:
        return {"code": 500, "message": f"Failed to login error : {str(e)}"}, HTTP_500_INTERNAL_SERVER_ERROR


@auth.get("/login/")
def login_by_token(token=None):
    try:
        if token is None:
            token = request.args.get('token')

        if not token:
            return {"code": 400, "message": "Invalid token"}, HTTP_400_BAD_REQUEST

        decoded_token = decode(
            token, current_app.config['JWT_SECRET_KEY'], algorithms=["HS256"])
        data_decoded = decoded_token.get("sub")

        email = data_decoded.get("email", "")

        password = data_decoded.get("password", "")

        if len(password) == 0 or password is None or len(email) == 0 or email is None:
            return {"code": 400, "message": "Invalid data"}, HTTP_400_BAD_REQUEST

        user: User = User.objects(email=email).first()
        if user:

            is_correct_password = check_password_hash(user.password, password)

            if is_correct_password:
                user_json = user.to_json()

                refresh_token = create_refresh_token(identity=str(user.id))
                access_token = create_access_token(identity=str(user.id))

                current_datetime = datetime.utcnow()
                access_expire_time = current_datetime + \
                    current_app.config['JWT_ACCESS_TOKEN_EXPIRES']
                refresh_expire_time = current_datetime + \
                    current_app.config['JWT_REFRESH_TOKEN_EXPIRES']

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


@auth.get("/logout")
@jwt_required()
def logout():
    try:
        response = make_response(
            {"code": 200, "message": "Logged out successfully"}, HTTP_200_OK)
        unset_jwt_cookies(response)

        return response

    except Exception as e:
        return {"code": 500, "message": f"Failed to logout error : {str(e)}"}, HTTP_500_INTERNAL_SERVER_ERROR


@auth.get("/me")
@jwt_required()
def me():
    try:
        user_id = get_jwt_identity()
        user: User = User.objects(id=user_id).first()

        if not user:
            return {"code": 400, "message": "User not found"}, HTTP_400_BAD_REQUEST
        return {"code": 200, "message": "User retrieved successfully", "data": user.to_json()}, HTTP_200_OK

    except Exception as e:
        return {"code": 500, "message": f"Failed to retrieve user error : {str(e)}"}, HTTP_500_INTERNAL_SERVER_ERROR


@auth.get("/cookie_expire")
@jwt_required()
def cookie_expire():
    try:
        refresh_token = request.cookies.get('refresh_token_cookie')
        decoded_token = decode_token(refresh_token)
        refresh_exp_time = decoded_token['exp']
        refresh_exp_datetime = datetime.utcfromtimestamp(refresh_exp_time)

        access_exp_time = get_jwt()["exp"]
        access_exp_datetime = datetime.utcfromtimestamp(access_exp_time)
        return {"code": 200, "message": "Cookie expiration retrieved successfully",
                "data": {"accessExpireTime": access_exp_datetime,
                         "refreshExpireTime": refresh_exp_datetime}}, HTTP_200_OK
    except Exception as e:
        return {"code": 500,
                "message": f"Failed to retrieve cookie expiration : {str(e)}"}, HTTP_500_INTERNAL_SERVER_ERROR


@auth.get("/token/refresh")
@jwt_required(refresh=True)
def refresh_users_token():
    try:
        user_id = get_jwt_identity()
        access_token = create_access_token(identity=str(user_id))

        current_datetime = datetime.utcnow()
        access_expire_time = current_datetime + \
            current_app.config['JWT_ACCESS_TOKEN_EXPIRES']
        refresh_expire_time = current_datetime + \
            current_app.config['JWT_REFRESH_TOKEN_EXPIRES']

        data = {'accessExpireTime': access_expire_time,
                'refreshExpireTime': refresh_expire_time}

        response = make_response(
            {"code": 200, "message": "Token refreshed successfully", "data": data}, HTTP_200_OK)

        set_access_cookies(
            response, access_token, max_age=current_app.config['JWT_ACCESS_TOKEN_EXPIRES'].total_seconds())

        return response

    except Exception as e:
        return {"code": 500, "message": f"Failed to refresh token error : {str(e)}"}, HTTP_500_INTERNAL_SERVER_ERROR


@auth.get("hello")
def hello():
    return {"code": 200, "message": os.environ.get("HELLO")}, HTTP_200_OK


@auth.get("/subscription")
def get_subscription_status():
    try:
        user_id = request.args.get("userId")
        user: User = User.objects(id=user_id).first()
        company_plan_ids = ['64aff45ae43f3103d2fa22e2',
                            '64aff45ae43f3103d2fa22e3']
        if not user:
            return "User does not exist", HTTP_404_NOT_FOUND
        return {'isCompany': str(user.subscriptionId) in company_plan_ids}, HTTP_200_OK

    except Exception as e:
        return f"Failed to retrieve subscription status : {str(e)}", HTTP_500_INTERNAL_SERVER_ERROR


@auth.post("/token")
def login_token():
    try:
        if not request.is_json:
            return {"code": 400, "message": "Invalid JSON data"}, HTTP_400_BAD_REQUEST

        email = request.json.get("email", "")
        password = request.json.get("password", "")

        if len(password) == 0 or password is None or len(email) == 0 or email is None:
            return {"code": 400, "message": "Invalid data"}, HTTP_400_BAD_REQUEST

        user: User = User.objects(email=email).first()

        if user:
            is_correct_password = check_password_hash(user.password, password)
            user_json = user.to_json()
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
                    "access_expire_time": access_expire_time,
                    "refresh_expire_time": refresh_expire_time
                }
                return {"code": 200, "message": "Logged in successfully",
                        "data": {"tokenPayload": token_payload,
                                 "userInfo": user_json}}, HTTP_200_OK

            return {"code": 400, "message": "Email or password is incorrect"}, HTTP_400_BAD_REQUEST
        return {"code": 404, "message": "User not found"}, HTTP_404_NOT_FOUND
    except Exception as e:
        return {"code": 500, "message": f"Failed to login error : {str(e)}"}, HTTP_500_INTERNAL_SERVER_ERROR


@auth.post("/docker/login")
def docker_login():
    # try:
    # if FLASK_ENV != "docker":
    #     return {"code": 400, "message": "Invalid FLASK_ENV"}, HTTP_400_BAD_REQUEST
    if not request.is_json:
        return {"code": 400, "message": "Invalid JSON data"}, HTTP_400_BAD_REQUEST
    print(f"{current_app.config['BASE_URL_DOCKER']}/auth/login")
    res = requests.post(f"{WEBSITE_URL}/stage/web/api/v1/auth/token", json=request.get_json(),
                        headers=request.headers)

    token_payload = res.json()

    response = make_response(
        res.json(), HTTP_200_OK)

    # set_access_cookies(
    #     response, res.headers.access_token_cookie, max_age=current_app.config['JWT_ACCESS_TOKEN_EXPIRES'].total_seconds())
    # set_refresh_cookies(
    #     response, res.headers.refresh_token_cookie, max_age=current_app.config['JWT_REFRESH_TOKEN_EXPIRES'].total_seconds())
    return response
# except Exception as e:
#     return {"code": 500, "message": f"Failed to login error : {str(e)}"}, HTTP_500_INTERNAL_SERVER_ERROR
