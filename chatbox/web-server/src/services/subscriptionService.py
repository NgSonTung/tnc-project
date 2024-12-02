name_order = {"free": 1, "starter": 2, "professional": 3, "company": 4}

def custom_sort_key(item):
    name = item["name"].lower()
    return name_order.get(name, float("inf"))