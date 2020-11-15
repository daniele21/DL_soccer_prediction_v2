import pandas as pd
from core.time_decorator import timing
from core.file_manager.os_utils import exists

from scripts.data.preprocessing import (preprocessing_season,
                                        feature_engineering_league)
from scripts.data import constants as K
from core.logger.logging import logger
from urllib.error import HTTPError

class Database_Manager():
    
    def __init__(self, params):
        self.params = params

    @timing
    def extract_data_league(self):
        league_name = self.params['league_name']
        n_prev_match = int(self.params['n_prev_match'])
        train = bool(self.params['train'])
        test_size = int(self.params['test_size']) if 'test_size' in list(self.params.keys()) else None
        league_dir = self.params['league_dir'] if 'league_dir' in list(self.params.keys()) else None

        logger.info(f'> Extracting {league_name} data: train={train}')

        if(train):
            # LOADING TRAINING DATA --> ALL DATA SEASON
            league_path = f'{league_dir}{league_name}/{league_name}_npm={n_prev_match}.csv' if league_dir is not None else None

            if(league_path is not None and exists(league_path)):
                league_df = pd.read_csv(league_path, index_col=0)
            else:
                league_df = extract_training_data(league_name, n_prev_match)

        else:
            # LOADING JUST THE LAST SEASON
            league_df = extract_test_data(league_name, n_prev_match, test_size)

        return league_df


def extract_season_data(path, season_i, league_name):
    loading = False

    while(loading == False):
        try:
            season_df = pd.read_csv(path, index_col=0)
            loading = True
        except HTTPError as err:
            print(f'Http error: {err}')

    season_df = preprocessing_season(season_df, season_i, league_name)

    # dropping nan rows
    season_df = season_df.dropna()

    season_df = season_df.reset_index(drop=True)

    return season_df



def extract_training_data(league_name, n_prev_match):

    league_df = pd.DataFrame()

    for season_i, path in enumerate(K.get_league_csv_paths(league_name)):
        season_df = extract_season_data(path, season_i, league_name)
        league_df = league_df.append(season_df, sort=False)
        league_df = league_df.reset_index(drop=True)

    league_df = feature_engineering_league(league_df, n_prev_match)

    return league_df



def extract_test_data(league_name, n_prev_match, test_size):
    league_df = pd.DataFrame()

    paths = K.get_league_csv_paths(league_name)[-2:]
    season_i = len(K.get_league_csv_paths(league_name))

    for path in paths:
        season_df = extract_season_data(path, season_i, league_name)
        league_df = league_df.append(season_df, sort=False)

    league_df = league_df.iloc[-test_size:]
    league_df = feature_engineering_league(league_df, n_prev_match)

    return league_df
    
    
    