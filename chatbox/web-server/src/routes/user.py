from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.constants.http_status_codes import (
    HTTP_200_OK, HTTP_400_BAD_REQUEST, HTTP_401_UNAUTHORIZED, HTTP_500_INTERNAL_SERVER_ERROR, HTTP_404_NOT_FOUND)
from src.models import User, UserKey, MapPoint, Plug
from src.config.config import URL_PATH
from src.services import validate_user_openai_key
from src.helper import get_all_model_fields, is_field_in_embedded_document
from bson import ObjectId
from copy import deepcopy

user = Blueprint(
    "user", __name__, url_prefix=f"{URL_PATH}/web/api/v1/user")


@user.patch("/update")
@jwt_required()
def user_update():
    try:
        user_id = get_jwt_identity()
        user = User.objects(id=user_id).first()
        if not user:
            return {"code": 404, "message": "User not found"}, HTTP_404_NOT_FOUND
        data = request.json
        if data is None:
            return {"code": 400, "message": "No data provided"}, HTTP_400_BAD_REQUEST
        modifiable_fields = ["firstName", "lastName", "password"]

        user_model_fields = user._fields_ordered
        for field in data:
            if field in modifiable_fields:

                if data[field] is not None and field in user_model_fields:
                    user[field] = data[field]
            else:
                return {
                    "code": 400,
                    "message": f"Invalid field {field} provided.",
                }, HTTP_400_BAD_REQUEST
        user.save()
        return {
            "code": 200,
            "data": user.to_json(),
            "message": "User updated successfully."
        }, HTTP_200_OK

    except Exception as e:
        return {
            "code": 500,
            "message": f"Failed to update user. {str(e)}",
        }, HTTP_500_INTERNAL_SERVER_ERROR


@user.get("/key")
@jwt_required()
def get_user_keys():
    try:
        user_id = get_jwt_identity()
        user = User.objects(id=user_id).first()
        plug_id = request.headers.get('plugId')
        if not user:
            return {"code": 404, "message": "User not found"}, HTTP_404_NOT_FOUND
        if plug_id:
            plug = Plug.objects(id=plug_id).first()
            if not plug:
                return {"code": 404, "message": "Plug not found"}, HTTP_404_NOT_FOUND
            keys = [key.to_json() for key in user.userKeys]
            for user_key in user.userKeys:
                if user_key.key == plug.userKey or user_key.isDefault and not plug.userKey:
                    user_key.active = True
                else:
                    user_key.active = False
            return {
                "code": 200,
                "data": [key.to_json() for key in user.userKeys],
                "message": "User keys retrieved successfully."
            }, HTTP_200_OK
        return {
            "code": 200,
            "data": [key.to_json() for key in user.userKeys],
            "message": "User keys retrieved successfully."
        }, HTTP_200_OK
    except Exception as e:
        return {
            "code": 500,
            "message": f"Failed to get user keys. {str(e)}",
        }, HTTP_500_INTERNAL_SERVER_ERROR


@user.post("/key")
@jwt_required()
def add_new_key():
    try:
        user_id = get_jwt_identity()
        user = User.objects(id=user_id).first()
        if not user:
            return {"code": 404, "message": "User not found"}, HTTP_404_NOT_FOUND
        data = request.json
        if data is None:
            return {"code": 400, "message": "No data provided"}, HTTP_400_BAD_REQUEST
        key = data.get("key", None)
        if key is None or key == "":
            return {"code": 400, "message": "No key provided"}, HTTP_400_BAD_REQUEST
        is_valid, message = validate_user_openai_key(key)
        if not is_valid:
            return {"code": 400, "message": message}, HTTP_401_UNAUTHORIZED
        key_exist = user.userKeys.filter(key=key).first()
        if key_exist:
            return {"code": 400, "message": "Key already exists"}, HTTP_400_BAD_REQUEST

        user_key = UserKey(key=key)
        user.userKeys.append(user_key)
        user.save()
        new_key = user.userKeys.filter(key=key).first()
        return {
            "code": 200,
            "data": new_key.to_json(),
            "message": "Key added successfully."
        }, HTTP_200_OK
    except Exception as e:
        return {
            "code": 500,
            "message": f"Failed to add new key. {str(e)}",
        }, HTTP_500_INTERNAL_SERVER_ERROR


