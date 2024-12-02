from mongoengine import EmbeddedDocument, StringField, DateTimeField, IntField, ObjectIdField
import uuid
import datetime
import pytz
from bson import ObjectId


def generate_default_key():
    return "sk-" + str(uuid.uuid4())


class Client(EmbeddedDocument):
    id = ObjectIdField(primary_key=True, required=True, default=ObjectId)
    key = StringField(required=True, default=generate_default_key)
    origin = StringField(required=True, default="")
    token = IntField(required=True, default=0)
    createdAt = DateTimeField(
        required=True, default=datetime.datetime.now(pytz.UTC))

    def to_json(self):
        return {
            "id": str(self.id),
            "key": self.key,
            "token": self.token,
            "origin": self.origin,
            "createdAt": self.createdAt.timestamp(),
        }
