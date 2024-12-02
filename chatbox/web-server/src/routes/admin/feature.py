from flask import Blueprint, request
from src.models import Feature
from flask_jwt_extended import jwt_required
from src.helper import role_restrict, Controller
from src.config.config import ADMIN
admin_feature = Blueprint(
    "admin_feature", __name__, url_prefix="/web/api/v1/admin/feature")


@admin_feature.get("")
@jwt_required()
@role_restrict(ADMIN)
def get_features():
    return Controller.get_all(Feature, request)


@admin_feature.get("/<feature_id>")
@jwt_required()
@role_restrict(ADMIN)
def get_feature(feature_id):
    return Controller.get_by_id(Feature, request, feature_id)


@admin_feature.post("")
@jwt_required()
@role_restrict(ADMIN)
def create_feature():
    return Controller.create(Feature, request)


@admin_feature.delete("/<feature_id>")
@jwt_required()
@role_restrict(ADMIN)
def delete_feature(feature_id):
    return Controller.delete(Feature, feature_id)


@admin_feature.patch("/<feature_id>")
@jwt_required()
@role_restrict(ADMIN)
def update_feature(feature_id):
    return Controller.update_by_id(Feature, request, feature_id)
