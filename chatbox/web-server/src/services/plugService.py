import math
from src.models import Plug, Subscription, FEATURE_DICT, MODEL_DICT
from bson import ObjectId


def query_plugs_by_user_id(user_id, page, page_size):
    pipeline = [
        {
            '$match': {
                'userId': ObjectId(user_id),
            }
        },
        {
            "$project": {
                "prompt": 0
            }
        },
        {
            "$lookup": {
                "from": "user",
                "localField": "userId",
                "foreignField": "_id",
                "as": "user"
            }
        },
        {
            "$unwind": "$user"
        },
        {
            "$lookup": {
                "from": "subscription",
                "localField": "user.subscriptionId",
                "foreignField": "_id",
                "as": "subscription"
            }
        },
        {
            "$unwind": "$subscription"
        },
        {
            "$addFields": {
                "featuresLimit": "$subscription.featuresLimit",
            }
        },
        {
            "$project": {
                "subscription": 0,
                "user": 0
            }
        },
        {
            "$sort": {
                "_id": -1
            }
        },
        {
            "$group": {
                "_id": None,
                "plugs": {
                    "$push": "$$ROOT"
                },
                "total_items": {"$sum": 1}
            }
        },
        {
            "$unwind": "$plugs"
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
                "plugs": {
                    "$push": {
                        "id": {"$toString": "$plugs._id"},
                        "plugName": "$plugs.plugName",
                        "model": "$plugs.model",
                        "token": "$plugs.token",
                        "liveDemo": "$plugs.liveDemo",
                        "isAutoCreateMap": "$plugs.isAutoCreateMap",
                        "active": "$plugs.active",
                        "createdAt": {"$toLong": {"$toDate": "$plugs.createdAt"}},
                        "updatedAt": {"$toLong": {"$toDate": "$plugs.updatedAt"}},
                        "featuresLimit": "$plugs.featuresLimit",
                        "userId": {"$toString": "$plugs.userId"},
                        "client": {
                            "id": {"$toString": "$plugs.client._id"},
                            "name": "$plugs.client.name",
                            "key": "$plugs.client.key",
                            "token": "$plugs.client.token",
                            "origin": "$plugs.client.origin",
                            "createdAt": {"$toLong": {"$toDate": "$plugs.client.createdAt"}},
                        },

                    }
                },

                "total_items": {"$first": "$total_items"}
            }
        },

    ]
    result = list(Plug.objects().aggregate(*pipeline))
    return result


def query_plug_by_id(plug_id, user_id):
    pipeline = [
        {
            '$match': {
                'userId': ObjectId(user_id),
                '_id': ObjectId(plug_id)
            }
        },
        {
            "$project": {
                "prompt": 0
            }
        },
        {
            "$lookup": {
                "from": "user",
                "localField": "userId",
                "foreignField": "_id",
                "as": "user"
            }
        },
        {
            "$unwind": "$user"
        },
        {
            "$lookup": {
                "from": "subscription",
                "localField": "user.subscriptionId",
                "foreignField": "_id",
                "as": "subscription"
            }
        },
        {
            "$unwind": "$subscription"
        },
        {
            "$addFields": {
                "featuresLimit": "$subscription.featuresLimit",
                "id": "$_id"
            }
        },
        {
            "$project": {
                "id": {"$toString": "$_id"},
                "createdAt": {"$toLong": {"$toDate": "$createdAt"}},
                "updatedAt": {"$toLong": {"$toDate": "$updatedAt"}},

                "plugName": 1,
                "model": 1,
                "token": 1,
                "liveDemo": 1,
                "active": 1,
                "featuresLimit": 1,
                "isAutoCreateMap": 1,
                "userId": {"$toString": "$userId"},
                "client": {
                    "id": {"$toString": "$client._id"},
                    "name": "$client.name",
                    "key": "$client.key",
                    "token": "$client.token",
                    "origin": "$client.origin",
                    "createdAt": "$client.createdAt",
                },
            },
        },
        {
            "$project": {
                "_id": 0,
            }
        }
    ]
    result = list(Plug.objects(id=ObjectId(plug_id)).aggregate(*pipeline))
    return result


def handle_get_plugs_by_user_id(user_id, page, page_size):
    try:
        result = query_plugs_by_user_id(user_id, page, page_size)
        if not result:
            return {
                "data": [],
                "totalItems": 0,
                "totalPage": 0,
                "page": page,
                "pageSize": page_size
            }
        total_page = math.ceil(result[0]["total_items"] / page_size)
        features_limit = result[0]["plugs"][0]["featuresLimit"]
        customize_features = {
        }
        for limit in features_limit:
            if limit['name'] == "gpt-3.5" or limit['name'] == "gpt-4":
                if limit['name'] == "gpt-3.5":
                    limit['name'] = "gpt-4"
                limit['name'] = MODEL_DICT.get(limit['name'])
            else:
                limit['name'] = FEATURE_DICT.get(limit['name'])
            feature = {
                f"{limit['name']}": {
                    "limit": int(limit['limit']) if not limit['unlimited'] and 'gpt' not in limit['name'] else -1,
                    "active": True,
                    "unlimited": limit['unlimited']
                }
            }
            customize_features.update(feature)
        for item in result[0]["plugs"]:
            item["featuresLimit"] = customize_features
        return {
            "data": result[0]["plugs"],
            "totalItems": result[0]["total_items"],
            "totalPage": total_page,
            "page": page,
            "pageSize": page_size
        }

    except Exception as e:
        raise e


def handle_get_plug_by_id(plug_id, user_id):
    try:
        result = query_plug_by_id(plug_id, user_id)
        if not result:
            return None
        customize_features = {
        }
        features_limit = result[0]["featuresLimit"]
        for limit in features_limit:
            if limit['name'] == "gpt-3.5" or limit['name'] == "gpt-4":
                if limit['name'] == "gpt-3.5":
                    limit['name'] = "gpt-4"
                limit['name'] = MODEL_DICT.get(limit['name'])
            else:
                limit['name'] = FEATURE_DICT.get(limit['name'])

            feature = {
                f"{limit['name']}": {
                    "limit": int(limit['limit']) if not limit['unlimited'] and 'gpt' not in limit['name'] else -1,
                    "active": True,
                    "unlimited": limit['unlimited']
                }
            }
            customize_features.update(feature)
        result[0]["featuresLimit"] = customize_features
        return result[0]
    except Exception as e:
        raise e
