from _ast import Dict

import torch
from core.file_manager.loading import load_json, load_object
from core.logger.logging import logger
from scripts.constants.league import LEAGUE_NAMES
from scripts.constants.paths import MODEL_DIR, PRODUCTION_DIR
from scripts.data.constants import load_model_paths
# import scripts.constants.paths as K

def load_model(ckp_path):
    if(torch.cuda.is_available()):
        return torch.load(ckp_path)
    else:
        return torch.load(ckp_path, map_location=torch.device('cpu'))

def _load_model_config(paths):
    model_path = paths['model']
    model_config_path = paths['model_params']
    league_config_path = paths['league_params']
    data_config_path = paths['data_params']
    feat_eng_path = paths['feat_eng']

    model = load_model(model_path)
    logger.info(f'\n> Loading Model: {model_path}')

    model_config = load_json(model_config_path)
    data_config = load_json(data_config_path)
    league_config = load_json(league_config_path)
    logger.info(f'\n> Loading Params')

    feat_eng = load_object(feat_eng_path)
    logger.info(f'\n> Loading Feature Engineering object')

    config = {'data': data_config,
              'league': league_config,
              'feat_eng': feat_eng,
              'model': model_config}

    return model, config

def load_configs(league_name):
    production_paths = load_production_paths()

    try:
        model_path = production_paths[league_name]['model_path']
        data_config_path = production_paths[league_name]['data_params']
        league_config_path = production_paths[league_name]['league_params']
        model_config_path = production_paths[league_name]['model_params']
        feat_eng_path = production_paths[league_name]['feat_eng']

        model = load_model(model_path)
        logger.info(f'> Loading Model: {model_path}')

        model_config = load_json(model_config_path)
        data_config = load_json(data_config_path)
        league_config = load_json(league_config_path)
        logger.info(f'> Loading Params')

        feat_eng = load_object(feat_eng_path)
        logger.info(f'> Loading Feature Engineering object\n\n')

        config = {'data': data_config,
                  'league': league_config,
                  'feat_eng': feat_eng,
                  'model': model_config}

    except Exception as error:
        model, config = None, None
        logger.info(f'Loading Model: {league_name} not found: {error}')

    return model, config

def load_model_config(league_name, model_version, model_name):
    paths = load_model_paths(league_name, model_version, model_name)

    model, config = _load_model_config(paths)

    return model, config


def load_model_paths(league_name, model_version, model_name):
    league_name = league_name.lower()
    league = league_name if league_name in LEAGUE_NAMES else None
    model_version = 'network_v1' if model_version == 1 else 'network_v2' if model_version == 2 else None

    if league is not None and model_version is not None:
        folder_dir = f'{MODEL_DIR}{model_version}/{league}/{model_name}/'
        model_path = f'{folder_dir}{model_name}.pth'
        league_params_path = f'{folder_dir}1.league_params.json'
        data_params_path = f'{folder_dir}2.data_params.json'
        model_params_path = f'{folder_dir}3.model_params.json'
        feat_eng_path = f'{folder_dir}feat_eng'

        paths = {'model': model_path,
                 'model_params': model_params_path,
                 'league_params': league_params_path,
                 'data_params': data_params_path,
                 'feat_eng': feat_eng_path}

        return paths

    else:
        raise ValueError('LOAD MDOEL PATHS: Wrong League Name provided')

# def get_league_csv_paths(league_name):
#     if (league_name == K.SERIE_A):
#         paths = K.SERIE_A_PATH
#
#     elif (league_name == K.PREMIER):
#         paths = K.PREMIER_PATH
#
#     elif (league_name == K.JUPILIER):
#         paths = K.JUPILIER_PATH
#
#     return paths

def load_configs_from_paths(paths):
    """

    Args:
        paths: dict{'league_params',
                    'data_params',
                    'model_params',
                    'model',
                    'feat_eng'}

    Returns:
        params: dict{'league',
                    'data',
                    'model',
                    'feat_eng'}

        model: torch Model
    """
    league_params_path = paths['league_params'] if 'league_params' in list(paths.keys()) else None
    data_params_path = paths['data_params'] if 'data_params' in list(paths.keys()) else None
    model_params_path = paths['model_params'] if 'model_params' in list(paths.keys()) else None
    model_path = paths['model'] if 'model' in list(paths.keys()) else None
    feat_eng_path = paths['feat_eng'] if 'feat_eng' in list(paths.keys()) else None

    params = {}
    model = None

    if league_params_path:
        params['league'] = load_json(league_params_path)

    if data_params_path:
        params['data'] = load_json(data_params_path)

    if model_params_path:
        params['model'] = load_json(model_params_path)

    if feat_eng_path:
        params['feat_eng'] = load_object(feat_eng_path)

    if model_path:
        model = load_model(model_path)

    return params, model

def load_production_paths():
    config_path = f'{PRODUCTION_DIR}production_paths.json'

    paths_json = load_json(config_path)

    return paths_json