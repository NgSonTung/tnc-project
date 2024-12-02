from mongoengine import (
    Document,
    StringField,
    IntField,
    ListField,
    BooleanField,
    DateTimeField,
)
from bson import ObjectId
class PaymentInvoice(Document):
    stripeInvoiceId = StringField(required=True, unique=True)
    paymentIntentId = StringField(required=True, default="")
    stripePriceId = StringField(required=True, default="")
    stripeCustomerId = StringField(required=True, default="")
    amount =IntField(required=True, default=0)
    currency = StringField(required=True, default="usd")
    status = StringField(required=True, default="draft")
    collectionMethod = StringField(required=True, default="charge_automatically")
    periodStart = DateTimeField(required=True, default="")
    periodEnd = DateTimeField(required=True, default="")
    detailHostUrl = StringField(required=True, default="")
    detailUrl = StringField(required=True, default="")
    updatedAt = DateTimeField(required=True, default="")

    def to_json(self):
        return {
            "id": str(self.pk),
            "stripeInvoiceId": self.stripeInvoiceId,
            "paymentIntentId": str(self.paymentIntentId),
            "stripePriceId": self.stripePriceId,
            "stripeCustomerId": self.stripeCustomerId,
            "amount": self.amount,
            "currency": self.currency,
            "status": self.status,
            "collectionMethod": self.collectionMethod,
            "periodStart": self.periodStart,
            "periodEnd": self.periodEnd,
            "detailHostUrl": self.detailHostUrl,
            "detailUrl": self.detailUrl,
            "updatedAt": self.updatedAt.timestamp(),
        }