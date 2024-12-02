from flask import Blueprint, request
from src.models import ContextItem
from flask_jwt_extended import jwt_required
from src.helper import role_restrict, Controller
from src.config.config import ADMIN
admin_context_base = Blueprint(
    "admin_context_base", __name__, url_prefix="/web/api/v1/admin/context_base")


@admin_context_base.get("")
@jwt_required()
@role_restrict(ADMIN)
def get_context_bases():
    return Controller.get_all(ContextItem, request)


@admin_context_base.get("/<context_base_id>")
@jwt_required()
@role_restrict(ADMIN)
def get_context_base(context_base_id):
    return Controller.get_by_id(ContextItem, request, context_base_id)


@admin_context_base.post("")
@jwt_required()
@role_restrict(ADMIN)
def create_context_base():
    return Controller.create(ContextItem, request)


@admin_context_base.delete("/<context_base_id>")
@jwt_required()
@role_restrict(ADMIN)
def delete_context_base(context_base_id):
    return Controller.delete(ContextItem, context_base_id)


@admin_context_base.patch("/<context_base_id>")
@jwt_required()
@role_restrict(ADMIN)
def update_context_base(context_base_id):
    return Controller.update_by_id(ContextItem, request, context_base_id)
