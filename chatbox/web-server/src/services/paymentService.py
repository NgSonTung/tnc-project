import stripe
from flask import request
from flask_jwt_extended import create_access_token
from src.config.config import STRIPE_API_SECRET_KEY, TERM_URL, PRIVACY_URL, DEFAULT_BILLING_CALL_BACK_URL
from src.models import Subscription, User
from src.constants.http_status_codes import (HTTP_200_OK, HTTP_500_INTERNAL_SERVER_ERROR, HTTP_400_BAD_REQUEST)
from datetime import timedelta, datetime

stripe.api_key = STRIPE_API_SECRET_KEY


def handle_create_checkout_session(user_id, PRICE_ID, callback_success_url, callback_cancel_url):
    print("handle_create_checkout_session",STRIPE_API_SECRET_KEY)
    try:
        user = User.objects(id=user_id).first()

        subs = Subscription.objects(stripePriceId=PRICE_ID).first()
        if subs.id == user.subscriptionId:
            return {"code": 400, "message": "The user has already subscribed to this package"}, HTTP_400_BAD_REQUEST

        customer = stripe.Customer.create(
            metadata={"user_id": user_id},
            email=user.email,
        )
        stripe_customer_id = customer.id
        checkout_session = stripe.checkout.Session.create(
            line_items=[
                {
                    # Provide the exact Price ID (for example, pr_1234) of the product you want to sell
                    'price': f'{PRICE_ID}',
                    'quantity': 1,
                },
            ],
            mode='subscription',
            locale="en",
            customer=stripe_customer_id,
            consent_collection={
                'terms_of_service': 'required',
            },
            custom_text={
                "terms_of_service_acceptance": {
                    "message": f"I agree to the [Terms of Service]({TERM_URL}) and [Privacy Policy]({PRIVACY_URL})",
                },
            },

            success_url=callback_success_url + generate_message_token(checkout=True),  # callback_success_url
            cancel_url=callback_cancel_url + generate_message_token(),  # callback_cancel_url
        )

        return {'code': 200, "message": "Create successfully", 'data': checkout_session.url}

    except Exception as e:
        raise e


def handle_change_plan(user_id, PRICE_ID, callback_success_url, callback_cancel_url):
    try:
        user = User.objects(id=user_id).first()
        subs = Subscription.objects(stripePriceId=PRICE_ID).first()
        if subs.id == user.subscriptionId:
            return {"code": 400, "message": "The user has already subscribed to this package"}, HTTP_400_BAD_REQUEST
        old_customer_id = user.stripeCustomerId
        if old_customer_id is not None and len(old_customer_id) > 0:
            current_subscription = stripe.Subscription.list(customer=old_customer_id)

            if current_subscription and current_subscription.data:
                current_subscription_id = current_subscription.data[0].id
                subscription = stripe.Subscription.retrieve(current_subscription_id)
                current_subscription_item_id = subscription['items']['data'][0]['id']
                subscription_status = current_subscription.data[0].status
                latest_invoice = stripe.Invoice.retrieve(current_subscription.data[0].latest_invoice)
                latest_invoice_status = latest_invoice.status
                if subscription_status == 'past_due' and latest_invoice_status == 'open':
                    default_callback = DEFAULT_BILLING_CALL_BACK_URL
                    portalSession = stripe.billing_portal.Session.create(
                        customer=user.stripeCustomerId,
                        return_url=default_callback,)
                    return {'code': 200, "message": "Create successfully", "data":  {"isChangePlan": None,"url": portalSession.url}}, HTTP_200_OK
                updated_subscription = stripe.Subscription.modify(
                    current_subscription_id,
                    items=[{
                        'id': f"{current_subscription_item_id}",
                        "price": f"{PRICE_ID}",
                    }],
                    # Charge the prorated amount immediately.
                    proration_behavior='always_invoice',
                )
                mess_token = generate_message_token(old_subs=user.subscriptionId, new_subs=subs.id)
                return {'code': 200, "message": "Upgrade or Downgrade successfully",
                        "data": {"isChangePlan": True, "messToken": mess_token}}, HTTP_200_OK

            else:
                checkout_session = stripe.checkout.Session.create(
                    line_items=[
                        {
                            # Provide the exact Price ID (for example, pr_1234) of the product you want to sell
                            'price': f'{PRICE_ID}',
                            'quantity': 1,
                        },
                    ],
                    mode='subscription',
                    locale="en",
                    customer=user.stripeCustomerId,
                    consent_collection={
                        'terms_of_service': 'required',
                    },
                    custom_text={
                        "terms_of_service_acceptance": {
                            "message": f"I agree to the [Terms of Service]({TERM_URL}) and [Privacy Policy]({PRIVACY_URL})",
                        },
                    },
                    success_url=callback_success_url + generate_message_token(checkout=True),
                    # callback_success_url
                    cancel_url=callback_cancel_url + generate_message_token(),  # callback_cancel_url
                )
                return {'code': 200, "message": "Create successfully",
                        "data": {"isChangePlan": None, "url": checkout_session.url}}
        else:
            return {"code": 400, "message": "The user does not have a subscription"}, HTTP_400_BAD_REQUEST

    except Exception as e:
        raise e


def generate_message_token(old_subs=None, new_subs=None, checkout=False):
    try:
        if old_subs is not None and new_subs is not None:
            old_subs = Subscription.objects(id=old_subs).first()
            new_subs = Subscription.objects(id=new_subs).first()
            message = f"Your subscription has been changed from {old_subs.name} to {new_subs.name}"
            if old_subs.cost < new_subs.cost:
                title = "Upgrade Successfully"
            else:
                title = "Downgrade Successfully"
            return create_access_token(identity={"title": title, "message": message}, expires_delta=timedelta(days=1))
        elif new_subs is None and old_subs is None:
            if checkout:
                message = """
                Thank you for your purchase! Your transaction was completed successfully, and a receipt has been sent to your email.
                """
                return create_access_token(identity={"title": "Payment Successful!", "message": message})
            else:
                message = """
                We're sorry, but your transaction could not be completed at this time. Please check your payment details and try again!
                """
                return create_access_token(identity={"title": "Payment Failed!", "message": message})

        return None
    except Exception as e:
        raise e
