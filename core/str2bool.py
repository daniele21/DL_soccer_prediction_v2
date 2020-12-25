
def str2bool(value):
    str_value = str(value).lower()
    if str_value == 'true':
        return True
    elif str_value == 'false':
        return False
    else:
        return False