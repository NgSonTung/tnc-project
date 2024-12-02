import datetime
import os

from flask import Blueprint, request, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from jwt import decode
from src.constants.http_status_codes import HTTP_200_OK, HTTP_500_INTERNAL_SERVER_ERROR, HTTP_400_BAD_REQUEST
import stripe
from src.helper.smtp_mail import send_mail_smtp
from src.config.config import STRIPE_ENDPOINTS_WEBHOOK_SECRET_KEY, STRIPE_API_SECRET_KEY
from src.services.stripe_webhookService import (
    handle_product,
    handle_user_payment_succeeded,
    handle_invoice_payment_failed,
    handle_customer_subscription_deleted,
    handle_customer_subscription_update,
    handle_invoice_finalized,
    handle_invoice_payment_succeeded,
    handle_invoice_voided
)
from src.models import User, Subscription
from src.template.mail_template import (
    main_mail_template_non_button
)
from src.services.paymentService import handle_create_checkout_session, handle_change_plan
from src.config.config import URL_PATH

payment = Blueprint("payment", __name__, url_prefix=f"{URL_PATH}/web/api/v1/payment")
stripe.api_key = STRIPE_API_SECRET_KEY

if os.environ.get("FLASK_ENV") != "docker":
    portal_config = stripe.billing_portal.Configuration.create(
        features={
            "invoice_history": {"enabled": True},
            "payment_method_update": {"enabled": True},
            "subscription_pause": {"enabled": True},
            "customer_update": {"enabled": True, "allowed_updates": ["email", "name", "address", "phone"]},
        },
        default_return_url="http://127.0.0.1:4200" if os.environ.get("FLASK_ENV") == "development" else "https://webaipilot.neoprototype.ca",
        login_page={"enabled": True},
        business_profile={
            "headline": "Partners with Stripe for simplified billing.", }
    )
    login_page_url = portal_config.login_page.url


@payment.post("/create_checkout_session")
@jwt_required()
def create_checkout_session():
    try:
        user_id = get_jwt_identity()
        PRICE_ID = request.json.get("priceId")
        callback_success_url = request.json.get("callbackSuccessUrl")
        callback_cancel_url = request.json.get("callbackCancelUrl")

        return handle_create_checkout_session(user_id=user_id, PRICE_ID=PRICE_ID,
                                              callback_success_url=callback_success_url,
                                              callback_cancel_url=callback_cancel_url,
                                              )
    except Exception as e:
        return {"code": 500, "message": str(e)}, HTTP_500_INTERNAL_SERVER_ERROR


@payment.post("/change_plan")
@jwt_required()
def update_subscription():
    try:
        user_id = get_jwt_identity()
        PRICE_ID = request.json.get("priceId")
        callback_success_url = request.json.get("callbackSuccessUrl")
        callback_cancel_url = request.json.get("callbackCancelUrl")
        return handle_change_plan(user_id, PRICE_ID, callback_success_url, callback_cancel_url)

    except Exception as e:
        return {"code": 500, "message": str(e)}, HTTP_500_INTERNAL_SERVER_ERROR


@payment.get("/convert_message_token/")
def get_message_token():
    try:
        token = request.args.get("token")
        if token is None:
            return {"code": 400, "message": "Token is required"}, HTTP_400_BAD_REQUEST
        message = decode(token, current_app.config["JWT_SECRET_KEY"], algorithms=[
            "HS256"]).get("sub")
        return {'code': 200, "message": "Convert successfully", "data": message}, HTTP_200_OK
    except Exception as e:
        return {"code": 500, "message": str(e)}, HTTP_500_INTERNAL_SERVER_ERROR


@payment.post("/create_portal_session")
@jwt_required()
def customer_portar():
    try:
        req_data = request.json
        user_id = get_jwt_identity()
        user = User.objects(id=user_id).first()
        if user is None:
            return {"code": 400, "message": "User not found"}, HTTP_400_BAD_REQUEST

        current_subscription = stripe.Subscription.list(
            customer=user.stripeCustomerId)
        if not current_subscription.data:
            return {"code": 400, "message": "Your subscription has ended. Please consider renewing to stay with us!"}, HTTP_400_BAD_REQUEST
        default_callback = "https://www.2gai.ai/home"
        portalSession = stripe.billing_portal.Session.create(
            customer=user.stripeCustomerId,
            return_url=req_data.get("callback", default_callback)),

        return {'code': 200, "message": "Create successfully", "data": portalSession[0].url}, HTTP_200_OK
    except Exception as e:
        return {"code": 500, "message": str(e)}, HTTP_500_INTERNAL_SERVER_ERROR


