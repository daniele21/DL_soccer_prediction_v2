from json import JSONDecodeError

from scripts.constants.paths import DATA_DIR
import scripts.constants.league as LEAGUE
from core.file_manager.os_utils import exists
from core.str2bool import str2bool
from scripts.constants.configs import *
from scripts.constants.paths import LEAGUE_PARAMS_FILENAME, DATA_PARAMS_FILENAME, MODEL_PARAMS_FILENAME, \
    FEAT_ENG_FILENAME
from scripts.exceptions.param_exc import ParameterError


def check_league(league_name):
    league_name = str(league_name).lower()

    if(league_name not in LEAGUE.LEAGUE_NAMES):
        msg = f' League not found: >>> {league_name} <<<'
        check = False
    else:
        msg = f' League found: {league_name}'
        check = True

    response = {'check':check,
                'msg':msg}

    return response

def check_data_league(league_name, npm):

    data_path = f'{DATA_DIR}{league_name}/{league_name}_npm={npm}.csv'

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

    params = {}

    params[TEST_SIZE_LABEL] = int(sim_params[TEST_SIZE_LABEL]) if TEST_SIZE_LABEL in params_list else DEFAULT_TEST_SIZE
    params[THR_LABEL] = float(sim_params[THR_LABEL]) if THR_LABEL in params_list else DEFAULT_THR
    params[N_MATCHES_LABEL] = sim_params[N_MATCHES_LABEL] if N_MATCHES_LABEL in params_list else -1
    params[COMBO_LABEL] = sim_params[COMBO_LABEL] if COMBO_LABEL in params_list else None
    params[COMBO_LIST_LABEL] = sim_params[COMBO_LIST_LABEL] if COMBO_LIST_LABEL in params_list else DEFAULT_COMBO_LIST
    params[FILTER_BET_LABEL] = sim_params[FILTER_BET_LABEL] if FILTER_BET_LABEL in params_list else DEFAULT_FILTER_BET
    params[MONEY_BET_LABEL] = sim_params[MONEY_BET_LABEL] if MONEY_BET_LABEL in params_list else DEFAULT_MONEY_BET
    params[THR_LIST_LABEL] = sim_params[THR_LIST_LABEL] if THR_LIST_LABEL in params_list else DEFAULT_THR_LIST
    params[FILTER_BET_LIST_LABEL] = sim_params[FILTER_BET_LIST_LABEL] if FILTER_BET_LIST_LABEL in params_list else DEFAULT_FILTER_BET_LIST
    params[FIELD_LABEL] = sim_params[FIELD_LABEL] if FIELD_LABEL in params_list else -1
    params[SAVE_DIR_LABEL] = sim_params[SAVE_DIR_LABEL] if SAVE_DIR_LABEL in params_list else DEFAULT_SAVE_DIR
    params[VERBOSE_LABEL] = str2bool(sim_params[VERBOSE_LABEL]) if VERBOSE_LABEL in params_list else DEFAULT_VERBOSE

    if(params[FIELD_LABEL] == -1):
        raise ParameterError(f'Invalid or Missing Field Params:\n {params[FIELD_LABEL]}')

    return params

def check_data_params(data_params):
    params_list = list(data_params.keys())

    params = {}
    params[LEAGUE_NAME_LABEL] = data_params[LEAGUE_NAME_LABEL] if LEAGUE_NAME_LABEL in params_list else -1
    params[N_PREV_MATCH_LABEL] = int(data_params[N_PREV_MATCH_LABEL]) if N_PREV_MATCH_LABEL in params_list else -1
    params[TRAIN_LABEL] = str2bool(data_params[TRAIN_LABEL]) if TRAIN_LABEL in params_list else -1
    params[TEST_SIZE_LABEL] = int(data_params[TEST_SIZE_LABEL]) if TEST_SIZE_LABEL in params_list else DEFAULT_TEST_SIZE
    params[LEAGUE_DIR_LABEL] = data_params[LEAGUE_DIR_LABEL] if LEAGUE_DIR_LABEL in params_list else -1
    params[UPDATE_LABEL] = data_params[UPDATE_LABEL] if UPDATE_LABEL in params_list else DEFAULT_UPDATE
    params[PLOT_LABEL] = data_params[PLOT_LABEL] if PLOT_LABEL in params_list else DEFAULT_PLOT

    if -1 in params.values():
        raise ParameterError(f'Invalid or Missing Data Params:\n {data_params}')

    return params

