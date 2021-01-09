# -*- coding: utf-8 -*-

from time import time
import os

from core.str2bool import str2bool
from scripts.constants.configs import HOME, AWAY
from scripts.data import constants as K
from scripts.data.data_extraction import Database_Manager
from scripts.data.preprocessing import data_preprocessing
from scripts.data.feature_engineering import Feature_engineering_v1, Feature_engineering_v2
from scripts.data.datasets import create_test_dataloader, create_training_dataloader
from scripts.utils.utils import logger
from core.file_manager.saving import save_object

def extract_data_league(params):

    db_manager = Database_Manager(params)
    
    # DATA EXTRACTION
    league_csv = db_manager.extract_data_league()
    
    # DATA PREPROCESSING
    input_data = data_preprocessing(league_csv, params)

    return league_csv, input_data

def generate_dataset(input_data, params):

    train = str2bool(params['train'])
    normalize = str2bool(params['normalize'])
    home_data = input_data['home']
    away_data = input_data['away']
    save_dir = params['save_dir']

    if(int(params['version']) == 1):
        home_feat_eng = Feature_engineering_v1(home_data,
                                               normalize=normalize,
                                               field=HOME)

        away_feat_eng = Feature_engineering_v1(away_data,
                                               normalize=normalize,
                                               field=AWAY)

    elif(int(params['version']) == 2):
        home_feat_eng = Feature_engineering_v2(home_data,
                                               normalize=normalize,
                                               field=HOME)
        away_feat_eng = Feature_engineering_v2(away_data,
                                               normalize=normalize,
                                               field=AWAY)

    else:
        raise ValueError('---- Error version number ----')

    feat_eng = {'home':home_feat_eng,
                'away':away_feat_eng}

    data = {'home':home_feat_eng.transforms(home_data, train),
            'away':away_feat_eng.transforms(away_data, train)}
        
    dataloader, in_features = create_training_dataloader(data, params)

    if(save_dir is not None):
        filepath = f'{save_dir}feat_eng'
        # logger.info(f' > Saving Feat.Eng object at {filepath}')
        save_object(feat_eng, filepath)
    
    return dataloader, feat_eng, in_features

def update_data_league(params):
    league_name = params['league_name']
    npm = params['n_prev_match']
    params['train'] = True
    params['update'] = True
    params['test_size'] = 0

    try:
        league_csv, input_data = extract_data_league(params)
        last_date = league_csv.iloc[-1]['Date']

        logger.info(f'> Updating {league_name} npm={npm} at date {last_date}')

    except Exception as error:
        response = {'check':False,
                    'msg':error}
        return response

    response = {'check':True,
                'msg':'Successfull update'}

    return response

