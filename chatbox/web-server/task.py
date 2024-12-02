from celery import Celery
from celery.schedules import schedule
from datetime import datetime
from src.models import User, Plug, Guest
import src.database.mongodb as mongo
import pytz
from datetime import timedelta
from celery.schedules import crontab
from mongoengine import Q

broker_url = "redis://localhost:6379/0"

celery = Celery('task', broker=broker_url)

celery.conf.beat_schedule = {
    'delete_expired_users': {
        'task': 'task.delete_expired_users',
        'schedule': schedule(run_every=timedelta(days=1)),
    },
    'delete_guests': {
        'task': 'task.delete_guests',
        'schedule': crontab(0, 0, day_of_month='1')
    }
}


@celery.task
def delete_expired_users():
    mongo.create_db_connection()
    User.objects(expiredAt__lte=datetime.now(pytz.UTC)).delete()


@celery.task
def delete_guests():
    mongo.create_db_connection()
    two_months_ago = datetime.now(pytz.UTC) - timedelta(days=60)
    client_ids = [plug.client.id for plug in Plug.objects(
        createdAt__lte=two_months_ago, client__exists=True)]
    if client_ids:
        Guest.objects(Q(client__in=client_ids)).delete()
