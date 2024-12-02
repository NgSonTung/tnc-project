from src.models import Subscription
from flask import current_app


def get_subscription_name(subscription_id):
    try:
        subscription = Subscription.objects(id=subscription_id).first()
        if subscription is None:
            return None
        return subscription.name
    except Exception as e:
        print(str(e))
        return None


def get_feature_limit(subscription_id):
    subscription = Subscription.objects(id=subscription_id).first()
    if subscription is None:
        return None
    if subscription.name.lower() == "free" or subscription.cost == 0:
        return {"uploadLimit": current_app.config["FREE_UPLOAD_FILE"],
                "crawlLimit": current_app.config["FREE_CRAWL_WEBSITE"]}
    elif subscription.name.lower() == "starter":
        return {"uploadLimit": current_app.config["STARTER_UPLOAD_FILE"],
                "crawlLimit": current_app.config["STARTER_CRAWL_WEBSITE"]}
    elif subscription.name.lower() == "pro":
        return {"uploadLimit": current_app.config["PRO_UPLOAD_FILE"],
                "crawlLimit": current_app.config["PRO_CRAWL_WEBSITE"]}
    elif subscription.name.lower() == "company":
        return {"uploadLimit": current_app.config["COMPANY_UPLOAD_FILE"],
                "crawlLimit": current_app.config["COMPANY_CRAWL_WEBSITE"]}
    else:
        return None
