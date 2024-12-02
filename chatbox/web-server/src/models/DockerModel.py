from mongoengine import EmbeddedDocument, StringField, DateTimeField, IntField, ObjectIdField, Document
import uuid
import datetime
import pytz
from bson import ObjectId


class DockerImage(Document):
    id = ObjectIdField(primary_key=True, required=True, default=ObjectId)
    name = StringField(required=True, default="")
    imageId = StringField(required=True, default="")
    tag = StringField(required=True, default="")
    dockerFile = StringField(required=True, default="")
    createdAt = DateTimeField(
        required=True, default=datetime.datetime.now(pytz.UTC))

    def to_json(self):
        return {
            "id": str(self.id),
            "name": self.name,
            "image": self.imageId,
            "tag": self.tag,
            "createdAt": self.createdAt.timestamp(),
        }


class DockerUserConfig(Document):
    id = ObjectIdField(primary_key=True, required=True, default=ObjectId)
    userId = ObjectIdField(required=True, default=ObjectId)
    dockerConfigId = ObjectIdField(required=True, default=ObjectId)
    openaiKey = StringField()
    apifyKey = StringField()
    baseApiUrl = StringField()
    chromadbUrl = StringField()
    plugPort = StringField()
    webPort = StringField()
    uiPort = StringField()
    createdAt = DateTimeField(
        required=True, default=datetime.datetime.now(pytz.UTC))


class DockerToken(Document):
    id = ObjectIdField(primary_key=True, required=True, default=ObjectId)
    token = StringField(required=True, default="")
    refreshToken = StringField(required=True, default="")
    createdAt = DateTimeField(
        required=True, default=datetime.datetime.now(pytz.UTC))

    def to_json(self):
        return {
            "id": str(self.id),
            "token": self.token,
            "createdAt": self.createdAt.timestamp(),
        }
