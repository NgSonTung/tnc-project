from flask import Blueprint, request
from mongoengine import ValidationError
from src.models import Client, User, Subscription, Plug
from src.constants.http_status_codes import (
    HTTP_200_OK, HTTP_201_CREATED, HTTP_400_BAD_REQUEST, HTTP_500_INTERNAL_SERVER_ERROR, HTTP_404_NOT_FOUND
)
from bson.objectid import ObjectId
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.helper import is_valid_base_url
from src.services import clientService
from src.config.config import URL_PATH
client = Blueprint("client", __name__, url_prefix=f"{URL_PATH}/web/api/v1/client")


@client.get("/<client_id>")
@jwt_required()
def get_client_by_id(client_id):
    try:
        user_id = get_jwt_identity()
        plug = Plug.objects(client__id=ObjectId(
            client_id), userId=user_id).first()
        if not plug:
            return {"code": 404, f"message": "Client not found"}, HTTP_404_NOT_FOUND

        client = plug.client

        return {"code": 200, "data": client.to_json(), "message": "Client retrieved successfully"}, HTTP_200_OK

    except Exception as e:
        return {"code": 500, "message": "Failed to retrieve client", "error": str(e)}, HTTP_500_INTERNAL_SERVER_ERROR


@client.post("")
@jwt_required()
def create_client():
    try:
        data = request.json
        user_id = get_jwt_identity()
        plug_id = data.get("plugId", None)
        if not ObjectId.is_valid(plug_id):
            return {"code": 400, "message": "Invalid plugId"}, HTTP_400_BAD_REQUEST

        origin = data.get("origin", None)
        if origin is not None and not is_valid_base_url(origin):
            return {"code": 400,
                    "message": "The input must be a valid base URL without a trailing slash"}, HTTP_400_BAD_REQUEST

        plug = Plug.objects(id=ObjectId(plug_id), userId=user_id).first()
        if not plug:
            return {"code": 404, "message": "Plug not found"}, HTTP_404_NOT_FOUND

        if not plug.active:
            return {"code": 400, "message": "Plug is not active"}, HTTP_400_BAD_REQUEST
        client_exist = plug.client
        user = User.objects(id=user_id).first()

        # Check client limit
        if client_exist:
            return {"code": 400, "message": f"Please delete existing client to create a new one"}, HTTP_400_BAD_REQUEST

        # Check subscription
        subscription = Subscription.objects(
            id=ObjectId(user.subscriptionId)).first()
        if not subscription:
            return {"code": 400, "message": "Please subscribe to create a client"}, HTTP_400_BAD_REQUEST

        # Add client to plug
        client = Client(origin=origin)
        plug.update(client=client)

        return {
            "code": 201,
            "message": "Client added successfully.",
            "data": client.to_json()
        }, HTTP_201_CREATED

    except ValidationError as e:
        return {"code": 400, "message": "Validation error", "error": str(e)}, HTTP_400_BAD_REQUEST
    except Exception as e:
        return {"code": 500, "message": "Failed to create client", "error": str(e)}, HTTP_500_INTERNAL_SERVER_ERROR


@client.patch("/<client_id>")
@jwt_required()
def update_client(client_id):
    try:
        user_id = get_jwt_identity()
        data = request.json

        plug = Plug.objects(client__id=ObjectId(
            client_id), userId=user_id).first()
        if not plug:
            return {"code": 404, "message": "Client not found"}, HTTP_404_NOT_FOUND

        if not plug.active:
            return {"code": 400, "message": "Plug is not active"}, HTTP_400_BAD_REQUEST
        client = plug.client
        if 'origin' in data:
            origin = data.get("origin", "")
            if not is_valid_base_url(origin):
                if origin != '':
                    return {"code": 400,
                            "message": "The input must be a valid base URL without a trailing slash"}, HTTP_400_BAD_REQUEST
            client.origin = origin
        plug.save()
        return {"code": 200, "data": client.to_json(), "message": "Client updated successfully"}, HTTP_200_OK

    except ValidationError as e:
        return {
            "code": 500,
            "message": "Validation error",
            "error": str(e)}, HTTP_400_BAD_REQUEST
    except Exception as e:
        return {
            "code": 500,
            "message": "Failed to update client.",
            "error": str(e)
        }, HTTP_500_INTERNAL_SERVER_ERROR


@client.delete("/<client_id>")
@jwt_required()
def delete_client(client_id):
    try:
        user_id = get_jwt_identity()
        plug = Plug.objects(client__id=ObjectId(
            client_id), userId=user_id).first()
        if not plug:
            return {"code": 404, "message": "Client not found"}, HTTP_404_NOT_FOUND
        if not plug.active:
            return {"code": 400, "message": "Plug is not active"}, HTTP_400_BAD_REQUEST
        client = plug.client
        plug.update(unset__client=ObjectId(client_id))
        return {"code": 200, "data": client.to_json(), "message": "Client deleted successfully"}, HTTP_200_OK

    except Exception as e:
        return {
            "code": 500,
            "message": "Failed to delete client.",
            "error": str(e)
        }, HTTP_500_INTERNAL_SERVER_ERROR


@client.get("/key/<client_key>")
def get_client_by_key(client_key):
    try:
        if not client_key:
            return {"code": 400, "message": "Missing client_key"}, HTTP_400_BAD_REQUEST

        plug = Plug.objects(client__key=client_key).first()

        if not plug:
            return {"code": 404, "message": "Client not found"}, HTTP_404_NOT_FOUND

        if not plug.active:
            return {"code": 400, "message": "Plug is not active"}, HTTP_400_BAD_REQUEST

        client = plug.client

        return {"code": 200, "data": client.to_json(), "message": "Client retrieved successfully"}, HTTP_200_OK

    except Exception as e:
        return {"code": 500, "message": "Failed to retrieve client", "error": str(e)}, HTTP_500_INTERNAL_SERVER_ERROR
