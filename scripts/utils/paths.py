# -*- coding: utf-8 -*-
import os

from scripts.constants.configs import NETWORK_V1, NETWORK_V2


def set_env_var(env_name, value):
    os.environ[env_name] = value
    print(f'{env_name}:{value}')

def init_env_paths(version=''):
    assert version == 1 or version == 2

    if(version == 1):
        version_net = NETWORK_V1
    elif(version == 2):
        version_net = NETWORK_V2
    else:
        version_net = None

    set_env_var('CKP_MODEL_PATH', f'resources/models/{version_net}/')
    set_env_var('RESOURCES_PATH', 'resources/')
    set_env_var('LEAGUE_PATH', 'resources/leagues_data/')
    set_env_var('RESULT_PATH', 'static/')

def get_model_config_paths(model_dir, model_name):
    model_path = f'{model_dir}{model_name}.pth'
    league_params_path = f'{model_dir}1.league_params.json'
    data_params_path = f'{model_dir}2.data_params.json'
    model_params_path = f'{model_dir}3.model_params.json'
    feat_eng_path = f'{model_dir}feat_eng'

    paths = {'league_params': league_params_path,
             'data_params': data_params_path,
             'model_params': model_params_path,
             'model': model_path,
             'feat_eng':feat_eng_path
             }

    return paths


