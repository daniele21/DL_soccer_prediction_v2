import json

import requests
from scripts.constants.configs import API_READ, API_WRITE, API_PROCESS


def league_request(api_config):
    """

    Args:
        api_config: dict{
                            'host',
                            'port'
                        }

    Returns:
        response: dict {
                            'league_name': list

                        }
    """

    host, port = api_config['host'], api_config['port']
    endpoint = f'http://{host}:{port}{API_READ}leagues'

    response = requests.get(endpoint)

    return response

def league_teams_request(api_config, league_name):
    """

    Args:
        api_config: dict{
                            'host',
                            'port'

                        }

    Returns:
        response: dict {
                            'league_name': str,
                            'teams': list

                        }
    """
    host, port = api_config['host'], api_config['port']
    endpoint = f'http://{host}:{port}{API_READ}/teams'

    response = requests.get(endpoint, params={'league': league_name})

    return response

def predict_request(api_config, params):
    """

    Args:
        api_config: dict{
                            'host',
                            'port'
                        }

        params: dict{'league_name':  str <OPTION_1>,
                     |'model_dir':   str <OPTION_2>|,
                     |'model_name':  str <OPTION_2>|,

                     'thr': OPTIONAL -> {'home':float,
                                         'away':float},
                     'round': int,
                     'home_teams': list,
                     'away_teams': list,
                     '1X_odds': list,
                     'X2_odds': list}

    Returns:
        response: dict{'match_1': {
                                   '1X',
                                   'pred_1X',
                                   'pred_1X_bet',
                                   'X2',
                                   'pred_X2',
                                   'pred_X2_bet',
                                   'event',
                                   'prob'
                                }
                       'match_2': {...}
        """

    host, port = api_config['host'], api_config['port']
    endpoint = f'http://{host}:{port}{API_PROCESS}predict'

    response = requests.post(endpoint, json=params)
    # print(response)
    response_dict = json.loads(response.text)

    return response_dict

def write_request(api_config, params):
    """

    Args:
        api_config: dict{
                            'host',
                            'port'
                        }

        params: dict{ 'league_name': LEAGUE_NAME,
                      'n_prev_match': NPM,
          }

    Returns:

    """
    host, port = api_config['host'], api_config['port']
    endpoint = f'http://{host}:{port}{API_WRITE}/league_data'

    response = requests.post(endpoint, params)

    return response
