from flask import Blueprint, request
import stripe
from src.models import User
from flask_jwt_extended import jwt_required
from src.helper import role_restrict, Controller
from src.config.config import ADMIN, STRIPE_API_SECRET_KEY
admin_user = Blueprint(
    "admin_user", __name__, url_prefix="/web/api/v1/admin/user")

stripe.api_key = STRIPE_API_SECRET_KEY

@admin_user.get("")
@jwt_required()
@role_restrict(ADMIN)
def get_users():
    return Controller.get_all(User, request)

 
@admin_user.get("/<user_id>")
@jwt_required()
@role_restrict(ADMIN)
def get_user(user_id):
    return Controller.get_by_id(User, request, user_id)


@admin_user.post("")
@jwt_required()
@role_restrict(ADMIN)
def create_user():
    return Controller.create(User, request)


@admin_user.delete("/<user_id>")
@jwt_required()
@role_restrict(ADMIN)
def delete_user(user_id):
    return Controller.delete(User, user_id)


@admin_user.patch("/<user_id>")
@jwt_required()
@role_restrict(ADMIN)
def update_user(user_id):
    return Controller.update_by_id(User, request, user_id)

@admin_user.get("/payment_user_data")
@jwt_required()
@role_restrict(ADMIN)
def get_payment_user_data():
    metadata_to_search = {
    "user_id": "64aff45ae43f3103da6f1b52"
    }
    all_customers = stripe.Customer.list(limit=100)  # Adjust the limit as needed

    # Retrieve customers with the specified metadata
    filtered_customers = [
    customer for customer in all_customers if customer.metadata == metadata_to_search
    ]

    # Loop through the filtered customers
    # for customer in filtered_customers:
    #     print(f"Customer ID: {customer.id}, Email: {customer.email}")
    return {"code": 200, "message": "Success"}