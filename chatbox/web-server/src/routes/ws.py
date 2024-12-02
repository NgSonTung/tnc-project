from flask_socketio import SocketIO, join_room
from flask import Blueprint, request
from src.config.config import URL_PATH
from dotenv import load_dotenv
import os
import json

load_dotenv()
flask_env = os.environ.get("FLASK_ENV")

path = f"{URL_PATH}/web/socket.io"[1:]
socketio = SocketIO(path=path, cors_allowed_origins="*",
                    logger=True if flask_env == 'development' else False,
                    engineio_logger=True if flask_env == 'development' else False)

websocket = Blueprint("websocket", __name__,
                      url_prefix=f"{URL_PATH}/web/api/v1/websocket")


def progressUpdate(progress, is_file, message, room, context_item={}):
    response = {**context_item, 'progress': progress,
                'isFile': is_file, 'message': message}
    print("progressUpdate",message)
    socketio.emit('context_item_upload', response, broadcast=True, to=room)
    socketio.sleep(0)


def statusUpdate(is_file, message, room, context_item={}, event="message"):
    response = {**context_item, 'isFile': is_file, 'message': message}
    print("statusUpdate",message)
    socketio.emit(event, response, broadcast=True, to=room)
    socketio.sleep(0)


@socketio.on('connect')
def connect():
    return


@socketio.on('join')
def join(data):
    join_room(data['user_id'])
    return


@websocket.route("notify", methods=["POST"])
def notify():
    body = request.json
    event_type = body.get("eventType")
    room = body.get("room")
    context_item = body.get("contextItem")

    response = {**context_item, 'isFile': False}

    if event_type == 'ACTOR.RUN.CREATED':
        response['message'] = 'Run initiated'
        response['progress'] = 30
    elif event_type == 'ACTOR.RUN.SUCCEEDED' or event_type == 'ACTOR.RUN.TIMED_OUT':
        response['message'] = 'Run finished'
        response['progress'] = 50
    elif event_type == 'ACTOR.RUN.ABORTED':
        response['message'] = 'Run aborted'
        response['progress'] = 50
    elif event_type == 'ACTOR.BUILD.FAILED':
        response['message'] = 'Run failed'
        response['progress'] = 100

    socketio.send(response, broadcast=True, to=room)
    return "ok", 200