def check_dataset_params(data_params):
    params_list = list(data_params.keys())

    params = {}
    params[TRAIN_LABEL] = str2bool(data_params[TRAIN_LABEL]) if TRAIN_LABEL in params_list else -1
    params[NORMALIZE_LABEL] = str2bool(data_params[NORMALIZE_LABEL]) if NORMALIZE_LABEL in params_list else DEFAULT_NORMALIZE
    params[SAVE_DIR_LABEL] = data_params[SAVE_DIR_LABEL] if SAVE_DIR_LABEL in params_list else DEFAULT_SAVE_DIR
    params[DATASET_LABEL] = data_params[DATASET_LABEL] if DATASET_LABEL in params_list else DEFAULT_DATASET
    params[BATCH_SIZE_LABEL] = int(data_params[BATCH_SIZE_LABEL]) if BATCH_SIZE_LABEL in params_list else DEFAULT_BATCH_SIZE
    params[TEST_SIZE_LABEL] = int(data_params[TEST_SIZE_LABEL]) if TEST_SIZE_LABEL in params_list else DEFAULT_TEST_SIZE
    params[WINDOW_LABEL] = int(data_params[WINDOW_LABEL]) if WINDOW_LABEL in params_list else DEFAULT_WINDOW
    params[VERSION_LABEL] = int(data_params[VERSION_LABEL]) if VERSION_LABEL in params_list else DEFAULT_VERSION

    if(params[DATASET_LABEL] == WINDOWED_DATASET):
        params[EVAL_SIZE_LABEL] = int(data_params[EVAL_SIZE_LABEL]) if EVAL_SIZE_LABEL in params_list else DEFAULT_EVAL_SIZE
        params[MAX_TRAIN_SIZE_LABEL] = int(data_params[MAX_TRAIN_SIZE_LABEL]) if MAX_TRAIN_SIZE_LABEL in params_list else DEFAULT_MAX_TRAIN_SIZE
        params[N_SPLITS_LABEL] = int(data_params[N_SPLITS_LABEL]) if N_SPLITS_LABEL in params_list else DEFAULT_N_SPLITS
        params[GAP_LABEL] = int(data_params[GAP_LABEL]) if GAP_LABEL in params_list else DEFAULT_GAP
    else:
        params[SPLIT_SIZE_LABEL] = float(data_params[SPLIT_SIZE_LABEL]) if SPLIT_SIZE_LABEL in params_list else DEFAULT_SPLIT_SIZE


    params[PRODUCTION_LABEL] = str2bool(data_params[PRODUCTION_LABEL]) if PRODUCTION_LABEL in params_list else DEFAULT_PRODUCTION
    # params[PROD_PHASE_LABEL] = data_params[PROD_PHASE_LABEL] if PROD_PHASE_LABEL in params_list else DEFAULT_PROD_PHASE

    params[PLOT_LABEL] = str2bool(data_params[PLOT_LABEL]) if PLOT_LABEL in params_list else DEFAULT_PLOT

    if -1 in params.values():
        raise ParameterError(f'Invalid or Missing Data Params:\n {data_params}')

    return params

def check_evaluation_params(eval_params):
    params_list = list(eval_params.keys())

    params = {}
    params[THR_LABEL] = float(eval_params[THR_LABEL]) if THR_LABEL in params_list else DEFAULT_THR
    params[FIELD_LABEL] = eval_params[FIELD_LABEL] if FIELD_LABEL in params_list else -1
    params[SAVE_DIR_LABEL] = eval_params[SAVE_DIR_LABEL] if SAVE_DIR_LABEL in params_list else DEFAULT_SAVE_DIR

    if -1 in params.values():
        raise ParameterError(f'Invalid or Missing Evaluation Params: \n{eval_params}')

    return params



