from flask import Blueprint, request
from src.models import Message, History
from src.constants.http_status_codes import (
    HTTP_200_OK, HTTP_400_BAD_REQUEST, HTTP_500_INTERNAL_SERVER_ERROR, HTTP_404_NOT_FOUND
)
from bson.objectid import ObjectId
from flask_jwt_extended import jwt_required, get_jwt_identity
import math
from src.config.config import URL_PATH
message = Blueprint("message", __name__, url_prefix=f"{URL_PATH}/web/api/v1/message")


@message.get("")
@jwt_required()
def get_messages():
    try:
        user_id = get_jwt_identity()

        history_id = request.args.get('historyId')
        if not ObjectId.is_valid(history_id):
            return {"code": 400, "message": "Invalid history id"}, HTTP_400_BAD_REQUEST

        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('pageSize', 30))
        if page_size > 60:
            page_size = 60
        pipeline = [
            {
                "$match": {
                    "_id": ObjectId(history_id),
                }
            },
            {
                "$lookup": {
                    "from": "message",
                    "localField": "_id",
                    "foreignField": "history",
                    "as": "messages",
                }
            },
            {
                "$lookup": {
                    "from": "guest",
                    "localField": "guest",
                    "foreignField": "_id",
                    "as": "guest"
                }
            },
            {
                "$project": {
                    "messages": 1,
                    "guest": {"$arrayElemAt": ["$guest", 0]}
                }
            },
            {
                "$lookup": {
                    "from": "plug",
                    "localField": "guest.client",
                    "foreignField": "client._id",
                    "as": "plug"
                }
            },
            {
                "$project": {
                    "messages": 1,
                    "messages": {
                        "$map": {
                            "input": "$messages",
                            "as": "message",
                            "in": {
                                "_id": "$$message._id",
                                "role": "$$message.role",
                                "content": "$$message.content",
                                "createdAt": {
                                        "$toLong": {
                                            "$toDate": "$$message.createdAt"
                                        }
                                    }
                            }
                        }},
                    "plug": {"$arrayElemAt": ["$plug", 0]}
                }
            },
            {
                "$match": {
                    "plug.userId": ObjectId(user_id),
                }
            },
            {
                "$addFields": {
                    "totalDocuments": {"$size": "$messages"},
                }
            },
            {
                "$unwind": "$messages"
            },
            {
                "$sort": {
                    "messages._id": -1
                }
            },
            {
                "$skip": (page - 1) * page_size
            },
            {
                "$limit": page_size
            },
            {
                "$addFields": {
                    "messages._id": {"$toString": "$messages._id"},
                }
            },
            {
                "$addFields": {
                    "messages.id": "$messages._id"
                }
            },
            {
                "$project": {
                    "messages._id": 0
                }
            },
            {
                "$group": {
                    "_id": "$_id",
                    "totalDocuments": {"$first": "$totalDocuments"},
                    "messages": {"$push": "$messages"}
                }
            },
            {
                "$project": {
                    "messages": 1,
                    "totalDocuments": 1,
                    "_id": 0
                }
            },

        ]
        results = list(History.objects().aggregate(*pipeline))
        if results:
            total_documents = results[0]['totalDocuments']
            total_pages = math.ceil(total_documents / page_size)
            messages = results[0]['messages']
        else:
            total_documents = 0
            total_pages = 0
            messages = []

        return {"code": 200, "data": {'messages': messages}, "page": page * 1, "pageSize": page_size * 1, "totalPages": total_pages * 1,   "totalItems": total_documents, "message": "Messages retrieved successfully"}, HTTP_200_OK

    except Exception as e:
        return {"code": 500, "message": "Failed to retrieve messages", "error": str(e)}, HTTP_500_INTERNAL_SERVER_ERROR


