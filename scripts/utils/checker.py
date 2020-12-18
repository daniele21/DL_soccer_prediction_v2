import scripts.data.constants as K
from core.file_manager.os_utils import exists

def check_league(league_name):
    league_name = str(league_name).lower()

    if(league_name not in K.LEAGUE_NAMES):
        msg = f' League not found: >>> {league_name} <<<'
        check = False
    else:
        msg = f' League found: {league_name}'
        check = True

    response = {'check':check,
                'msg':msg}

    return response

def check_data_league(league_name, npm):

    data_path = f'{K.DATA_DIR}{league_name}/{league_name}_npm={npm}.csv'

    check = exists(data_path)
    if not check:
        msg = f'Data not Found: {data_path}'
    else:
        msg = f'Data Found at {data_path}'

    response = {'check':check,
                'msg':msg}

    return response

def check_npm(npm):

    try:
        check = True if int(npm) > 0 else False
        msg = 'Valid NPM parameter passed'

    except ValueError:
        check = False
        msg = f'Invalid NPM parameter passed: {msg} is not castable to an integer number'

    response = {'check':check,
                'msg':msg}

    return response
