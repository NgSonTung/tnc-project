from datetime import datetime, timedelta
from flask import Blueprint, request, make_response
from mongoengine import ValidationError, Q
from src.models import Plug, Message, Subscription, User, Client, Guest, History, MODEL_DICT, FEATURE_DICT
from src.constants.http_status_codes import (
    HTTP_200_OK, HTTP_201_CREATED, HTTP_400_BAD_REQUEST, HTTP_500_INTERNAL_SERVER_ERROR, HTTP_404_NOT_FOUND)
from bson.objectid import ObjectId
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.services import plugService
from calendar import month_name
from src.helper import growth, dict_to_list_of_lists
from src.config.config import URL_PATH
import pytz
import copy
from dateutil.relativedelta import relativedelta


plug = Blueprint("plug", __name__, url_prefix=f"{URL_PATH}/web/api/v1/plug")


@plug.get("")
@jwt_required()
def get_plugs():
    try:
        user_id = get_jwt_identity()
        page = request.args.get("page", 1, type=int)
        page_size = request.args.get("page_size", 10, type=int)
        result = plugService.handle_get_plugs_by_user_id(
            user_id, page, page_size)
        return {"code": 200,  **result, "message": "Plugs retrieved successfully"}, HTTP_200_OK

    except Exception as e:
        return {"code": 500, "message": "Failed to retrieve plugs", "error": str(e)}, HTTP_500_INTERNAL_SERVER_ERROR


@plug.get("/live_demo")
@jwt_required()
def get_live_demo_plugs():
    try:
        user_id = get_jwt_identity()

        plug = Plug.objects(userId=user_id, liveDemo=True).first()

        if not plug:
            return {"code": 404, "message": "Live demo not found"}, HTTP_404_NOT_FOUND

        user = User.objects(id=user_id).first()

        if not user:
            return {"code": 404, "message": "User not found"}, HTTP_404_NOT_FOUND

        # ExpiredAt to seconds
        current_datetime = datetime.utcnow()
        time_difference = user.expiredAt - current_datetime
        time_difference_seconds = time_difference.total_seconds()

        data = plug.to_json()
        data["expireAfter"] = time_difference_seconds

        return {"code": 200, "data": data, "message": "Live demo retrieved successfully"}, HTTP_200_OK

    except Exception as e:
        return {"code": 500, "message": "Failed to retrieve live demo", "error": str(e)}, HTTP_500_INTERNAL_SERVER_ERROR


@plug.get("/<plug_id>")
@jwt_required()
def get_plug(plug_id):
    try:
        user_id = get_jwt_identity()

        if not ObjectId.is_valid(plug_id):
            return {"code": 400, "message": "Invalid id"}, HTTP_400_BAD_REQUEST

        result = plugService.handle_get_plug_by_id(plug_id, user_id)
        if not plug:
            return {"code": 404, "message": "Plug not found"}, HTTP_404_NOT_FOUND

        return {"code": 200, "data": result, "message": "Plug retrieved successfully"}, HTTP_200_OK

    except Exception as e:
        return {"code": 500, "message": "Failed to retrieve plug", "error": str(e)}, HTTP_500_INTERNAL_SERVER_ERROR


