import sys
import os
import stripe
import base64

sys.path.append(os.path.abspath(os.path.join('src', 'models')))
from ContextItemModel import ContextItem,ContextChunk
from UserModel import User
from PlugModel import Plug
from GuestModel import Guest
from HistoryModel import History
from MessageModel import Message
from SubscriptionModel import Subscription, FeatureLimit
from LLMModel import LLM
from FeatureModel import Feature
import mongoengine
import json
from bson import ObjectId
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
if os.environ.get("FLASK_ENV") != "docker":
    stripe.api_key = os.environ.get("STRIPE_API_SECRET_KEY")
else:
    stripe.api_key = os.environ.get("STRIPE_API_SECRET_KEY_LIVE") # hot fix demo 11-21-2024
    
WEBSITE_URL = os.getenv('URL_API_FE')

print("FLASK_ENV===========", os.environ.get("FLASK_ENV"))


def get_feature_limit(subscription_id):
    subscription = Subscription.objects(id=subscription_id).first()
    if subscription is None:
        return None
    if subscription.name.lower() == "free" or subscription.cost == 0:
        return {"upload files": os.environ.get("FREE_UPLOAD_FILE"),
                "crawl website": os.environ.get("FREE_CRAWL_WEBSITE"),
                "custom WebAI Pilot plug": os.environ.get("FREE_CUSTOM_2GAI_PLUG"),
                }
    elif subscription.name.lower() == "starter":
        return {"upload files": os.environ.get("STARTER_UPLOAD_FILE"),
                "crawl website": os.environ.get("STARTER_CRAWL_WEBSITE"),
                "custom WebAI Pilot plug": os.environ.get("STARTER_CUSTOM_2GAI_PLUG")}
    elif subscription.name.lower() == "professional":
        return {"upload files": os.environ.get("PRO_UPLOAD_FILE"),
                "crawl website": os.environ.get("PRO_CRAWL_WEBSITE"),
                "custom WebAI Pilot plug": os.environ.get("PRO_CUSTOM_2GAI_PLUG")}
    elif subscription.name.lower() == "company":
        return {"upload files": os.environ.get("COMPANY_UPLOAD_FILE"),
                "crawl website": os.environ.get("COMPANY_CRAWL_WEBSITE"),
                "custom WebAI Pilot plug": os.environ.get("COMPANY_CUSTOM_2GAI_PLUG")}
    else:
        return None


