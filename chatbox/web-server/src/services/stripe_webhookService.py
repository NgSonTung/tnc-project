import stripe
import datetime

from src.models import Subscription, User, Plug, PaymentInvoice
from src.config.config import STRIPE_API_SECRET_KEY
from src.helper.converter_datetime import convert_timestamp_to_datetime
from src.helper.plug_helper import sort_plug_date
from src.constants.http_status_codes import HTTP_200_OK
from bson import ObjectId

stripe.api_key = STRIPE_API_SECRET_KEY


# subcription is a stripe product

# more handle for exception
def handle_product(product, event):
    try:
        price_id = product.default_price
        if price_id is not None:
            price = stripe.Price.retrieve(price_id)
        else:
            price = {"unit_amount": 1, "currency": "usd"}
            price_id = ""
        metadata = product.metadata
        if metadata == {}:
            models = ["GPT-4"]
            features = ["GPT-4"]
            plug_limit = 1
            stripe.Product.modify(
                product.id,
                metadata={
                    "models": ",".join(models),
                    "features": ",".join(features),
                    "plug_limit": plug_limit
                }
            )
        else:

            models = metadata["models"]
            features = metadata["features"]
            models = models.replace(";", ",").replace(".", ",")
            features = features.replace(";", ",").replace(".", ",")
            models = models.split(",")
            features = features.split(",")
            plug_limit = metadata.get("plug_limit", " 1")
            if metadata.get("coming_soon") is None:
                coming_soon = True
            elif ''.join(metadata.get("coming_soon").split()) == "false":
                coming_soon = False
            else:
                coming_soon = True
        subs = {
            "name": product.name,
            "stripeSubscriptionId": product.id,
            "stripePriceId": price_id,
            "description": product.description,
            "cost": price.get("unit_amount", 1),
            "models": models,
            "features": features,
            "plugLimit": int(plug_limit),
            "active": product.active,
            "comingSoon": coming_soon,
            "updatedAt": convert_timestamp_to_datetime(product.updated),
            "currency": price.get("currency", "usd")
        }
        if event == 'product.created':
            # add subs into db
            Subscription(**subs).save()

        elif event == 'product.updated':
            print("product.updated", product)
            # old_subs = Subscription.objects(
            #     stripeSubscriptionId=product.id).first()
            # if old_subs is None and metadata[0] != {}:
            #     Subscription(**subs).save()
            #     return {"status": "success"}
            # else:
            #     old_subs.update(**subs)
        elif event == 'product.deleted':
            old_subs = Subscription.objects(
                stripeSubscriptionId=product.id).first()
            old_subs.delete()

        return {"status": "success"}
    except Exception as e:
        raise Exception("Error handle_product:", str(e))


############################ Payment Intent #############################################

def handle_user_payment_succeeded(payment_intent):
    try:

        # create customer portal in first time payment success
        invoice, product, customer, user = get_data_for_handle_user_by_payment_intent(
            payment_intent)
        portal_plug = stripe.billing_portal.Session.create(
            customer=customer.id,
            # The URL to redirect customers to when they click on the portal’s
            # link to return to my website.
            return_url="https://webaipilot.neoprototype.ca/dashboard",
        )
        print("handle_user_payment_succeeded----payment_intent")

        #         print("handle_user_payment_succeeded", invoice)
        metadata = product.metadata,
        user_id = customer.metadata.user_id
        user = User.objects(id=user_id).first() if not user else user
        price_id = invoice.lines.data[0].price.id
        sub = Subscription.objects(stripePriceId=price_id).first()
        print("sub", sub)
        subs_id = sub.id
        subs_model = sub.models[0]
        user.subscriptionId = ObjectId(subs_id)
        user.stripeCustomerId = customer.id
        sub_exp = invoice.lines.data[0].period.end
        user.stripePortal = portal_plug.url
        user.subExpiredAt = convert_timestamp_to_datetime(sub_exp)
        user.plugLimit = sub.plugLimit
        user.save()
        features = Subscription.objects(id=subs_id).first().features
        list_plug = Plug.objects(userId=user.id)
        sorted_plug_date = list(list_plug)
        sorted_plug_date.reverse()
        for plug in sorted_plug_date:
            plug.features = features
            plug.model = subs_model
            if sorted_plug_date.index(plug) <= user.plugLimit - 1:
                plug.active = True
            plug.save()

    except Exception as e:
        raise Exception("Error handle_user_payment_succeeded :", str(e))


