import scripts.data.constants as K

def check_league(league_name):
    league_name = str(league_name).lower()

    if(league_name not in K.LEAGUE_NAMES):
        msg = f' - League not found: >>> {league_name} <<<'
        check = False
    else:
        msg = f' - League found: {league_name}'
        check = True

    return check, msg
