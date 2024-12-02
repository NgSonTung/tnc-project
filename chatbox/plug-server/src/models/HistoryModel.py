from mongoengine import Document, ObjectIdField, DateTimeField, signals
import sys
import os
import datetime
import pytz
from bson import ObjectId
sys.path.append(os.path.abspath(os.path.join('src', 'models')))
from MessageModel import Message


class History(Document):
    id = ObjectIdField(primary_key=True, required=True, default=ObjectId)
    createdAt = DateTimeField(
        required=True, default=datetime.datetime.now(pytz.UTC))
    updatedAt = DateTimeField(
        required=True, default=datetime.datetime.now(pytz.UTC))
    guest = ObjectIdField(required=True)
    meta = {
        "collection": "history",
        'indexes': ['guest']
    }

    def to_json(self):
        return {
            "id": str(self.id),
            "createdAt": self.createdAt.timestamp(),
            "updatedAt": self.updatedAt.timestamp(),
            "guest": str(self.guest),
        }

    @classmethod
    def post_delete_hook(self, sender, document, **kwargs):
        if kwargs.get('deleted', True):
            try:
                # Delete guest
                Message.objects(client=document.id).delete()
            except:
                return


signals.post_delete.connect(History.post_delete_hook, sender=History)
