# -*- coding: utf-8 -*-

from time import time
import os

from scripts.data import constants as K
from scripts.data.data_extraction import Database_Manager
from scripts.data.preprocessing import data_preprocessing
from scripts.data.feature_engineering import Feature_engineering_v1
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

    train = bool(params['train'])
    normalize = bool(params['normalize'])
    home_data = input_data['home']
    away_data = input_data['away']
    save_dir = params['save_dir']

    if(int(params['version']) == 1):
        home_feat_eng = Feature_engineering_v1(home_data, normalize=normalize)
        away_feat_eng = Feature_engineering_v1(away_data, normalize=normalize)

        feat_eng = {'home':home_feat_eng,
                    'away':away_feat_eng}

        data = {'home':home_feat_eng.transforms(home_data, train),
                'away':away_feat_eng.transforms(away_data, train)}

    else:
        raise ValueError('---- Error version number ----')
        
    dataloader, in_features = create_training_dataloader(data, params)

    if(save_dir is not None):
        filepath = f'{save_dir}feat_eng'
        logger.info(f' > Saving Feat.Eng object at {filepath}')
        save_object(feat_eng, filepath)
    
    return dataloader, feat_eng, in_features

def test_set_integration(test_data, matches_df):
    
    for field in ['home_data', 'away_data']:
        test_data[field] = test_data[field].reset_index(drop=True)
        
        for i_row in range(len(test_data[field])):
            row = test_data[field].iloc[i_row]
            team = row['team']
            
            f_home = None
            
            if(team in matches_df['home'].to_list()):
                f_home = 1
                match_df = matches_df[matches_df['home'] == team]
                opponent = match_df['away'].item()
                bet = match_df['home_bet'].item()
                
#                test_data['home_data'].loc[i_row, 'f-opponent'] = opponent
#                test_data['home_data'].loc[i_row, 'f-bet-WD'] = bet
#                test_data['home_data'].loc[i_row, 'f-home'] = f_home
                
            elif(team in matches_df['away'].to_list()):
                f_home = 0
                match_df = matches_df[matches_df['away'] == team]
                opponent = match_df['home'].item()
                bet = match_df['away_bet'].item()
                
#                test_data['away_data'].loc[i_row, 'f-opponent'] = opponent
#                test_data['away_data'].loc[i_row, 'f-bet-WD'] = bet
#                test_data['away_data'].loc[i_row, 'f-home'] = f_home

            if(f_home is not None):
                test_data[field].loc[i_row, 'f-opponent'] = opponent
                test_data[field].loc[i_row, 'f-bet-WD'] = bet
                test_data[field].loc[i_row, 'f-home'] = f_home
    
    
    return test_data


def generate_test_dataset(test_data, feat_eng, inference):
    
    data = feat_eng.tranforms(test_data, production=True)
    
    for x in ['home', 'away']:
        data[x] = data[x].drop(data[x][data[x]['f-opponent'] == 1].index)
    
    dataloader = create_test_dataloader(data, inference=inference)
    
    return dataloader
    
    
    