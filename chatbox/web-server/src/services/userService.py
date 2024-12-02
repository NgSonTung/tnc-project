import openai


def validate_user_openai_key(key):
    try:
        client = openai.OpenAI(api_key=key)
        response = client.models.list()
        message = "Valid key"
        return True, message
    except openai.APIError as e:
        error_info = e.response.json()
        error_message = error_info.get('error', {}).get('message', 'Unknown error occurred')
        return False, error_message


def set_user_key_for_plug(plugs, key):
    for plug in plugs:
        plug.userKey = key
    return plugs