def import_data():
    print("\n==========Inserting Database=========")
    # Import data from plug.json
    plug_file = "src/database/mongodb/data/plug.json"

    with open(plug_file, "r") as file:
        plug_data = json.load(file)

    # Convert to valid BSON
    for doc in plug_data:
        doc["id"] = ObjectId(doc["id"])
        if doc.get("userId", None):
            doc["userId"] = ObjectId(doc["userId"])
        client_id = doc["client"].get("id", None)
        if client_id:
            doc["client"]["id"] = ObjectId(client_id)
        if doc.get("plugName", None) == "WEBAI-PILOT-WEBSITE-PLUG":
            if os.environ.get("FLASK_ENV") == "production":
                doc["client"]["origin"] = WEBSITE_URL
            else:
                doc["client"]["origin"] = WEBSITE_URL

    if isinstance(plug_data, list):
        for plug in plug_data:
            plug = Plug(**plug)
            plug.save()
            print("Inserted mongo collection: Plug from", plug_file)
    else:
        print("Invalid JSON data in", plug_file)

    # Import data from user.json
    user_file = "src/database/mongodb/data/user.json"

    with open(user_file, "r") as file:
        user_data = json.load(file)

    # Convert to valid BSON
    for doc in user_data:
        doc["id"] = ObjectId(doc["id"])
        if 'subscriptionId' in doc:
            doc["subscriptionId"] = ObjectId(doc["subscriptionId"])

    if isinstance(user_data, list):
        for user in user_data:
            user = User(**user)
            user.save()
            print("Inserted mongo collection: User from", user_file)
    else:
        print("Invalid JSON data in", user_file)

    # Import data from feature.json
    feature_file = "src/database/mongodb/data/feature.json"

    with open(feature_file, "r") as file:
        feature_data = json.load(file)

    # Convert to valid BSON
    for doc in feature_data:
        doc["id"] = ObjectId(doc["id"])

    if isinstance(feature_data, list):
        for feature in feature_data:
            feature = Feature(**feature)
            feature.save()
            print("Inserted mongo collection: Feature from", feature_file)
    else:
        print("Invalid JSON data in", feature_file)

    # Import data from llm.json
    llm_file = "src/database/mongodb/data/llm.json"

    with open(llm_file, "r") as file:
        llm_data = json.load(file)

    # Convert to valid BSON
    for doc in llm_data:
        doc["id"] = ObjectId(doc["id"])

    if isinstance(llm_data, list):
        for llm in llm_data:
            llm = LLM(**llm)
            llm.save()
            print("Inserted mongo collection: LLM from", llm_file)
    else:
        print("Invalid JSON data in", llm_file)

    # import guest data
    guest_file = "src/database/mongodb/data/guest.json"
    with open(guest_file, "r") as file:
        guest_data = json.load(file)
    for doc in guest_data:
        doc["id"] = ObjectId(doc["id"])
    if isinstance(guest_data, list):
        for guest in guest_data:
            guest = Guest(**guest)
            guest.save()
    else:
        print("Invalid JSON data in", guest_file)

    # import history data
    history_file = "src/database/mongodb/data/history.json"
    with open(history_file, "r") as file:
        history_data = json.load(file)
    for doc in history_data:
        doc["id"] = ObjectId(doc["id"])
    if isinstance(history_data, list):
        for history in history_data:
            history = History(**history)
            history.save()
    else:
        print("Invalid JSON data in", history_file)

       
    # import context item data
    context_file = "src/database/mongodb/data/item.json"
    with open(context_file, "r") as file:
        context_data = json.load(file)
    for doc in context_data:
        doc["id"] = ObjectId(doc["id"])
        doc["plugId"] = ObjectId(doc["plugId"])
        if "children" in doc and isinstance(doc["children"], list):
            for child in doc["children"]:
                child = ObjectId(child)
    if isinstance(context_data, list):
        print("Inserted mongo collection: ContextItem from", context_file)
        for context in context_data:
            context = ContextItem(**context)
            context.save()
    else:
        print("Invalid JSON data in", context_file)
        
    # import chunks data
    chunk_file = "src/database/mongodb/data/chunk.json"
    with open(chunk_file, "r") as file:
        chunk_data = json.load(file)
    for doc in chunk_data:
        doc["id"] = ObjectId(doc["id"])
        doc["files_id"] = ObjectId(doc["files_id"])
        doc["data"] = base64.b64decode(doc["data"])
    if isinstance(chunk_data, list):
        print("Inserted mongo collection: Chunk from", chunk_file)
        for chunk in chunk_data:
            chunk = ContextChunk(**chunk)
            chunk.save()
    else:
        print("Invalid JSON data in", chunk_file)
    # todo cmt this for testing
    # import message data
    message_file = "src/database/mongodb/data/message.json"
    with open(message_file, "r") as file:
        message_data = json.load(file)
    for doc in message_data:
        doc["id"] = ObjectId(doc["id"])
    if isinstance(message_data, list):
        print(f"{len(message_data)} messages have been found from {message_file}")
        for message in message_data:
            message = Message(**message)
            message.save()

    else:
        print("Invalid JSON data in", message_file)

    if os.environ.get("FLASK_ENV") == "docker" or os.environ.get("FLASK_ENV") is None:
        subscription_file = "src/database/mongodb/data/subscription.json"
        with open(subscription_file, "r") as file:
            subscription_data = json.load(file)
        print(f"{len(message_data)} messages have been found from {subscription_file}")
        for doc in subscription_data:
            doc["id"] = ObjectId(doc["id"])
        if isinstance(subscription_data, list):
            for subscription in subscription_data:
                subscription = Subscription(**subscription)
                subscription.save()
        else:
            print("Invalid JSON data in", subscription_file)
        print("=====================================\n")


