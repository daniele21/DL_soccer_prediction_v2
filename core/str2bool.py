from scripts.constants.configs import DEFAULT_PRODUCTION


def str2bool(value):
    str_value = str(value).lower()
    if str_value == 'true':
        return True
    elif str_value == 'false':
        return False
    else:
        return DEFAULT_PRODUCTION