from flask import Blueprint, request
from src.models import Subscription, User, PaymentInvoice
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.helper import Controller
from src.constants.http_status_codes import HTTP_200_OK, HTTP_404_NOT_FOUND, HTTP_500_INTERNAL_SERVER_ERROR
import stripe
from src.config.config import STRIPE_API_SECRET_KEY, URL_PATH
from src.services.subscriptionService import custom_sort_key

stripe.api_key = STRIPE_API_SECRET_KEY

subscription = Blueprint(
    "subscription", __name__, url_prefix=f"{URL_PATH}/web/api/v1/subscription")


@subscription.get("")
@jwt_required(optional=True)
def get_subscriptions():
    try:
        subs_active = []
        user = None
        user_role = None
        if get_jwt_identity():
            user_id = get_jwt_identity()
            user = User.objects(id=user_id).first()
            user_role = Subscription.objects(id=user.subscriptionId).first().name if user is not None else None
        subs = Subscription.objects(active=True)
        for sub in subs:
            if user is not None and (user.subscriptionId == sub.id or user_role == sub.name):
                sub = sub.to_json()
                sub["current"] = True
            elif (user is not None and user.subscriptionId != sub.id) or not get_jwt_identity():
                sub = sub.to_json()
                sub["current"] = False
            elif user is not None and user.subscriptionRole == "Free" and sub.name == "Free":
                sub = sub.to_json()
                sub["current"] = True
            if sub["models"][0] == "gpt-4":
                # sub = sub.to_json()
                sub["models"][0] = "gpt-4"
            subs_active.append(sub)
        sorted_data = sorted(subs_active, key=custom_sort_key)
        return {"code": 200, "message": "Subscription retrieval successful", "data": sorted_data}, HTTP_200_OK
    except Exception as e:
        return {"code": 500, "message": f"Failed to get subscriptions {str(e)}", }, HTTP_500_INTERNAL_SERVER_ERROR


@subscription.get("/<subscription_id>")
@jwt_required()
def get_subscription(subscription_id):
    return Controller.get_by_id(Subscription, request, subscription_id)


@subscription.get("/features")
def get_subscription_fuetures():
    try:
        subscriptions = Subscription.objects()
        features = ["GPT Model"]
        features_lower = ["gpt model"]
        for subscription in subscriptions:
            if subscription.active:
                for f in subscription.features:
                    if f.lower() not in features_lower and "GPT" not in f and "gpt" not in f:
                        f = f.title()
                        if "2gai" in f or "2Gai" in f:
                            if "2gaip" in f or "2Gaip" in f:
                                f = f.replace('Gaip', 'GAIP')
                            f = f.replace('Gai', 'GAI')
                        features.append(f)
                        features_lower.append(f.lower())
        return {"code": 200, "message": "success", "data": features}, HTTP_200_OK
    except Exception as e:
        return {"code": 500, "message": "Failed to get features", "error": str(e)}, HTTP_500_INTERNAL_SERVER_ERROR


@subscription.get("/invoice/retrieve_invoices")
@jwt_required()
def retrieve_invoices():
    try:
        user_id = get_jwt_identity()
        user = User.objects(id=user_id).first()
        if user is None:
            return {"code": 404, "message": "User not found"}, HTTP_404_NOT_FOUND
        invoices = PaymentInvoice.objects(
            stripeCustomerId=user.stripeCustomerId)
        invoices_json = [invoice.to_json() for invoice in invoices]

        return {"code": 200, "message": "Successful retrieval of user invoices", "data": invoices_json}, HTTP_200_OK

    except Exception as e:
        return {"code": 500, "message": "Failed to retrieve invoices", "error": str(e)}, HTTP_500_INTERNAL_SERVER_ERROR


@subscription.get("/get_current_subscription")
@jwt_required()
def get_current_subscription():
    try:
        user_id = get_jwt_identity()
        user = User.objects(id=user_id).first()
        if user is None:
            return {"code": 404, "message": "User not found"}, HTTP_404_NOT_FOUND
        if user.subscriptionId is None:
            return {"code": 404, "message": "User does not have a subscription"}, HTTP_404_NOT_FOUND
        subscription = Subscription.objects(id=user.subscriptionId).first()
        if subscription is None:
            return {"code": 404, "message": "Subscription not found"}, HTTP_404_NOT_FOUND
        customer_credits = 0
        if user.stripeCustomerId is not None:
            list_credits_data = stripe.Customer.list_balance_transactions(user.stripeCustomerId,
                                                                          limit=1)  # get last transaction
            if list_credits_data.data:
                credits_data = list_credits_data.data[0]
                if credits_data.ending_balance <= 0:  # have credits
                    customer_credits = credits_data.ending_balance
                    if customer_credits != 0:
                        customer_credits = (customer_credits / 100) * -1
        name = subscription.name
        cost = subscription.cost
        is_yearly = False
        description = subscription.description
        user_subscription = None
        if user.stripeCustomerId is not None:
            user_subscription = stripe.Subscription.list(
                customer=user.stripeCustomerId)
        is_paused = False

        if user_subscription is not None and user_subscription.data:
            is_yearly = user_subscription.data[0]["items"]["data"][0]["price"]["recurring"]["interval"] == "year"
            if user_subscription.data[0]["pause_collection"]:
                is_paused = True
        subscription_json = {"name": name, "cost": str(cost), "isYearly": is_yearly, "description": description,
                             "isPaused": is_paused,
                             "credits": "$" + str(customer_credits)}
        if subscription.name == "Free" and user.stripeCustomerId is None:  # not subscribed
            subscription_json = {"name": name,
                                 "cost": str(cost),
                                 "isYearly": False,
                                 "description": description,
                                 "isPaused": False,
                                 "credits": "$0"}

            if user.subExpiredAt is not None:
                subscription_json["subExpiredAt"] = user.subExpiredAt
            return {"code": 200, "message": "Successful retrieval of current subscription",
                    "data": subscription_json}, HTTP_200_OK

        if user.subExpiredAt is not None:
            subscription_json["subExpiredAt"] = user.subExpiredAt
        return {"code": 200, "message": "Successful retrieval of current subscription",
                "data": subscription_json}, HTTP_200_OK
    except Exception as e:
        return {"code": 500,
                "message": f"Failed to retrieve current subscription {str(e)}"}, HTTP_500_INTERNAL_SERVER_ERROR


@subscription.post("/admin/create_subscription")
def create_subscription():
    try:
        data = request.get_json()
        name = data.get("name")
        default_price_data = data.get("defaultPriceData")
        currency = default_price_data.get("currency", "usd")
        unit_amount = default_price_data.get("unitAmount")
        interval = default_price_data.get("interval", "month")
        interval_count = default_price_data.get("intervalCount", 1)
        product = stripe.Product.create(
            name=name,
            default_price_data={"currency": currency, "unit_amount": unit_amount,
                                "recurring": {"interval": interval, "interval_count": interval_count}},
            metadata={"coming_soon": "false", "plug_limit": 2,
                      "features": "gpt-4,upload files", "models": "gpt-4"},
        )
        print(product)
        return {"code": 200, "message": "Subscription created successfully", "data": product}, HTTP_200_OK
    except Exception as e:
        return {"code": 500, "message": "Failed to create subscription",
                "error": str(e)}, HTTP_500_INTERNAL_SERVER_ERROR
