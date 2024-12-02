from flask import Blueprint, request
from src.models import Subscription
from flask_jwt_extended import jwt_required
from src.helper import role_restrict, Controller
from src.config.config import ADMIN
admin_subscription = Blueprint(
    "admin_subscription", __name__, url_prefix="/web/api/v1/admin/subscription")


@admin_subscription.get("")
@jwt_required()
@role_restrict(ADMIN)
def get_subscriptions():
    return Controller.get_all(Subscription, request)


@admin_subscription.get("/<subscription_id>")
@jwt_required()
@role_restrict(ADMIN)
def get_subscription(subscription_id):
    return Controller.get_by_id(Subscription, request, subscription_id)


@admin_subscription.post("")
@jwt_required()
@role_restrict(ADMIN)
def create_subscription():
    return Controller.create(Subscription, request)


@admin_subscription.delete("/<subscription_id>")
@jwt_required()
@role_restrict(ADMIN)
def delete_subscription(subscription_id):
    return Controller.delete(Subscription, subscription_id)


@admin_subscription.patch("/<subscription_id>")
@jwt_required()
@role_restrict(ADMIN)
def update_subscription(subscription_id):
    return Controller.update_by_id(Subscription, request, subscription_id)