@payment.get("/retrieve_portal_session")
@jwt_required()
def retrieve_portal_session():
    try:
        user_id = get_jwt_identity()
        user = User.objects(id=user_id).first()
        if user is None:
            return {"code": 400, "message": "User not found"}, HTTP_400_BAD_REQUEST
        if user.stripeCustomerId is None:
            return {"code": 400, "message": "User not found  stripeCustomerId"}, HTTP_400_BAD_REQUEST
        if user.stripePortal is None:
            return {"code": 400, "message": "User not found stripePortal"}, HTTP_400_BAD_REQUEST
        return {'code': 200, "message": "Retrieve successfully", "data": user.stripePortal}
    except Exception as e:
        return {"code": 500, "message": str(e)}, HTTP_500_INTERNAL_SERVER_ERROR


@payment.get("/portal_mail")
@jwt_required()
def portal_mail():
    try:
        # user_id = get_jwt_identity()
        # user = User.objects(id=user_id).first()
        # user_portal = user.stripePortal
        # user_email = user.email
        # user_name = user.userName
        # content = f"""We hope this message finds you well.
        # We wanted to take a moment to express our heartfelt gratitude for subscribing to 2GAI.
        # Your decision to join our community means a lot to us, and we're excited to have you on board.
        # <p>Here's your customer portal login page : {login_page_url}<p>
        #
        # """
        # ps = f"In your customer portal, you can change your payment method, edit billing information and check invoice history."
        # html_content = main_mail_template_non_button(
        #     " Thank You for Subscribing!", f"Dear {user_name},", "Welcome to 2GAI - Your Customer Portal Awaits!",
        #     content, ps)
        #
        # send_mail_smtp(user_email,
        #                "2GAI Subscription", html_content)
        return {'code': 200, "message": "Send mail successfully"}, HTTP_200_OK
    except Exception as e:
        return {"code": 500, "message": str(e)}, HTTP_500_INTERNAL_SERVER_ERROR


@payment.get("/pause_subscription")
@jwt_required()
def pause_subscription():
    try:
        user_id = get_jwt_identity()
        user = User.objects(id=user_id).first()
        if user is None:
            return {"code": 400, "message": "User not found"}, HTTP_400_BAD_REQUEST
        if user.stripeCustomerId is None:
            return {"code": 400, "message": "User not found  stripeCustomerId"}, HTTP_400_BAD_REQUEST
        if user.subscriptionId is None:
            return {"code": 400, "message": "User not found subscriptionId"}, HTTP_400_BAD_REQUEST
        current_subscription = stripe.Subscription.list(
            customer=user.stripeCustomerId)
        if not current_subscription.data:
            return {"code": 400, "message": "Your subscription has ended. Please consider renewing to stay with us!"}, HTTP_400_BAD_REQUEST
        current_subscription_id = current_subscription.data[0].id

        subscription = stripe.Subscription.modify(
            current_subscription_id,
            pause_collection={"behavior": "mark_uncollectible"}
        )

        return {'code': 200, "message": "Pause successfully"}, HTTP_200_OK

    except Exception as e:
        return {"code": 500, "message": str(e)}, HTTP_500_INTERNAL_SERVER_ERROR