def handle_payment_intent_fail(payment_intent):
    try:
        return {"code": 200, "message": "payment fail"}, HTTP_200_OK
    except Exception as e:
        raise Exception("Error handle_payment_intent_fail:", str(e))


############################ Invoice #############################################

def handle_invoice_finalized(invoice, event):
    try:
        # add invoice into db
        inv = {
            "stripeInvoiceId": invoice.id,
            "paymentIntentId": invoice.payment_intent,
            "stripePriceId": invoice.lines.data[0].price.id,
            "stripeCustomerId": invoice.customer,
            "amount": invoice.lines.data[0].amount,
            "currency": invoice.lines.data[0].currency,
            "status": invoice.status,
            "collectionMethod": invoice.collection_method,
            "periodStart": convert_timestamp_to_datetime(invoice.period_start),
            "periodEnd": convert_timestamp_to_datetime(invoice.period_end),
            "detailHostUrl": invoice.hosted_invoice_url,
            "detailUrl": invoice.lines.url,
            "updatedAt": datetime.datetime.utcnow(),
        }
        if event == "finalized":

            i = PaymentInvoice(**inv)
            i.save()
        elif event == "updated" and invoice:
            old_inv = PaymentInvoice.objects(
                stripeInvoiceId=invoice.id).first()
            old_inv.update(**inv)
            old_inv.save()

    except Exception as e:
        raise Exception("Error handle_invoice_finalized:", str(e))


def handle_invoice_payment_failed(invoice):
    try:
        # print("handle_invoice_payment_failed", invoice)
        customer = stripe.Customer.retrieve(invoice.customer)
        user = User.objects(stripeCustomerId=customer.id).first()
        list_plug = Plug.objects(userId=user.id)
        sorted_plug_date = list(list_plug)
        sorted_plug_date.reverse()
        if invoice.billing_reason == 'subscription_cycle' or invoice.billing_reason == 'subscription_update':
            if invoice.lines.data.__len__() > 1:
                # case for payment fail with card
                invoice_intent = invoice.payment_intent
                print("invoice_intent", invoice_intent)
                payment_intent = stripe.PaymentIntent.retrieve(invoice_intent)
                # print("payment_intent", payment_intent)
                if payment_intent.last_payment_error:
                    old_sub_id = invoice.lines.data[0].plan.id
                    old_sub = Subscription.objects(stripePriceId=old_sub_id).first()
                    user.subscriptionId = old_sub.id
                    user.save()
                    current_subscription = stripe.Subscription.retrieve(invoice.lines.data[0].subscription)
                    print("current_subscription", current_subscription)
                    stripe.Invoice.void_invoice(invoice.id)
                    rollback_subscription = stripe.Subscription.modify(
                        current_subscription['id'],
                        items=[{
                            'id': f"{current_subscription['items']['data'][0]['id']}",
                            "price": f"{old_sub.stripePriceId}",
                        }],
                        proration_behavior='create_prorations',
                    )
                    return {"code": 200, "message": "invoice payment fail"}, HTTP_200_OK

            user.subscriptionId = None
            for plug in sorted_plug_date:
                plug.features = None
                plug.model = None
                if sorted_plug_date.index(plug) != 0:
                    plug.active = False
                plug.save()
            user.subExpiredAt = None
            user.plugLimit = None
            user.save()

        return {"code": 200, "message": "invoice payment fail"}, HTTP_200_OK
    except Exception as e:
        raise Exception("Error handle_invoice_payment_failed:", str(e))


