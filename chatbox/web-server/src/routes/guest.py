from flask import Blueprint, request
from src.models import Guest, Plug
from src.constants.http_status_codes import (
    HTTP_200_OK, HTTP_400_BAD_REQUEST, HTTP_500_INTERNAL_SERVER_ERROR, HTTP_404_NOT_FOUND
)
from bson.objectid import ObjectId
from flask_jwt_extended import jwt_required, get_jwt_identity
import math
from src.config.config import URL_PATH
guest = Blueprint("guest", __name__, url_prefix=f"{URL_PATH}/web/api/v1/guest")


@guest.get("")
@jwt_required()
def get_guests():
    try:
        user_id = get_jwt_identity()

        client_id = request.args.get('clientId')
        if not ObjectId.is_valid(client_id):
            return {"code": 400, "message": "Invalid client id"}, HTTP_400_BAD_REQUEST

        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('pageSize', 10))
        if page_size > 30:
            page_size = 30

        pipeline = [
            {
                "$match": {
                    "client._id": ObjectId(client_id),
                    "userId": ObjectId(user_id),
                    "active": True,
                }
            },
            {
                "$lookup": {
                    "from": "guest",
                    "localField": "client._id",
                    "foreignField": "client",
                    "as": "guests"
                }
            },
            {
                "$addFields": {
                    "totalDocuments": {"$size": "$guests"},
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "totalDocuments": 1,
                    "guests": {
                        "$map": {
                            "input": "$guests",
                            "as": "guest",
                            "in": {
                                "_id": "$$guest._id",
                                "ip": "$$guest.ip"
                            }
                        }}
                }
            },
            {
                "$unwind": "$guests"
            },
            {
                "$addFields": {
                    "guests._id": {"$toString": "$guests._id"}
                }
            },
            {
                "$sort": {
                    "guests._id": -1
                }
            },
            {
                "$skip": (page - 1) * page_size
            },
            {
                "$limit": page_size
            },
            {
                "$group": {
                    "_id": "$_id",
                    "totalDocuments": {"$first": "$totalDocuments"},
                    "guests": {"$push": "$guests"}
                }
            },
            {
                "$project": {
                    "_id": 0,
                }
            }
        ]

        results = list(Plug.objects().aggregate(*pipeline))
        if results:
            total_documents = results[0]['totalDocuments']
            total_pages = math.ceil(total_documents / page_size)
            guests = results[0]['guests']
        else:
            total_documents = 0
            total_pages = 0
            guests = []

        return {"code": 200, "data": guests, "page": page * 1, "pageSize": page_size * 1, "totalPages": total_pages * 1,   "totalItems": total_documents, "message": "Guests retrieved successfully"}, HTTP_200_OK

    except Exception as e:
        return {"code": 500, "message": "Failed to retrieve guests", "error": str(e)}, HTTP_500_INTERNAL_SERVER_ERROR


@guest.get("/<guest_id>")
@jwt_required()
def get_guest_by_id(guest_id):
    try:
        user_id = get_jwt_identity()

        client_id = request.args.get('clientId')
        if not ObjectId.is_valid(client_id):
            return {"code": 400, "message": "Invalid client id"}, HTTP_400_BAD_REQUEST

        if not ObjectId.is_valid(guest_id):
            return {"code": 400, "message": "Invalid guest id"}, HTTP_400_BAD_REQUEST

        pipeline = [
            {
                "$match": {
                    "client._id": ObjectId(client_id),
                    "userId": ObjectId(user_id),
                    "active": True,
                }
            },
            {
                "$lookup": {
                    "from": "guest",
                    "localField": "client._id",
                    "foreignField": "client",
                    "as": "guests"
                }
            },
            {
                "$project": {
                    "guests": 1,
                    "_id": 0
                }
            },
            {
                "$unwind": "$guests"
            },
            {
                "$replaceRoot": {
                    "newRoot": "$guests"
                }
            },
            {
                "$match": {
                    "_id": ObjectId(guest_id)
                }
            },
            {
                "$addFields": {
                    "client": {"$toString": "$client"},
                    "_id": {"$toString": "$_id"}
                }
            },
            {
                "$project": {
                    "client": 0,
                }
            }
        ]
        results = Plug.objects().aggregate(*pipeline)
        guests = list(results)

        if not guests:
            return {"code": 404, f"message": "Guest not found"}, HTTP_404_NOT_FOUND

        return {"code": 200, "data": guests[0], "message": "Guest retrieved successfully"}, HTTP_200_OK

    except Exception as e:
        return {"code": 500, "message": "Failed to retrieve guest", "error": str(e)}, HTTP_500_INTERNAL_SERVER_ERROR


@guest.delete("/<guest_id>")
@jwt_required()
def delete_guest(guest_id):
    try:
        user_id = get_jwt_identity()

        client_id = request.args.get('clientId')
        if not ObjectId.is_valid(client_id):
            return {"code": 400, "message": "Invalid client id"}, HTTP_400_BAD_REQUEST

        if not ObjectId.is_valid(guest_id):
            return {"code": 400, "message": "Invalid guest id"}, HTTP_400_BAD_REQUEST

        pipeline = [
            {
                "$match": {
                    "client._id": ObjectId(client_id),
                    "userId": ObjectId(user_id),
                    "active": True,
                }
            },
            {
                "$lookup": {
                    "from": "guest",
                    "localField": "client._id",
                    "foreignField": "client",
                    "as": "guests"
                }
            },
            {
                "$project": {
                    "guests": 1,
                    "_id": 0
                }
            },
            {
                "$unwind": "$guests"
            },
            {
                "$replaceRoot": {
                    "newRoot": "$guests"
                }
            },
            {
                "$match": {
                    "_id": ObjectId(guest_id)
                }
            },
            {
                "$addFields": {
                    "client": {"$toString": "$client"},
                    "_id": {"$toString": "$_id"}
                }
            },
            {
                "$project": {
                    "client": 0,
                }
            }
        ]
        results = Plug.objects().aggregate(*pipeline)
        guests = list(results)

        if not guests:
            return {"code": 404, f"message": "Guest not found"}, HTTP_404_NOT_FOUND

        Guest.objects(id=ObjectId(guests[0]['_id'])).delete()
        return {"code": 200, "data": guests[0], "message": "Guest deleted successfully"}, HTTP_200_OK

    except Exception as e:
        return {
            "code": 500,
            "message": "Failed to delete guest.",
            "error": str(e)
        }, HTTP_500_INTERNAL_SERVER_ERROR