@payment.get("/resume_subscription")
@jwt_required()
def resume_subscription():
    try:
        user_id = get_jwt_identity()
        user = User.objects(id=user_id).first()
        if user is None:
            return {"code": 400, "message": "User not found"}, HTTP_400_BAD_REQUEST
        if user.stripeCustomerId is None:
            return {"code": 400, "message": "User not found stripeCustomerId"}, HTTP_400_BAD_REQUEST
        if user.subscriptionId is None:
            return {"code": 400, "message": "User not found subscriptionId"}, HTTP_400_BAD_REQUEST

        # Retrieve the current subscription
        current_subscription = stripe.Subscription.list(
            customer=user.stripeCustomerId)
        if not current_subscription.data:
            return {"code": 400, "message": "Your subscription has ended. Please consider renewing to stay with us!"}, HTTP_400_BAD_REQUEST
        current_subscription_id = current_subscription.data[0].id
        current_timestamp = datetime.datetime.now().timestamp()
        if current_subscription.data[0]["pause_collection"] and \
                current_subscription.data[0]["items"]["data"][0]["price"]["active"] is True:
            if current_timestamp > current_subscription.data[0]['current_period_end']:
                # current day > current_period_end
                subscription = stripe.Subscription.modify(
                    current_subscription_id,
                    pause_collection='',
                    billing_cycle_anchor="now",
                    proration_behavior="none",
                )
            else:
                subscription = stripe.Subscription.modify(
                    current_subscription_id,
                    pause_collection='',

                )
            return {'code': 200, "message": "Resume successfully"}, HTTP_200_OK
        else:
            return {"code": 400, "message": "Subscription is not paused"}, HTTP_400_BAD_REQUEST

    except Exception as e:
        return {"code": 500, "message": str(e)}, HTTP_500_INTERNAL_SERVER_ERROR


################# Webhook #############################

@payment.post("/webhook")
def webhook():
    try:
        event = None
        payload = request.data
        sig_header = request.headers['STRIPE_SIGNATURE']
        endpoint_secret = STRIPE_ENDPOINTS_WEBHOOK_SECRET_KEY
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
        event_object = event['data']['object']
        print('eventccccccccccccccccccccccc', event['type'] )
        if event['type'] == 'checkout.session.async_payment_failed':
            session = event_object
        elif event['type'] == 'checkout.session.async_payment_succeeded':
            session = event_object
        elif event['type'] == 'checkout.session.completed':
            session = event_object
        elif event['type'] == 'checkout.session.expired':
            session = event_object
        elif event.type == 'payment_intent.succeeded':
            payment_intent = event_object  # contains a stripe.PaymentIntent
            handle_user_payment_succeeded(payment_intent)
        elif event.type == 'payment_intent.payment_failed':
            payment_intent = event_object
        elif event.type == 'payment_method.attached':
            payment_method = event.data.object  # contains a stripe.PaymentMethod
        elif event['type'] == 'product.created' or event['type'] == 'product.updated' or event['type'] == 'product.deleted':
            product = event_object
            handle_product(product, event['type'])
        elif event['type'] == 'invoice.finalized':
            invoice = event_object
            handle_invoice_finalized(invoice, "finalized")
        elif event['type'] == 'invoice.updated':
            invoice = event_object
            handle_invoice_finalized(invoice, "updated")
        elif event['type'] == 'invoice.payment_succeeded':
            invoice = event_object
            handle_invoice_payment_succeeded(invoice)
        elif event['type'] == 'invoice.payment_failed' or event['type'] == 'invoice.marked_uncollectible':
            invoice = event_object
            handle_invoice_payment_failed(invoice)
        elif event['type'] == 'invoice.voided':
            invoice = event_object
            handle_invoice_voided(invoice)
        elif event['type'] == 'customer.subscription.deleted':
            subs = event_object
            handle_customer_subscription_deleted(subs)
        elif event['type'] == 'customer.subscription.updated':
            subs = event_object
            handle_customer_subscription_update(subs)
        return {'code': 200, "message": "Webhook received"}, HTTP_200_OK
    except ValueError as e:
        # Invalid payload
        print("Invalid payload")
        return {"code": 500, "message": f"Failed to handle event {str(e)}"}, HTTP_500_INTERNAL_SERVER_ERROR
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        print("Invalid signature")
        return {"code": 500, "message": f"Failed to handle event {str(e)}"}, HTTP_500_INTERNAL_SERVER_ERROR
    except Exception as e:
        print("Error", str(e))
        return {"code": 500, "message": f"Failed to handle event {str(e)}"}, HTTP_500_INTERNAL_SERVER_ERROR
    # # Handle the event
