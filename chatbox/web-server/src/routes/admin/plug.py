from flask import Blueprint, request
from src.models.PlugModel import Plug
from flask_jwt_extended import jwt_required
from src.helper import role_restrict, Controller
from src.config.config import ADMIN
admin_plug = Blueprint(
    "admin_plug", __name__, url_prefix="/web/api/v1/admin/plug")


@admin_plug.get("")
@jwt_required()
@role_restrict(ADMIN)
def get_plugs():
    return Controller.get_all(Plug, request)


@admin_plug.get("/<plug_id>")
@jwt_required()
@role_restrict(ADMIN)
def get_plug(plug_id):
    return Controller.get_by_id(Plug, request, plug_id)


@admin_plug.post("")
@jwt_required()
@role_restrict(ADMIN)
def create_plug():
    return Controller.create(Plug, request)


@admin_plug.delete("/<plug_id>")
@jwt_required()
@role_restrict(ADMIN)
def delete_plug(plug_id):
    return Controller.delete(Plug, plug_id)


@admin_plug.patch("/<plug_id>")
@jwt_required()
@role_restrict(ADMIN)
def update_plug(plug_id):
    return Controller.update_by_id(Plug, request, plug_id)
