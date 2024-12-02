from mongoengine import StringField, Document, ObjectIdField, signals, DateTimeField
import sys
import os
import datetime
import pytz
from bson import ObjectId
sys.path.append(os.path.abspath(os.path.join('src', 'models')))
from HistoryModel import History


class Guest(Document):
    id = ObjectIdField(primary_key=True, required=True, default=ObjectId)
    createdAt = DateTimeField(
        required=True, default=datetime.datetime.now(pytz.UTC))
    ip = StringField(required=True)
    client = ObjectIdField(required=True)
    meta = {
        "collection": "guest",
        'indexes': ['client']
    }

    def to_json(self):
        return {
            "id": str(self.id),
            "ip": self.ip,
            "createdAt": self.createdAt.timestamp(),
            "client": str(self.client),
        }

    @classmethod
    def post_delete_hook(self, sender, document, **kwargs):
        if kwargs.get('deleted', True):
            try:
                # Delete guest
                History.objects(client=document.id).delete()
            except:
                return


signals.post_delete.connect(Guest.post_delete_hook, sender=Guest)