def import_stipe_products(env_key=None):
    if env_key is not None:
        stripe.api_key = env_key
        print(env_key)
    try:
        products = stripe.Product.list(limit=100)
        limitation = os.environ.get("LIMITATION").split(",")
        print(limitation)
        if products.data is None or len(products.data) == 0 or products is None or len(products) == 0:
            print("No stripe products found")
            return None
        index = 1
        for product in products.data:
            if product.active:
                prices = stripe.Price.list(product=product.id)
                if product.name == "Free":
                    id = "64aff45ae43f3103d2fa22e0"
                if prices.data.__len__() > 1:
                    for price in prices.data:
                        price_id = price.id
                        metadata = product.metadata
                        models = metadata["models"].split(",")
                        features = metadata["features"].split(",")
                        plug_limit = metadata.get("plug_limit", "1")
                        if price.recurring.interval == "year":
                            is_yearly = True
                        else:
                            is_yearly = False
                        if metadata.get("coming_soon") is None:
                            coming_soon = True
                        elif ''.join(metadata.get("coming_soon").split()) == "false":
                            coming_soon = False
                        else:
                            coming_soon = True

                        if coming_soon is None:
                            coming_soon = True
                        if plug_limit is None:
                            plug_limit = 1
                            # for dev
                        if product.name != "Free":
                            id = f"64aff45ae43f3103d2fa22e{index}"
                            # coming_soon = True
                        subs = {
                            "id": f"{id}",
                            "name": product.name,
                            "stripeSubscriptionId": product.id,
                            "stripePriceId": price_id,
                            "description": product.description,
                            "cost": price.unit_amount / 100,
                            "models": models,
                            "features": features,
                            "plugLimit": int(plug_limit),
                            "active": product.active,
                            "comingSoon": coming_soon,  # product.name =="Free" ? False : True,
                            "isYearly": is_yearly,
                            "updatedAt": datetime.fromtimestamp(product["updated"]).strftime('%Y-%m-%d %H:%M:%S'),
                            "currency": price.currency
                        }
                        print(subs)
                        subscription = Subscription(**subs)
                        subscription.save()
                        f_limit = get_feature_limit(subscription.id)
                        if f_limit is not None and subscription.features:
                            for feature in subscription.features:
                                limit_value = -1
                                unlimited = False
                                if feature in f_limit.keys():
                                    limit_value = int(f_limit[feature])
                                if (
                                        limit_value == -1 and feature in limitation) or "gpt" in feature or feature not in limitation:
                                    unlimited = True
                                feature_limit = FeatureLimit(name=feature, limit=limit_value, unlimited=unlimited)
                                subscription.featuresLimit.append(feature_limit)
                            subscription.save()
                        index += 1
                else:
                    price_id = product.default_price

                    price = stripe.Price.retrieve(price_id)

                    metadata = product.metadata
                    models = metadata["models"].split(",")
                    features = metadata["features"].split(",")
                    plug_limit = metadata.get("plug_limit", "1")

                    if metadata.get("coming_soon") is None:
                        coming_soon = True
                    elif ''.join(metadata.get("coming_soon").split()) == "false":
                        coming_soon = False
                    else:
                        coming_soon = True

                    if coming_soon is None:
                        coming_soon = True
                    if plug_limit is None:
                        plug_limit = 1
                        # for dev
                    if product.name != "Free":
                        id = f"64aff45ae43f3103d2fa22e{index}"
                        # coming_soon = True
                    subs = {
                        "id": f"{id}",
                        "name": product.name,
                        "stripeSubscriptionId": product.id,
                        "stripePriceId": price_id,
                        "description": product.description,
                        "cost": price.unit_amount / 100,
                        "models": models,
                        "features": features,
                        "plugLimit": int(plug_limit),
                        "active": product.active,
                        "comingSoon": coming_soon,  # product.name =="Free" ? False : True,
                        "updatedAt": datetime.fromtimestamp(product["updated"]).strftime('%Y-%m-%d %H:%M:%S'),
                        "currency": price.currency
                    }
                    subscription = Subscription(**subs)
                    subscription.save()
                    f_limit = get_feature_limit(subscription.id)
                    if f_limit is not None and subscription.features:
                        for feature in subscription.features:
                            limit_value = -1
                            unlimited = False
                            if feature in f_limit.keys():
                                limit_value = int(f_limit[feature])
                            if (
                                    limit_value == -1 and feature in limitation) or "gpt" in feature or feature not in limitation:
                                unlimited = True
                            feature_limit = FeatureLimit(name=feature, limit=limit_value, unlimited=unlimited)
                            subscription.featuresLimit.append(feature_limit)
                        subscription.save()
                    index += 1

        print(f"Inserted {index - 1} mongo collection: Subscription from stripe api")
    except Exception as e:
        print("Error:", str(e))


def re_import_subscription(env_key=None):
    Subscription.objects({}).delete()
    import_stipe_products(env_key)


