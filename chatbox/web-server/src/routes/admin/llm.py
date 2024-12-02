from flask import Blueprint, request
from src.models import LLM
from flask_jwt_extended import jwt_required
from src.helper import role_restrict, Controller
from src.config.config import ADMIN
admin_llm = Blueprint(
    "admin_llm", __name__, url_prefix="/web/api/v1/admin/llm")


@admin_llm.get("")
@jwt_required()
@role_restrict(ADMIN)
def get_llms():
    return Controller.get_all(LLM, request)


@admin_llm.get("/<llm_id>")
@jwt_required()
@role_restrict(ADMIN)
def get_llm(llm_id):
    return Controller.get_by_id(LLM, request, llm_id)


@admin_llm.post("")
@jwt_required()
@role_restrict(ADMIN)
def create_llm():
    return Controller.create(LLM, request)


@admin_llm.delete("/<llm_id>")
@jwt_required()
@role_restrict(ADMIN)
def delete_llm(llm_id):
    return Controller.delete(LLM, llm_id)


@admin_llm.patch("/<llm_id>")
@jwt_required()
@role_restrict(ADMIN)
def update_llm(llm_id):
    return Controller.update_by_id(LLM, request, llm_id)