@plug.post("")
@jwt_required()
def create_plug():
    try:
        data = request.json
        user_id = get_jwt_identity()

        user = User.objects(id=user_id).first()
        plug_limit = user.plugLimit
        total_plugs = Plug.objects(userId=user_id).count()

        # Check plug limit
        if total_plugs + 1 > plug_limit:
            return {"code": 400, "message": f"Exceeded plug limit of {plug_limit}"}, HTTP_400_BAD_REQUEST

        plug_name = data.get("plugName", f"Plug {total_plugs + 1}")
        if len(plug_name) == 0:
            plug_name = f"Plug {total_plugs + 1}"
        elif len(plug_name) > 20:
            return {"code": 400, "message": f"Names can't have more than 20 characters"}, HTTP_400_BAD_REQUEST

        # Check subscription
        subscription = Subscription.objects(
            id=ObjectId(user.subscriptionId)).first()
        if not subscription:
            return {"code": 400, "message": "Please subscribe to create a plug"}, HTTP_400_BAD_REQUEST

        features = subscription.features
        model = subscription.models[0]
        # if model == "gpt-4":
        model = "gpt-4"
        plug = Plug(features=features, model=model,
                    plugName=plug_name, userId=user_id)

        client = Client()
        plug.client = client
        plug.save()
        customize_features = {
        }
        print(subscription.featuresLimit)
        subscription_features_limit = subscription.featuresLimit if not None else []
        for limit in subscription_features_limit:
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
        plug_json = plug.to_json()
        plug_json['featuresLimit'] = customize_features
        return {
            "code": 201,
            "message": "Plug added successfully.",
            "data": plug_json
        }, HTTP_201_CREATED

    except ValidationError as e:
        return {"code": 400, "message": "Validation error", "error": str(e)}, HTTP_400_BAD_REQUEST
    except Exception as e:
        return {"code": 500, "message": "Failed to create plug", "error": str(e)}, HTTP_500_INTERNAL_SERVER_ERROR


@plug.patch("/<plug_id>")
@jwt_required()
def update_plug(plug_id):
    try:
        user_id = get_jwt_identity()

        if not ObjectId.is_valid(plug_id):
            return {"code": 400, "message": "Invalid id"}, HTTP_400_BAD_REQUEST

        user = User.objects(id=user_id).first()
        if not user:
            return {"code": 404, "message": "User not found"}, HTTP_404_NOT_FOUND

        data = request.json

        plug = Plug.objects(id=ObjectId(
            oid=plug_id), userId=user_id).first()

        if not plug:
            return {"code": 404, "message": "Plug not found"}, HTTP_404_NOT_FOUND

        if not plug.active:
            return {"code": 400, "message": "Plug is not active"}, HTTP_400_BAD_REQUEST

        # user can only modify these fields
        modifiable_fields = ["model", "plugName", "isAutoCreateMap", "userKey"]

        subscription = Subscription.objects(
            id=ObjectId(user.subscriptionId)).first()
        if not subscription:
            return {"code": 400, "message": "Please subscribe to update a plug"}, HTTP_400_BAD_REQUEST

        model = data.get("model", None)
        if model and model not in subscription.models:
            return {"code": 400, "message": "The user's subscription doesn't have that llm"}, HTTP_400_BAD_REQUEST
        if model == "gpt-3.5":
            model = "gpt-4"

        for field in data:
            if field in modifiable_fields:
                if field in plug._fields:
                    field_value = data[field]
                    if field_value is not None:
                        if field == "messages":
                            messages = [Message(**message)
                                        for message in field_value]
                            plug[field] = messages
                        else:
                            plug[field] = field_value
        plug.save()

        return {
            "code": 200,
            "data": plug.to_json(),
            "message": "Plug updated successfully."
        }, HTTP_200_OK

    except ValidationError as e:
        return {
            "code": 500,
            "message": "Validation error",
            "error": str(e)}, HTTP_400_BAD_REQUEST

    except Exception as e:
        return {
            "code": 500,
            "message": "Failed to update plug.",
            "error": str(e)
        }, HTTP_500_INTERNAL_SERVER_ERROR


@plug.delete("/<plug_id>")
@jwt_required()
def delete_plug(plug_id):
    try:
        user_id = get_jwt_identity()
        plug = Plug.objects(id=plug_id, userId=user_id).first()
        if not plug:
            return {
                "code": 404,
                "message": "Plug not found"
            }, HTTP_404_NOT_FOUND

        plug.delete()
        list_plugs = Plug.objects(userId=user_id)
        if len(list_plugs) >= 1:
            list_plugs.order_by("-id")
            user = User.objects(id=user_id).first()
            for i in range(0, len(list_plugs)):
                if not list_plugs[i].active and i < user.plugLimit:
                    list_plugs[i].update(active=True)
                    break
        return {
            "code": 200,
            "data": plug.to_json(),
            "message": "Plug deleted successfully."
        }, HTTP_200_OK

    except Exception as e:
        return {
            "code": 500,
            "message": "Failed to delete plug.",
            "error": str(e)
        }, HTTP_500_INTERNAL_SERVER_ERROR


