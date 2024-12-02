from flask import Blueprint, request, jsonify
from mongoengine import ValidationError
from src.models import Client, User, Guest, Plug, History
from src.constants.http_status_codes import (
    HTTP_200_OK, HTTP_201_CREATED, HTTP_400_BAD_REQUEST, HTTP_500_INTERNAL_SERVER_ERROR, HTTP_404_NOT_FOUND
)
from bson.objectid import ObjectId
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.helper import is_valid_base_url
from src.helper.converter_datetime import sort_list_date_desc
from src.config.config import URL_PATH
from src.services import historyService, clientService
import math

history = Blueprint("history", __name__, url_prefix=f"{URL_PATH}/web/api/v1/history")


@history.get("/message")
@jwt_required()
def get_history_message_by_client_id_history_id():
    try:
        user_id = get_jwt_identity()
        user = User.objects(id=user_id).first()
        if not user:
            return {"code": 404, "message": "User not found"}, HTTP_404_NOT_FOUND
        client_id = request.args.get("clientId")
        history_id = request.args.get("historyId")
        page = request.args.get("page", 1, type=int)
        page_size = request.args.get("pageSize", 10, type=int)
        if not ObjectId.is_valid(client_id) or not ObjectId.is_valid(history_id):
            return {"code": 400, "message": "Invalid id"}, HTTP_400_BAD_REQUEST
        if int(page_size) > 30:
            page_size = 30
        result = historyService.handle_get_history_message_by_client_id_history_id(history_id, client_id, page,
                                                                                   page_size, user_id)
        if not result:
            return {"code": 404, "message": "History not found"}, HTTP_404_NOT_FOUND

        return {
            "code": 200,
            **result,
            "message": "History retrieved successfully."
        }, HTTP_200_OK

    except Exception as e:
        return {
            "code": 500,
            "message": "Failed to retrieve history.",
            "error": str(e)
        }, HTTP_500_INTERNAL_SERVER_ERROR


@history.delete("/<history_id>")
@jwt_required()
def delete_history(history_id):
    try:
        user_id = get_jwt_identity()
        client_id = request.args.get('clientId')

        if not ObjectId.is_valid(history_id) or not ObjectId.is_valid(client_id):
            return {"code": 400, "message": "Invalid history id"}, HTTP_400_BAD_REQUEST
        result = historyService.handle_delete_history(
            user_id, client_id, history_id)
        if not result:
            return {"code": 404, "message": "History not found"}, HTTP_404_NOT_FOUND
        return {
            "code": 200,
            "data": result,
            "message": "History deleted successfully."
        }, HTTP_200_OK
    except Exception as e:
        return {
            "code": 500,
            "message": "Failed to delete history.",
            "error": str(e)
        }, HTTP_500_INTERNAL_SERVER_ERROR


@history.get("")
@jwt_required()
def search_client_message():
    try:
        message = request.args.get("message", None)
        user_id = get_jwt_identity()
        client_id = request.args.get("clientId")
        page = request.args.get("page", 1, type=int)
        page_size = request.args.get("pageSize", 10, type=int)

        if not ObjectId.is_valid(client_id):
            return {"code": 400, "message": "Invalid client id"}, HTTP_400_BAD_REQUEST

        if page_size > 30:
            page_size = 30

        if not message:
            result = historyService.handle_get_histories_by_client_id(
                client_id, page, page_size, user_id)
            return {"code": 200, "message": "Client history retrieved successfully", **result}, HTTP_200_OK

        elif message:
            result = clientService.handle_search_client_message(
                page, page_size, client_id, message, user_id)
            return {"code": 200, "message": "Search successfully", **result}, HTTP_200_OK
        return {"code": 400, "message": "Invalid query params"}, HTTP_400_BAD_REQUEST
    except Exception as e:
        return {
            "code": 500,
            "message": "Failed to search client message.",
            "error": str(e)
        }, HTTP_500_INTERNAL_SERVER_ERROR


@history.get("/<history_id>")
@jwt_required()
def get_history_by_id(history_id):
    try:
        user_id = get_jwt_identity()
        user = User.objects(id=user_id).first()
        if not user:
            return {"code": 404, "message": "User not found"}, HTTP_404_NOT_FOUND

        if not ObjectId.is_valid(history_id) or not ObjectId.is_valid(history_id):
            return {"code": 400, "message": "Invalid id"}, HTTP_400_BAD_REQUEST
        result = historyService.handle_get_history_by_id(history_id, user_id)
        if not result:
            return {"code": 200, "data": {}, "message": "History not found"}, HTTP_200_OK
        return {
            "code": 200,
            "data": result[0],
            "message": "History retrieved successfully."
        }, HTTP_200_OK
    except Exception as e:
        return {
            "code": 500,
            "message": "Failed to retrieve history.",
            "error": str(e)
        }, HTTP_500_INTERNAL_SERVER_ERROR
