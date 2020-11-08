# -*- coding: utf-8 -*-

from time import time
import os

from scripts.data import constants as K
from scripts.data.data_extraction import Database_Manager
from scripts.data.preprocessing import (data_preprocessing,
                                        get_last_round)
from scripts.data.feature_engineering import Feature_engineering_v1
from scripts.data.datasets import create_dataloader, create_test_dataloader
from scripts.utils.utils import logger, spent_time
from core.file_manager.saving import save_object

def extract_data_league(params):
    
    db_manager = Database_Manager(params)
    
    # DATA EXTRACTION
    league_csv = db_manager.extract_data_league()
    
    # DATA PREPROCESSING
    input_data = data_preprocessing(league_csv, params)

    return input_data

def split_train_test(input_data, test_size=10):
    home = input_data['home_data'].copy(deep=True)
    away = input_data['away_data'].copy(deep=True)
    
    train_home = home[home['f-WD'].isnull()==False]
    train_away = away[away['f-WD'].isnull()==False]
    
#    home = home.iloc[-test_size:]
#    away = away.iloc[-test_size:]
    
    test_home = home[home['f-WD'].isnull()]
    test_away = away[away['f-WD'].isnull()]
    test_home = get_last_round(test_home)
    test_away = get_last_round(test_away)
    
    train_data = {'home_data':train_home, 'away_data':train_away}
    test_data = {'home_data':test_home, 'away_data':test_away}
    
    return train_data, test_data
           

def generate_dataset(input_data, params):
    
    if(int(params['version']) == 1):
        feat_eng = Feature_engineering_v1(input_data,
                                          normalize=params['normalize'])
        
        data = feat_eng.tranforms(input_data)
    else:
        raise ValueError('---- Error version number ----')
        
    dataloader, in_features = create_dataloader(data, params)
    
    path_feat_eng = f'{os.environ["CKP_MODEL_PATH"]}{os.environ["MODEL_NAME"]}/' + \
                     'feat_eng_object'
    logger.info(f' > Saving Feat.Eng object at {path_feat_eng}')
    save_object(feat_eng, path_feat_eng)
    
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






def test_data():
    league_params = {'league_name': K.SERIE_A,
                     'n_prev_match':3
                     }   
    
    data_params = {'window_size':200,
                   'split_size':0.8,
                   'test_size':0,
                   'batch_size':32,
                   'n_workers':0,
                   'version':1,
                   'normalize':True
                   }
    
    input_data = extract_data_league(league_params)
    dataloader, scalers, in_features = generate_dataset(input_data, data_params)
    
if __name__ == '__main__':
    test_data()
    
    
    
    
    