@plug.get("/key/<plug_key>")
def get_plug_by_key(plug_key):
    try:
        plug_key = plug_key

        if not plug_key:
            return {"code": 400, "message": "Invalid plug key"}, HTTP_400_BAD_REQUEST

        plug = Plug.objects(key=plug_key).first()
        plug.createdAt = plug.createdAt.timestamp()
        if not plug:
            return {"code": 404, "message": "Plug not found"}, HTTP_404_NOT_FOUND

        return {"code": 200, "data": plug.to_json(), "message": "Plug retrieved successfully"}, HTTP_200_OK

    except Exception as e:
        return {"code": 500, "message": "Failed to retrieve plug", "error": str(e)}, HTTP_500_INTERNAL_SERVER_ERROR


@plug.get("/export/<plug_id>")
@jwt_required()
def export_plug(plug_id):
    try:
        user_id = get_jwt_identity()
        user = User.objects(id=user_id).first()
        if user is None:
            return {"code": 404, "message": "User not found"}, HTTP_404_NOT_FOUND
        plug = Plug.objects(id=plug_id, userId=user_id).first()
        if plug is None:
            return {"code": 404, "message": "Plug not found"}, HTTP_404_NOT_FOUND
        markdown_content = "".join(
            f"{message.content}" for message in plug.messages)
        response = make_response(markdown_content)
        response.headers['Content-Type'] = 'text/markdown'
        response.headers['Content-Disposition'] = f'attachment; filename="{plug.id}.md"'
        return response
    except Exception as e:
        return {
            "code": 500,
            "message": "Failed to export plug.",
            "error": str(e)
        }, HTTP_500_INTERNAL_SERVER_ERROR