@message.get("/<message_id>")
@jwt_required()
def get_message_by_id(message_id):
    try:
        user_id = get_jwt_identity()

        history_id = request.args.get('historyId')
        if not ObjectId.is_valid(history_id):
            return {"code": 400, "message": "Invalid client id"}, HTTP_400_BAD_REQUEST

        if not ObjectId.is_valid(message_id):
            return {"code": 400, "message": "Invalid message id"}, HTTP_400_BAD_REQUEST

        pipeline = [
            {
                "$match": {
                    "_id": ObjectId(history_id),
                }
            },
            {
                "$lookup": {
                    "from": "message",
                    "localField": "_id",
                    "foreignField": "history",
                    "as": "messages",
                    "pipeline": [
                        {
                            "$match": {
                                "_id": ObjectId(message_id),
                            }
                        },
                    ]
                }
            },
            {
                "$lookup": {
                    "from": "guest",
                    "localField": "guest",
                    "foreignField": "_id",
                    "as": "guest"
                }
            },
            {
                "$project": {
                    "messages": 1,
                    "guest": {"$arrayElemAt": ["$guest", 0]}
                }
            },
            {
                "$lookup": {
                    "from": "plug",
                    "localField": "guest.client",
                    "foreignField": "client._id",
                    "as": "plug"
                }
            },
            {
                "$project": {
                    "messages": 1,
                    "plug": {"$arrayElemAt": ["$plug", 0]}
                }
            },
            {
                "$match": {
                    "plug.userId": ObjectId(user_id),
                }
            },
            {
                "$unwind": "$messages"
            },
            {
                "$replaceRoot": {
                    "newRoot": "$messages"
                }
            },
            {
                "$addFields": {
                    "_id": {"$toString": "$_id"},
                }
            },
            {
                "$project": {
                    "history": 0
                }
            },
        ]
        results = History.objects().aggregate(*pipeline)
        messages = list(results)

        if not messages:
            return {"code": 404, f"message": "Message not found"}, HTTP_404_NOT_FOUND

        return {"code": 200, "data": messages[0], "message": "Message retrieved successfully"}, HTTP_200_OK

    except Exception as e:
        return {"code": 500, "message": "Failed to retrieve message", "error": str(e)}, HTTP_500_INTERNAL_SERVER_ERROR


@message.delete("/<message_id>")
@jwt_required()
def delete_message(message_id):
    try:
        user_id = get_jwt_identity()

        history_id = request.args.get('historyId')
        if not ObjectId.is_valid(history_id):
            return {"code": 400, "message": "Invalid client id"}, HTTP_400_BAD_REQUEST

        if not ObjectId.is_valid(message_id):
            return {"code": 400, "message": "Invalid message id"}, HTTP_400_BAD_REQUEST

        pipeline = [
            {
                "$match": {
                    "_id": ObjectId(history_id),
                }
            },
            {
                "$lookup": {
                    "from": "message",
                    "localField": "_id",
                    "foreignField": "history",
                    "as": "messages",
                    "pipeline": [
                        {
                            "$match": {
                                "_id": ObjectId(message_id),
                            }
                        },
                    ]
                }
            },
            {
                "$lookup": {
                    "from": "guest",
                    "localField": "guest",
                    "foreignField": "_id",
                    "as": "guest"
                }
            },
            {
                "$project": {
                    "messages": 1,
                    "guest": {"$arrayElemAt": ["$guest", 0]}
                }
            },
            {
                "$lookup": {
                    "from": "plug",
                    "localField": "guest.client",
                    "foreignField": "client._id",
                    "as": "plug"
                }
            },
            {
                "$project": {
                    "messages": 1,
                    "plug": {"$arrayElemAt": ["$plug", 0]}
                }
            },
            {
                "$match": {
                    "plug.userId": ObjectId(user_id),
                }
            },
            {
                "$unwind": "$messages"
            },
            {
                "$replaceRoot": {
                    "newRoot": "$messages"
                }
            },
            {
                "$addFields": {
                    "_id": {"$toString": "$_id"},
                }
            },
            {
                "$project": {
                    "history": 0
                }
            },
        ]
        results = History.objects().aggregate(*pipeline)
        messages = list(results)

        if not messages:
            return {"code": 404, f"message": "Message not found"}, HTTP_404_NOT_FOUND

        Message.objects(id=ObjectId(messages[0]['_id'])).delete()
        return {"code": 200, "data": messages[0], "message": "Message deleted successfully"}, HTTP_200_OK

    except Exception as e:
        return {
            "code": 500,
            "message": "Failed to delete message.",
            "error": str(e)
        }, HTTP_500_INTERNAL_SERVER_ERROR
