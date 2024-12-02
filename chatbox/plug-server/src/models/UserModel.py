from bson import ObjectId
from mongoengine import Document, StringField, ObjectIdField, IntField, DateTimeField, signals, BooleanField, \
    EmbeddedDocumentListField, EmbeddedDocument, EmailField
import sys
import os

sys.path.append(os.path.abspath(os.path.join('src', 'config')))
from config import USER

sys.path.append(os.path.abspath(os.path.join('src', 'models')))
from SubscriptionModel import Subscription
from PlugModel import Plug

# from src.helper.user_subscription import get_subscription_name
roles = ["0", "1"]


class UserKey(EmbeddedDocument):
    id = ObjectIdField(required=True, default=ObjectId())
    key = StringField(required=True, default="Default")
    active = BooleanField(required=True, default=False)
    isDefault = BooleanField(required=True, default=False)
    meta = {"collection": "UserKey"}

    def format_key(self):
        return (self.key[:3] + '*' * (len(self.key) - 6) + self.key[-4:]) if not self.isDefault else self.key

    def to_json(self):
        return {
            "id": str(self.id),
            "key": self.format_key(),
            "active": self.active,
            "isDefault": self.isDefault
        }


class User(Document):
    id = ObjectIdField(primary_key=True, required=True, default=ObjectId)
    userName = StringField(required=True, unique=True)
    email = EmailField(required=True, unique=True)
    firstName = StringField(default=None)
    lastName = StringField(default=None)
    password = StringField(required=True)
    role = StringField(required=True, choices=roles, default=USER)
    subscriptionId = ObjectIdField(
        default=ObjectId("64aff45ae43f3103d2fa22e0"))  # free subscription
    plugLimit = IntField(required=True, default=1)
    stripePortal = StringField(default=None)
    expiredAt = DateTimeField()
    liveDemo = BooleanField(default=False)
    trial = BooleanField(default=False)
    userKeys = EmbeddedDocumentListField(UserKey, default=[UserKey(active=True, isDefault=True)])
    stripeCustomerId = StringField(default=None)
    subExpiredAt = DateTimeField()
    meta = {"collection": "user"}

    def to_json(self):
        return {
            "id": str(self.id),
            "userName": self.userName,
            "firstName": self.firstName,
            "lastName": self.lastName,
            "email": self.email,
            "subscriptionRole": Subscription.objects(id=self.subscriptionId).first().name,
            "subExpiredAt": str(self.subExpiredAt) if self.subExpiredAt else None,
            "stripeCustomerId": self.stripeCustomerId,
            "liveDemo": self.liveDemo,
            "plugLimit": self.plugLimit,
            "trial": self.trial
        }

    @classmethod
    def post_delete_hook(self, sender, document, **kwargs):
        if kwargs.get('deleted', True):
            try:
                Plug.objects(userId=document.id).delete()
            except:
                return


signals.post_delete.connect(User.post_delete_hook, sender=User)
