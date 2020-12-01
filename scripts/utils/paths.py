# -*- coding: utf-8 -*-
import os

def set_env_var(env_name, value):
    os.environ[env_name] = value
    print(f'{env_name}:{value}')

def init_env_paths():
    set_env_var('CKP_MODEL_PATH', 'resources/models/')
    set_env_var('RESOURCES_PATH', 'resources/')
    set_env_var('LEAGUE_PATH', 'resources/leagues_data/')
    set_env_var('RESULT_PATH', 'static/')