def clean_data():
    print("\n==========Cleaning Database==========")
    ContextItem.objects({}).delete()
    print("Cleaned mongo collection: ContextItem")
    ContextChunk.objects({}).delete()
    print("Cleaned mongo collection: ContextChunk")
    Plug.objects({}).delete()
    print("Cleaned mongo collection: Plug")
    User.objects({}).delete()
    print("Cleaned mongo collection: User")
    # Subscription.objects({}).delete()
    # print("Cleaned mongo collection: Subscription")
    Feature.objects({}).delete()
    print("Cleaned mongo collection: Feature")
    LLM.objects({}).delete()
    print("Cleaned mongo collection: LLM")
    Guest.objects({}).delete()
    print("Cleaned mongo collection: Guest")
    History.objects({}).delete()
    print("Cleaned mongo collection: History")
    Message.objects({}).delete()
    print("Cleaned mongo collection: Message")
    print("=====================================\n")
    print("To reset subscription data run : python src/database/mongodb/import.py --stripe_reset_subscriptions ")


def update_data():
    try:
        print("Please provide your file path (json file) to update data")
        path = input("Enter your file path: ")
        print("Choose mongo collection to update:")
        print(
            "1. User model \n2. Plug model \n3. Subscription model \n4. Feature model \n5. LLM model \n6. ContextItem model \n7. Guest model \n8. History model \n9. Message model")
        choice = input("Enter your choice: ")
        with open(path, "r") as file:
            data = json.load(file)
        print("Updating data................")
        if choice == "1":
            print("Updating User model")

            for doc in data:
                doc["id"] = ObjectId(doc["id"])
                if 'subscriptionId' in doc:
                    doc["subscriptionId"] = ObjectId(doc["subscriptionId"])
            if isinstance(data, list):
                for user in data:
                    user = User(**user)
                    user.save()
                    print("Updated mongo collection: User")
            else:
                print("Invalid JSON data in", path)
        elif choice == "2":
            print("Updating Plug model")
            for doc in data:
                doc["id"] = ObjectId(doc["id"])
                if doc.get("userId", None):
                    doc["userId"] = ObjectId(doc["userId"])
                if doc.get("plugName", None) == "WEBAI-PILOT-WEBSITE-PLUG":
                    if os.environ.get("FLASK_ENV") == "production":
                        doc["client"]["origin"] = WEBSITE_URL
                    else:
                        doc["client"]["origin"] = WEBSITE_URL

            if isinstance(data, list):
                for plug in data:
                    plug = Plug(**plug)
                    plug.save()
                    print("Updated mongo collection: Plug")
            else:
                print("Invalid JSON data in", path)
        print("\n==========Done==========")
    except Exception as e:
        print("Error:", str(e))


if __name__ == "__main__":
    # Parse command-line arguments using argparse
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('--fill', action='store_true',
                        help='Run database import')
    parser.add_argument('--clean', action='store_true',
                        help='Run database clean')
    parser.add_argument('--reset', action='store_true',
                        help='Run database clean then import')
    parser.add_argument('--test', action='store_true',
                        help='test')
    parser.add_argument('--stripe_import_subscriptions', action='store_true',
                        help='stripe_import_subscriptions')
    parser.add_argument('--stripe_reset_subscriptions', action='store_true',
                        help='stripe_reset_subscriptions')
    parser.add_argument('--update_data', action='store_true', help='update_data')

    parser.add_argument('--reset_production', action='store_true', help='reset_production'),

    parser.add_argument('--reset_subscription_production', action='store_true', help='reset_subscription_production')
    args = parser.parse_args()

    # If --import argument is provided, run the import_data() function
    # Establish the MongoDB connection
    mongoengine.connect(os.environ.get("DB_NAME"), host="mongodb://localhost:27017")
    if args.fill:
        # Run the import_data() function
        import_data()

        # Close the MongoDB connection
        mongoengine.disconnect()

    elif args.clean:
        # Run the import_data() function
        clean_data()

        # Close the MongoDB connection
        mongoengine.disconnect()

    elif args.reset:
        # Run the import_data() function
        clean_data()
        import_data()
        # Close the MongoDB connection
        mongoengine.disconnect()

    elif args.reset_production:
        # Run the import_data() function
        clean_data()
        import_data()
        re_import_subscription(os.environ.get("STRIPE_API_SECRET_KEY_LIVE"))
        # Close the MongoDB connection
        mongoengine.disconnect()

    elif args.stripe_import_subscriptions:
        print("Inserting subscription")
        import_stipe_products()
    elif args.stripe_reset_subscriptions:
        re_import_subscription()
        print("\nreset subscription")

    elif args.reset_subscription_production:

        re_import_subscription(os.environ.get("STRIPE_API_SECRET_KEY_LIVE"))
        print("\nreset subscription")
    elif args.update_data:
        update_data()
        print("data updated")
