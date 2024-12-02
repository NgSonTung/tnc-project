import datetime


def convert_timestamp_to_datetime(timestamp):
    return datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')


def add_days_to_timestamp(timestamp, days):
    datetime_obj = datetime.datetime.fromtimestamp(timestamp)
    new_datetime_obj = datetime_obj + datetime.timedelta(days=days)
    new_timestamp = new_datetime_obj.timestamp()

    return new_timestamp


def convert_datetime_to_timestamp(y=None, m=None, d=None, now=False, datetime_obj=None):
    if now:
        datetime_obj = datetime.datetime.now()
    elif datetime_obj:
        return str(datetime_obj.timestamp()).split('.')[0]
    else:
        datetime_obj = datetime.datetime(y, m, d)
    return str(datetime_obj.timestamp()).split('.')[0]


# the obj is dict
def sort_list_date_desc(list_date):
    return sorted(list_date, key=lambda obj: convert_datetime_to_timestamp(datetime_obj=obj['createdAt']), reverse=True)
