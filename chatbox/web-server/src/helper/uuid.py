import uuid


def generate_uuid(length=10):
    uuid_str = str(uuid.uuid4())

    short_uuid = uuid_str[:length]

    return short_uuid
