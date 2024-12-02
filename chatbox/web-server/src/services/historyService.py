import math

from bson.objectid import ObjectId
from src.models import Client, User, Subscription, Plug, History


def query_get_histories_by_client_id(client_id, page, page_size, user_id):
    pipeline = [
        {
            "$match": {
                "client._id": ObjectId(client_id),
                "active": True,
                "userId": ObjectId(user_id)
            }
        },
        {
            "$lookup": {
                "from": "guest",
                "localField": "client._id",
                "foreignField": "client",
                "as": "client_guests"
            }
        },
        {
            "$project": {
                "_id": 0,
                "client_guests": 1
            }
        },
        {
            "$unwind": "$client_guests"
        },

        {
            "$replaceRoot": {
                "newRoot": "$client_guests"
            }
        },
        {
            "$lookup": {
                "from": "history",
                "localField": "_id",
                "foreignField": "guest",
                "as": "guest_histories"
            }
        },
        {
            "$unwind": "$guest_histories"
        },

        {
            "$group": {
                "_id": None,
                "histories": {
                    "$push": {
                        "ip": "$ip",
                        "guestId": {"$toString": "$_id"},
                        "historyId": {"$toString": "$guest_histories._id"},
                        "createdAt": {"$toLong": {"$toDate": "$guest_histories.createdAt"}},
                        "updatedAt": {"$toLong": {"$toDate": "$guest_histories.updatedAt"}},
                        "clientId": client_id,
                    }
                },
                "total_items": {"$sum": 1}
            }
        },
        {
            "$project": {
                "_id": 0,
                "histories": 1,
                "total_items": 1
            }
        },

        {
            "$unwind": "$histories"
        },
        {
            "$sort": {
                "histories.historyId": -1
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
                "_id": None,
                "histories": {
                    "$push": "$histories"
                },
                "total_items": {"$first": "$total_items"}
            }
        },

    ]
    results = list(Plug.objects().aggregate(pipeline))
    return results


def query_message_history_paginate(user_id, client_id, history_id, page, page_size):
    pipeline = [
        {
            "$match": {
                "client._id": ObjectId(client_id),
                "active": True,
                "userId": ObjectId(user_id)
            }
        },
        {
            "$lookup": {
                "from": "guest",
                "localField": "client._id",
                "foreignField": "client",
                "as": "client_guests"
            }
        },
        {
            "$project": {
                "_id": 0,
                "client_guests": 1
            }
        },
        {
            "$unwind": "$client_guests"
        },
        {
            "$replaceRoot": {
                "newRoot": "$client_guests"
            }
        },
        {
            "$lookup": {
                "from": "history",
                "localField": "_id",
                "foreignField": "guest",
                "as": "guest_histories"
            }
        },
        {
            "$unwind": "$guest_histories"
        },
        {
            "$sort": {
                "guest_histories._id": -1
            }
        },
        {
            "$group": {
                "_id": "$_id",
                "histories": {
                    "$push": {
                        "ip": "$ip",
                        "historyId": "$guest_histories._id",
                        "createdAt": "$guest_histories.createdAt",
                        "updatedAt": "$guest_histories.updatedAt",

                    }
                }
            }
        },
        {
            "$project": {
                "_id": 0,
                "histories": 1
            }
        },
        {
            "$unwind": "$histories"
        },
        {
            "$group": {
                "_id": "$histories.historyId",
                "ip": {"$first": "$histories.ip"},
                "updatedAt": {"$first": "$histories.updatedAt"},
            }
        },
        {
            "$match": {
                "_id": ObjectId(history_id)
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
            "$addFields": {
                "total_items": {"$size": "$messages"},
            }
        },
        {
            "$project": {
                "historyId": "$_id",
                "total_items": 1,
                "messages": {
                    "$map": {
                        "input": "$messages",
                        "as": "message",
                        "in": {
                            "id": {"$toString": "$$message._id"},
                            "content": "$$message.content",
                            "role": "$$message.role"
                        }
                    }}
            }
        },
    ]
    results = list(Plug.objects().aggregate(pipeline))
    return results


def query_delete_history(user_id, client_id, history_id):
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
            "$lookup": {
                "from": "history",
                "localField": "_id",
                "foreignField": "guest",
                "as": "histories"
            }
        },
        {
            "$project": {
                "histories": 1,
            }
        },
        {
            "$unwind": "$histories"
        },
        {
            "$match": {
                "histories._id": ObjectId(history_id)
            }
        },
        {
            "$replaceRoot": {
                "newRoot": "$histories"
            }
        },
        {
            "$project": {
                "historyId": {"$toString": "$_id"},
                "createdAt": 1,
                "updatedAt": 1,
                "guest": {"$toString": "$guest"},
                "_id": 0
            }
        }
    ]
    results = list(Plug.objects().aggregate(pipeline))
    return results


def handle_get_histories_by_client_id(client_id, page, page_size, user_id):
    try:
        result = query_get_histories_by_client_id(
            client_id, page, page_size, user_id)
        if not result:
            return {
                "data": [],
                "totalItems": 0,
                "totalPage": 0,
                "page": page,
                "pageSize": page_size
            }
        total_items = result[0]["total_items"]
        return {
            "data": result[0]["histories"],
            "totalItems": total_items,
            "totalPages": math.ceil(total_items / page_size),
            "page": page,
            "pageSize": page_size
        }
    except Exception as e:
        raise e


def handle_get_history_by_id(history_id, user_id):
    pipeline = [
        {
            "$lookup": {
                "from": "guest",
                "localField": "guest",
                "foreignField": "_id",
                "as": "guest"
            },
        },
        {
            "$unwind": "$guest"
        },
        {
            "$project": {
                "historyId": "$_id",
                "createdAt": 1,
                "updatedAt": 1,
                "guest": "$guest._id",
                "client": "$guest.client",
                "ip": "$guest.ip",
            }
        },

        {
            "$lookup": {
                "from": "plug",
                "localField": "client",
                "foreignField": "client._id",
                "as": "plug"
            }
        },
        {
            "$unwind": "$plug"
        },
        {
            "$match": {
                "plug.userId": ObjectId(user_id)
            }
        },
        {
            "$project": {
                "_id": 0,
                "historyId": {"$toString": "$historyId"},
                "createdAt": 1,
                "updatedAt": 1,
                "guestId": {"$toString": "$guest"},
                "ip": "$ip",
                "clientId": {"$toString": "$client"},
            }
        }
    ]
    results = list(History.objects(id=ObjectId(history_id)).aggregate(pipeline))
    if not results:
        return None
    return results


def handle_get_history_message_by_client_id_history_id(history_id, client_id, page, page_size, user_id):
    try:
        page = int(page)
        page_size = int(page_size)
        result = query_message_history_paginate(
            user_id, client_id, history_id, page, page_size)
        if not result:
            return None
        total_items = result[0]["total_items"]
        total_pages = math.ceil(total_items / page_size)
        serialized_result = {
            "id": str(result[0]["historyId"]),
            "messages": result[0]["messages"],
            "totalItems": total_items,
            "totalPages": total_pages,
            "page": page,
            "pageSize": page_size
        }
        return serialized_result
    except Exception as e:
        raise e


def handle_delete_history(user_id, client_id, history_id):
    try:
        result = query_delete_history(user_id, client_id, history_id)
        if not result:
            return None
        else:
            history = History.objects(id=result[0]["historyId"]).first()
            history.delete()
            return result
    except Exception as e:
        raise e
