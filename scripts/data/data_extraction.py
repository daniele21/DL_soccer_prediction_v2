import pandas as pd
from core.time_decorator import timing
from core.file_manager.os_utils import exists
from scripts.constants.configs import DEFAULT_TEST_SIZE

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
        test_size = int(self.params['test_size']) if 'test_size' in list(self.params.keys()) else DEFAULT_TEST_SIZE
        league_dir = self.params['league_dir'] if 'league_dir' in list(self.params.keys()) else None
        update = self.params['update'] if 'update' in list(self.params.keys()) else False

        logger.info(f'> Extracting {league_name} data: train={train}')

        if(train):
            # LOADING TRAINING DATA --> ALL DATA SEASON
            league_path = f'{league_dir}{league_name}/{league_name}_npm={n_prev_match}.csv' \
                    if league_dir is not None else None

            # LEAGUE CSV ALREADY EXISTING
            if(league_path is not None and exists(league_path)):
                league_df = pd.read_csv(league_path, index_col=0)
                league_df = update_league_data(league_df, n_prev_match) if update else league_df
                logger.info('> Updating league data')
                league_df.to_csv(league_path)

            # GENERATING LEAGUE CSV
            else:
                league_df = extract_training_data(league_name, n_prev_match)
                logger.info(f'Saving data at {league_path}')
                league_df.to_csv(league_path)


        else:
            # LOADING JUST THE LAST SEASON
            league_path = f'{league_dir}{league_name}/{league_name}_npm={n_prev_match}.csv' \
                if league_dir is not None else None

            assert league_path is not None

            league_df = pd.read_csv(league_path, index_col=0).iloc[-test_size:]
            # league_df = extract_test_data(league_name, n_prev_match, test_size)

        return league_df


def extract_training_data(league_name, n_prev_match):

    league_df = pd.DataFrame()

    for season_i, path in enumerate(K.get_league_csv_paths(league_name)):
        season_df = extract_season_data(path, season_i, league_name)
        league_df = league_df.append(season_df, sort=False)
        league_df = league_df.reset_index(drop=True)

    league_df = feature_engineering_league(league_df, n_prev_match)

    return league_df


def update_league_data(league_df, n_prev_match):
    logger.info('> Updating league data')
    league_name = list(league_df['league'].unique())[0]

    assert league_name in K.LEAGUE_NAMES, f'Update League Data: Wrong League Name >> {league_name} provided'

    for season_i, path in enumerate(K.get_league_csv_paths(league_name)):
        season_df = extract_season_data(path, season_i, league_name)

        #---------CHECK LAST DATE----------
        last_date = pd.to_datetime(league_df.iloc[-1]['Date'])
        date = season_df.iloc[-1]['Date']

        if(date > last_date):
            update_df = pd.DataFrame()
            update_df = update_df.append(season_df, sort=False)\
                                 .reset_index(drop=True)
            update_df = feature_engineering_league(update_df, n_prev_match)
            update_df = update_df[update_df['Date'] > last_date]
            league_df = league_df.append(update_df).reset_index(drop=True)

        #----------------------------------

    league_df['Date'] = pd.to_datetime(league_df['Date'])

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
    # season_df = season_df.dropna()

    season_df = season_df.reset_index(drop=True)

    return season_df





def extract_test_data(league_name, n_prev_match, test_size):
    league_df = pd.DataFrame()

    paths = K.get_league_csv_paths(league_name)[-2:]
    season_i = len(K.get_league_csv_paths(league_name))

    for path in paths:
        season_df = extract_season_data(path, season_i, league_name)
        league_df = league_df.append(season_df, sort=False)

    league_df = league_df.iloc[-test_size:] if test_size is not None else league_df
    league_df = feature_engineering_league(league_df, n_prev_match)

    return league_df
    
    
    