from json import JSONDecodeError

import scripts.data.constants as K
from core.file_manager.os_utils import exists
from scripts.constants.configs import DEFAULT_COMBO_LIST, DEFAULT_FILTER_BET, DEFAULT_MONEY_BET, DEFAULT_THR_LIST, \
    DEFAULT_FILTER_BET_LIST
from scripts.constants.paths import LEAGUE_PARAMS_FILENAME, DATA_PARAMS_FILENAME, MODEL_PARAMS_FILENAME, \
    FEAT_ENG_FILENAME
from scripts.utils.loading import load_configs_from_paths


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

def check_training_args(args):

    check = 'epochs' in list(args.keys()) and 'patience' in list(args.keys())

    if not check:
        msg = f'Args not found: {list(args.keys())}'
    else:
        msg = 'Args read'

    return {'check':check,
            'msg':msg}


def check_training_params(params):
    check = ['league', 'data', 'model'] == list(params.keys())

    if not check:
        msg = f'Params not found: {params.keys()}'
    else:
        msg = 'Params read'

    return {'check': check,
            'msg': msg}

def check_predict_paths(model_dir, model_name):
    if not exists(model_dir):
        msg = f'model directory not found: {model_dir}'
        response = {'check':False,
                    'msg':msg}

    else:

        paths = {'league_params': f'{model_dir}{LEAGUE_PARAMS_FILENAME}',
                 'data_params': f'{model_dir}{DATA_PARAMS_FILENAME}',
                 'model_params': f'{model_dir}{MODEL_PARAMS_FILENAME}',
                 'model': f'{model_dir}{model_name}.pth',
                 'feat_eng': f'{model_dir}{FEAT_ENG_FILENAME}'}

        response = {'msg': 'paths created',
                    'check': True,
                    'paths':paths}

        return response

def check_simulation_params(sim_params):
    params_list = list(sim_params.keys())

    n_matches = sim_params['n_matches'] if 'n_matches' in params_list else -1
    combo = sim_params['combo'] if 'combo' in params_list else None
    combo_list = sim_params['combo_list'] if 'combo_list' in params_list else DEFAULT_COMBO_LIST
    filter_bet = sim_params['filter_bet'] if 'filter_bet' in params_list else DEFAULT_FILTER_BET
    money_bet = sim_params['money_bet'] if 'money_bet' in params_list else DEFAULT_MONEY_BET
    thr_list = sim_params['thr_list'] if 'thr_list' in params_list else DEFAULT_THR_LIST
    combo = sim_params['combo'] if 'combo' in params_list else None
    filter_bet_list = sim_params['filter_bet_list'] if 'filter_bet_list' in params_list else DEFAULT_FILTER_BET_LIST

    sim_params['n_matches'] = n_matches
    sim_params['combo'] = combo
    sim_params['combo_list'] = combo_list
    sim_params['filter_bet'] = filter_bet
    sim_params['money_bet'] = money_bet
    sim_params['thr_list'] = thr_list
    sim_params['filter_bet_list'] = filter_bet_list

    return sim_params