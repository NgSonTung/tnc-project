import datetime
import uuid
from flask_jwt_extended import  create_access_token
from flask import Blueprint, request, current_app
from werkzeug.security import  generate_password_hash
from src.models import User, Plug
from src.constants.http_status_codes import (
    HTTP_200_OK, HTTP_400_BAD_REQUEST,
     HTTP_500_INTERNAL_SERVER_ERROR
)
from src.helper.smtp_mail import send_mail_smtp
from src.template.mail_template import (
    main_mail_template,
    main_mail_template_non_button
)
from datetime import timedelta
from src.config.config import LIVE_DEMO_APPROVER_MAIL, URL_PATH
from jwt import decode
import pytz

live_demo = Blueprint("live_demo", __name__,
                      url_prefix=f"{URL_PATH}/web/api/v1/live_demo")


@live_demo.get("/accept_request/")
def create_live_demo():
    try:
        token = request.args.get('token')
        if not token:
            return {"code": 400, "message": "Invalid token"}, HTTP_400_BAD_REQUEST
        decoded_token = decode(
            token, current_app.config['JWT_SECRET_KEY'], algorithms=["HS256"])

        data_decoded = decoded_token.get("sub")

        email = data_decoded.get("email", "")
        your_name = data_decoded.get("your_name", "")
        callback = data_decoded.get("callback", "")
        if not email:
            return {"code": 400, "message": "Invalid token"}, HTTP_400_BAD_REQUEST

        # generate username
        userName = ""
        while True:
            random_str = str(uuid.uuid4().hex)[:20]
            if random_str.isalnum() and ' ' not in random_str:
                userName = random_str
                break

        # generate password
        password = ""
        while True:
            random_str = str(uuid.uuid4().hex)[:20]
            if ' ' not in random_str:
                password = random_str
                break
        password_hash = generate_password_hash(password)
        user = User(userName=userName, password=password_hash,liveDemo = True,
                    email=email, plugLimit=0, expiredAt=lambda: datetime.datetime.now(pytz.UTC) + datetime.timedelta(days=7))
        user.save()
        # print(user.id)
        plug = Plug(liveDemo=True, userId=user.id, model="gpt-4", features=[current_app.config[
            'UPLOAD_FILES'], current_app.config['CRAWL_WEBSITE']])
        plug.save()

        token_payload = {
            "email": email,
            "password": password
        }

        token = create_access_token(
            identity=token_payload, expires_delta=timedelta(days=7))
        url = callback+token
        content = "Exciting news! The demo for 2GAI is now live. You can click on the button below to start:"

        ps = f"""
        If you have any questions or comments, simply email admin@2gai.ai. We would love to hear from you!
        """
        html_content = main_mail_template(
            "Live Demo", f"Hi {your_name}!", "", content, url, " Start Live Demo", ps)
        send_mail_smtp(email, "Live Demo", html_content)

        return {"code": 200, "message": "Live demo request has been accepted"}, HTTP_200_OK
    except Exception as e:
        return {"code": 500, "message": "Live demo request acceptance failed", "error": str(e)}, HTTP_500_INTERNAL_SERVER_ERROR


@live_demo.post("/submit_request")
def send_request():
    try:
        request_data = request.get_json()
        if not request_data:
            return {"code": 400, "message": "Invalid JSON data"}, HTTP_400_BAD_REQUEST
        expires_in = timedelta(days=7)

        user_email = request_data.get("businessEmail", "")
        your_name = request_data.get("yourName", "")
        company = request_data.get("company", "")
        title = request_data.get("title", "")
        interest = request_data.get("interest", "")
        callback = request_data.get("callback", "")
        callback_accept_page = request_data.get("callbackAcceptPage", "")
        del request_data["callback"]
        del request_data["callbackAcceptPage"]

        old_user = User.objects(email=user_email).first() or User.objects(
            userName=your_name).first()

        if old_user:
            return {"code": 400, "message": "Email or User Name already exists"}, HTTP_400_BAD_REQUEST

        if not user_email:
            return {"code": 400, "message": "Email is required"}, HTTP_400_BAD_REQUEST
        if not callback:
            return {"code": 400, "message": "Callback is required"}, HTTP_400_BAD_REQUEST

        if not your_name:
            return {"code": 400, "message": "Your name is required"}, HTTP_400_BAD_REQUEST
        if not company:
            return {"code": 400, "message": "Company is required"}, HTTP_400_BAD_REQUEST
        if not title:
            return {"code": 400, "message": "Title is required"}, HTTP_400_BAD_REQUEST

        mail_exists = User.objects(email=user_email).first()

        if mail_exists:
            return {"code": 400, "message": "Email already exists"}, HTTP_400_BAD_REQUEST

        token_payload = {
            "email": user_email,
            "your_name": your_name,
            "callback": callback,
        }
        token_accept = create_access_token(
            identity=token_payload, expires_delta=expires_in)
        url_accept_page = callback_accept_page + \
            f"{token_accept}&mail={user_email}"

        content_approve = f"<b>{your_name}<b> has requested a demo. Please click the button below to approve it."
        html_content_approve = main_mail_template(
            "Request Live Demo", f"Hi 2GAI Admin!", "", content_approve, url_accept_page, button_name="Go to accept demo page")

        send_mail_smtp(LIVE_DEMO_APPROVER_MAIL,
                       "Request Live Demo", html_content_approve)
        # mail to user

        content_user = "We received your demo request for 2GAI. We're coordinating our schedule demo time soon. Thanks for your patience."
        html_content = main_mail_template_non_button(
            "Request Live Demo", f"Hi {your_name}!", "", content_user)
        send_mail_smtp(user_email, "Request Live Demo", html_content)

        return {
            "code": 200,
            "message": "Request Live Demo sent successfully.",
        }, HTTP_200_OK
    except Exception as e:
        return {"code": 500, "message": "Error", "error": str(e)}, HTTP_500_INTERNAL_SERVER_ERROR
