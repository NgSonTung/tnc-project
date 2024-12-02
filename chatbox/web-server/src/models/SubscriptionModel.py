import pytz
from mongoengine import (
    Document, StringField, FloatField, ListField, BooleanField, IntField, EmbeddedDocument, EmbeddedDocumentListField,DateTimeField)
import datetime

class FeatureLimit(EmbeddedDocument):
    name = StringField(required=True)
    description = StringField(required=True, default="")
    limit = IntField(default=-1)
    unlimited = BooleanField(default=False)
    meta = {"collection": "subscriptionFeature"}

    def to_json(self):
        return {
            "name": self.name,
            "description": self.description,
            "limit": None if self.limit == "None" else int(self.limit),
            "unlimited": self.unlimited,
        }


class Subscription(Document):
    name = StringField(required=True)
    stripeSubscriptionId = StringField(required=True)
    stripePriceId = StringField(required=True, unique=True)
    description = StringField(required=True, default="")
    models = ListField(StringField(), required=True)
    features = ListField(StringField())
    cost = FloatField(required=True)
    currency = StringField(required=True, default="usd")
    featuresLimit = EmbeddedDocumentListField(FeatureLimit, default=[])
    plugLimit = IntField(required=True, default=1)
    active = BooleanField(required=True, default=False)
    comingSoon = BooleanField(default=False)
    isYearly = BooleanField(default=False)
    updatedAt = DateTimeField(required=True, default=datetime.datetime.now(pytz.UTC))
    meta = {"collection": "subscription"}

    def to_json(self):
        return {
            "id": str(self.pk),
            "name": self.name,
            "description": self.description,
            "cost": str(self.cost),
            "features": self.features,
            "models": self.models,
            "stripeSubscriptionId": self.stripeSubscriptionId,
            "stripePriceId": self.stripePriceId,
            "currency": self.currency,
            "featuresLimit": [feature.to_json() for feature in self.featuresLimit],
            "plugLimit": self.plugLimit,
            "active": self.active,
            "isYearly": self.isYearly,
            "comingSoon": self.comingSoon,
            "updatedAt": self.updatedAt.timestamp(),

        }