def handle_invoice_payment_succeeded(invoice):
    try:
        customer = stripe.Customer.retrieve(invoice.customer)
        print("qqqqqqqqqqqqqqqqqqqqqqqqqqhandle_invoice_payment_succeeded", invoice)
        user = User.objects(stripeCustomerId=customer.id).first()
        # handle success payment for downgrade or upgrade subscription
        if invoice.billing_reason == 'subscription_update':
            subscriptions = stripe.Subscription.list(customer=customer.id)
            price_id = invoice.lines.data[0].plan.id
            sub_exp = invoice.lines.data[0].period.end
            if invoice.lines.data.__len__() > 1:  # has credits
                price_id = invoice.lines.data[1].plan.id
                sub_exp = invoice.lines.data[1].period.end
            # downgrade
            elif price_id != subscriptions["data"][0]["items"]["data"][0]["price"]["id"]:
                price_id = subscriptions["data"][0]["items"]["data"][0]["price"]["id"]
                sub_exp = subscriptions["data"][0]["current_period_end"]

            sub = Subscription.objects(stripePriceId=price_id).first()
            old_sub = Subscription.objects(id=user.subscriptionId).first()
            list_plug = Plug.objects(userId=user.id)
            sorted_plug_date = list(list_plug)
            sorted_plug_date.reverse()
            if old_sub.cost > sub.cost:  # downgrade
                for i in range(sub.plugLimit, sorted_plug_date.__len__()):
                    sorted_plug_date[i]["active"] = False
                    sorted_plug_date[i].save()
            elif old_sub.cost < sub.cost:  # upgrade
                range_plug = sorted_plug_date.__len__()
                if range_plug >= sub.plugLimit:
                    range_plug = sub.plugLimit
                for i in range(0, range_plug):
                    sorted_plug_date[i]["active"] = True
                    sorted_plug_date[i].save()
            user.plugLimit = sub.plugLimit
            user.update(subscriptionId=sub.id)
            user.subExpiredAt = convert_timestamp_to_datetime(sub_exp)
            user.plugLimit = sub.plugLimit
            user.save()
            subs_features = sub.features
            subs_model = sub.models[0]
            list_plug = Plug.objects(userId=user.id)
            for plug in list_plug:
                plug.features = subs_features
                plug.model = subs_model
                plug.save()
    except Exception as e:
        raise Exception("Error handle_invoice_payment_succeeded:", str(e))


def handle_invoice_voided(invoice):
    try:
        print("handle_invoice_voided")
    except Exception as e:
        raise Exception("Error handle_invoice_voided:", str(e))


############################ Subscription#############################################

def handle_customer_subscription_deleted(subs):
    try:
        customer_id = subs.customer
        if subs.cancellation_details.reason == 'cancellation_requested':
            user = User.objects(stripeCustomerId=customer_id).first()
            user.subscriptionId = None
            user.stripePortal = None
            user.subExpiredAt = None
            user.save()

    except Exception as e:
        raise Exception("Error handle_customer_subscription_deleted:", str(e))


def handle_customer_subscription_update(subs):
    try:
        customer_id = subs.customer
        # cancel,renew, -- upgrade, downgrade
        # unsubscribe
        if subs.cancellation_details.reason == 'cancellation_requested' and subs.cancel_at_period_end and not subs.cancellation_details.feedback:
            user = User.objects(stripeCustomerId=customer_id).first()
            free_sub_features = Subscription.objects(cost=0).first().features
            list_plug = Plug.objects(userId=user.id)

            for plug in list_plug:
                plug.features = free_sub_features
                plug.save()
        # Renew
        # if subs.cancellation_details.reason == 'null' and subs.cancel_at_period_end == False:
        #     price_id = subs['item']['data'][0]['price']['id']
        #     subs_features = Subscription.objects(stripePriceId=price_id).first().features
        #     user = User.objects(stripeCustomerId=customer_id).first()
        #     list_plug = Plug.objects(userId=user.id)
        #     for plug in list_plug:
        #         plug.features = subs_features
        #         plug.save()

    except Exception as e:
        raise Exception("Error handle_customer_subscription_update:", str(e))


def get_data_for_handle_user_by_payment_intent(payment_intent):
    invoice = stripe.Invoice.retrieve(payment_intent.invoice)
    invoice_product = invoice.lines.data[0].price.product
    product = stripe.Product.retrieve(invoice_product)
    customer = stripe.Customer.retrieve(invoice.customer)
    user = User.objects(stripeCustomerId=customer.id).first()
    return invoice, product, customer, user