@plug.get("/analytics/<plug_id>")
@jwt_required()
def get_analytics(plug_id):
    try:
        user_id = get_jwt_identity()
        user = User.objects(id=user_id).first()
        if user is None:
            return {"code": 404, "message": "User not found"}, HTTP_404_NOT_FOUND
        plug = Plug.objects(id=ObjectId(plug_id), userId=user_id).first()
        if not plug:
            return {"code": 404, "message": "Plug not found"}, HTTP_404_NOT_FOUND
        guests = list(Guest.objects(client=plug.client.id))

        current_date = datetime.now(pytz.UTC).replace(
            hour=0, minute=0, second=0, microsecond=0, tzinfo=None)

        first_day_of_month = current_date.replace(day=1)
        next_month = first_day_of_month + relativedelta(months=1)
        last_month = first_day_of_month - relativedelta(months=1)

        last_month_guest_dict = {}
        current_month_guest_dict = {}

        current_day_last_month = last_month
        current_day = first_day_of_month
        while current_day_last_month < first_day_of_month:
            timestamp = current_day_last_month.timestamp()
            last_month_guest_dict[timestamp] = 0
            current_day_last_month += timedelta(days=1)

        while current_day < next_month:
            timestamp = current_day.timestamp()
            current_month_guest_dict[timestamp] = 0
            current_day += timedelta(days=1)

        current_month_history_dict = copy.deepcopy(current_month_guest_dict)
        last_month_history_dict = copy.deepcopy(last_month_guest_dict)

        current_month_duration_dict = copy.deepcopy(current_month_guest_dict)
        last_month_duration_dict = copy.deepcopy(last_month_guest_dict)

        last_month_guests = 0
        this_month_guests = 0
        guest_ids = []

        # Iterate and count each day
        for guest in guests:
            guest_ids.append(guest.id)
            day = guest.createdAt.replace(
                hour=0, minute=0, second=0, microsecond=0).timestamp()
            if guest.createdAt.month == last_month.month:
                if day in last_month_guest_dict:
                    last_month_guest_dict[day] += 1
                    last_month_guests += 1
            elif guest.createdAt.month == first_day_of_month.month:
                if day in current_month_guest_dict:
                    current_month_guest_dict[day] += 1
                    this_month_guests += 1

        last_month_histories = 0
        this_month_histories = 0

        last_month_duration = 0
        this_month_duration = 0

        histories = list(History.objects(Q(guest__in=guest_ids)))
        for history in histories:
            duration = history.updatedAt.timestamp() - history.createdAt.timestamp()
            day = history.createdAt.replace(
                hour=0, minute=0, second=0, microsecond=0).timestamp()
            if history.createdAt.month == last_month.month:
                if day in last_month_history_dict:
                    last_month_histories += 1
                    last_month_history_dict[day] += 1
                if day in last_month_duration_dict:
                    last_month_duration_dict[day] += duration
                    last_month_duration += duration
            elif history.createdAt.month == first_day_of_month.month:
                if day in current_month_history_dict:
                    this_month_histories += 1
                    current_month_history_dict[day] += 1
                if day in current_month_duration_dict:
                    current_month_duration_dict[day] += duration
                    this_month_duration += duration

        current_duration_key_list = list(current_month_duration_dict.keys())
        last_duration_key_list = list(last_month_duration_dict.keys())
        for i in range(len(current_duration_key_list)):
            index = current_duration_key_list[i]
            history_num = 0
            if index in current_month_history_dict:
                history_num = current_month_history_dict[index]
            if history_num != 0 and index in current_month_duration_dict:
                current_month_duration_dict[index] /= history_num
        for i in range(len(last_duration_key_list)):
            index = last_duration_key_list[i]
            history_num = 0
            if index in last_month_history_dict:
                history_num = last_month_history_dict[index]
            if history_num != 0 and index in last_month_duration_dict:
                last_month_duration_dict[index] /= history_num
        data = {
            'graph1': {
                'series': [
                    {
                        'name': f"{month_name[current_date.month]}",
                        'data': dict_to_list_of_lists(current_month_history_dict)
                    },
                    {
                        'name':  f"{month_name[last_month.month]}",
                        'data': dict_to_list_of_lists(last_month_history_dict)
                    },
                ],
                'total': last_month_histories + this_month_histories,
                'growth': growth(last_month_histories, this_month_histories),
            },
            'graph2': {
                'series': [
                    {
                        'name': f"{month_name[current_date.month]}",
                        'data': dict_to_list_of_lists(current_month_guest_dict)
                    },
                    {
                        'name':  f"{month_name[last_month.month]}",
                        'data': dict_to_list_of_lists(last_month_guest_dict)
                    },
                ],
                'total': last_month_guests + this_month_guests,
                'growth': growth(last_month_guests, this_month_guests),
            },
            'graph3': {
                'series': [
                    {
                        'name': f"{month_name[current_date.month]}",
                        'data': dict_to_list_of_lists(current_month_duration_dict)
                    },
                    {
                        'name':  f"{month_name[last_month.month]}",
                        'data': dict_to_list_of_lists(last_month_duration_dict)
                    },
                ],
                'average': (this_month_duration + last_month_duration) / (last_month_histories + this_month_histories) if (last_month_histories + this_month_histories) != 0 else 0,
                'growth': growth(last_month_duration, this_month_duration),
            }
        }

        return {"code": 200, "data": data, "message": "Analytics retrieved successfully"}, HTTP_200_OK

    except Exception as e:
        return {
            "code": 500,
            "message": "Failed to retrieved analytics.",
            "error": str(e)
        }, HTTP_500_INTERNAL_SERVER_ERROR
