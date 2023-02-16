

def get_user_full_name(user_obj):
    name = None
    if user_obj:
        name = user_obj.get_full_name()
    return name
