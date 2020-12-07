import torch
from core.file_manager.loading import load_json, load_object
from core.logger.logging import logger
from scripts.data.constants import load_model_paths
import scripts.data.constants as K

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
    model_path = K.MODEL_PATH[league_name]
    data_config_path = K.DATA_PARAMS[league_name]
    league_config_path = K.LEAGUE_PARAMS[league_name]
    model_config_path = K.MODEL_PARAMS[league_name]
    feat_eng_path = K.FEAT_ENG[league_name]

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

def load_model_config(league_name, model_version, model_name):
    paths = load_model_paths(league_name, model_version, model_name)

    model, config = _load_model_config(paths)

    return model, config


