from src.models import Client, User, Subscription, Plug, History, Message
from bson import ObjectId
import math


def query_history_client_by_message(client_id, page, page_size, regex_filter, user_id):
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
                        "createdAt": {"$toLong": {"$toDate": "$guest_histories.createdAt"}},
                        "updatedAt": {"$toLong": {"$toDate": "$guest_histories.updatedAt"}},

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
                "createdAt": {"$first": "$histories.createdAt"},
                "updatedAt": {"$first": "$histories.updatedAt"},
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
            "$match": {
                "messages.content": {**regex_filter}  # Filter for messages with the desired content
            }
        },
        {
            "$project": {
                "messages": 0
            }
        },

        {
            "$group": {
                "_id": None,
                "histories": {
                    "$push": {
                        "historyId": {"$toString": "$_id"},
                        "ip": "$ip",
                        "createdAt": "$createdAt",
                        "updatedAt": "$updatedAt"
                    }
                },
                "total_items": {
                    "$sum": 1
                }
            }
        },
        {
            "$addFields": {
                "total_items": {
                    "$size": "$histories"
                }
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
        }
    ]

    result = list(Plug.objects().aggregate(pipeline))
    return result


def handle_search_client_message(page, page_size, client_id, message_content, user_id):
    try:
        message_regex = f"(?i){message_content}"  # Case-insensitive regex pattern
        regex_filter = {
            "$regex": message_regex,
            "$options": "i"
        }

        result = query_history_client_by_message(client_id, page, page_size, regex_filter, user_id)
        if not result:
            return {
                "data": [],
                "totalItems": 0,
                "totalPage": 1,
                "page": 1,
                "pageSize": page_size
            }
        total_page = math.ceil(result[0]["total_items"] / page_size)

        serialized_result = {
            "data": result[0]["histories"],
            "totalItems": result[0]["total_items"],
            "totalPage": total_page,
            "page": page,
            "pageSize": page_size
        }
        return serialized_result
    except Exception as e:
        raise e