@user.patch("/key/<key_id>")
@jwt_required()
def update_user_key(key_id):
    try:
        user_id = get_jwt_identity()
        user = User.objects(id=user_id).first()
        plug_id = request.headers.get('plugId')
        print("plug_id",plug_id)
        key_exist = user.userKeys.filter(id=ObjectId(key_id)).first()
        old_key_obj = deepcopy(key_exist)
        if not key_exist:
            return {"code": 400, "message": "Old key does not exist"}, HTTP_400_BAD_REQUEST
        modifiable_fields = ["key", "isDefault", "active"]
        old_key = key_exist.key
        if not user:
            return {"code": 404, "message": "User not found"}, HTTP_404_NOT_FOUND
        data = request.json
        plug_key={}
        if data is None:
            return {"code": 400, "message": "No data provided"}, HTTP_400_BAD_REQUEST
        user_fields = get_all_model_fields(User)
        for field in data:
            if field in modifiable_fields:
                if field in user_fields:
                    if is_field_in_embedded_document(User, field):
                        # need fix
                        if key_exist:
                            if field == "active" and data[field] and not plug_id:
                                if user.userKeys.filter(id=ObjectId(key_id)).first().key == data[field] and field == "key":
                                    return {"code": 400, "message": "Key already exists"}, HTTP_400_BAD_REQUEST
                                if user.userKeys.filter(id=ObjectId(key_id)).first().active == data[field] and field == "active":
                                    return {"code": 400, "message": "Key already active"}, HTTP_400_BAD_REQUEST
                                key_exist[field] = data[field]
                                plugs = Plug.objects(userId=user_id)
                                for plug in plugs:
                                    plug.userKey = key_exist.key if not key_exist.isDefault else None
                                    plug.save()
                                for user_key in user.userKeys:
                                    if user_key.key != old_key:
                                        user_key.active = False
                            elif field == "active" and data[field] and plug_id:
                                plug_key = key_exist.to_json()
                                plug = Plug.objects(id=plug_id).first()
                                if plug.userKey == key_exist.key and field == "active":
                                    return {"code": 400, "message": "Plug is using this key"}, HTTP_400_BAD_REQUEST
                                plug.userKey = key_exist.key if not key_exist.isDefault else None
                                plug.save()
                                plug_key["active"] = True
                            else:
                                key_exist[field] = data[field]

                        else:
                            return {"code": 400, "message": "Key does not exist"}, HTTP_400_BAD_REQUEST
            else:
                return {
                    "code": 400,
                    "message": f"Invalid field {field} provided.",
                }, HTTP_400_BAD_REQUEST
        if not key_exist.isDefault:
            is_valid, message = validate_user_openai_key(key_exist.key)
            if not is_valid:
                return {"code": 400, "message": message}, HTTP_400_BAD_REQUEST
        user.save()

        return {
            "code": 200,
            "data": key_exist.to_json() if not plug_key else plug_key,
            "message": "Update successfully"
        }

    except Exception as e:
        return {
            "code": 500,
            "message": f"Failed to update key. {str(e)}",
        }, HTTP_500_INTERNAL_SERVER_ERROR


@user.delete("/key/<key_id>")
@jwt_required()
def delete_key(key_id):
    try:
        user_id = get_jwt_identity()
        user = User.objects(id=user_id).first()
        if not user:
            return {"code": 404, "message": "User not found"}, HTTP_404_NOT_FOUND
        if key_id is None:
            return {"code": 400, "message": "No key id provided"}, HTTP_400_BAD_REQUEST
        key_exist = user.userKeys.filter(id=ObjectId(key_id)).first()
        if not key_exist:
            return {"code": 400, "message": "Key does not exist"}, HTTP_400_BAD_REQUEST
        if key_exist.active:
            return {"code": 400, "message": "Cannot delete active key"}, HTTP_400_BAD_REQUEST
        if key_exist.isDefault:
            return {"code": 400, "message": "Cannot delete default key"}, HTTP_400_BAD_REQUEST
        user.userKeys.remove(key_exist)
        user.save()
        return {
            "code": 200,
            "data": key_exist.to_json(),
            "message": "Delete successfully"
        }
    except Exception as e:
        return {
            "code": 500,
            "message": f"Failed to delete key. {str(e)}",
        }, HTTP_500_INTERNAL_SERVER_ERROR
