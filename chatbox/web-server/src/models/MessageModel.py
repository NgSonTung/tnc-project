import pytz
from mongoengine import StringField, Document, ObjectIdField, DateTimeField
import os
import sys
import datetime
sys.path.append(os.path.abspath(os.path.join('src', 'models')))


ROLES = ["system", "user", "assistant", "function"]


class Message(Document):
    type = StringField()
    content = StringField(required=True)
    role = StringField(required=True, choices=ROLES, message="Invalid role")
    history = ObjectIdField(required=True)
    createdAt = DateTimeField(required=True, default=datetime.datetime.now(pytz.UTC))
    meta = {
        "collection": "message",
        'indexes': ['history', 'content']
    }
    
    def to_json(self):
            return {
                "content": self.content,
                "type": self.type,
                "role": self.role,
                "createdAt": self.createdAt.timestamp(),
            }

