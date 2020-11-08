# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
from math import ceil
import os
from tqdm import tqdm

from scripts.data import constants as K
from scripts.data import data_cache as cache
from scripts.data.data_utils import (search_previous_matches,
                                     search_future_features,
                                     search_future_WDL,
                                     search_future_opponent,
                                     search_future_home, 
                                     search_future_bet_WD,
                                     compute_outcome_match,
                                     convert_result_1X2_to_WDL)
from core.logger.logging import logger
from core.time_decorator import timing
from multiprocessing import Pool
from functools import partial

def preprocessing_season(season_df, n_season, league_name):
    
    data = season_df.copy(deep=True)
    
    data.insert(0, 'season', n_season)
    data.insert(0, 'league', league_name)
    data.insert(2, 'match_n', np.arange(1, len(data)+1, 1))
    #data = _addRound(data)
    
    data['Date'] = pd.to_datetime(data['Date'], dayfirst=True)
    
    return data

def _addRound(season_csv):
    
    data = season_csv.copy(deep=True)
    n_teams = len(K.SERIE_A_TEAMS)
    
    rounds = []
    
    for i in range(len(data)):
        index = data.iloc[i]['match_n']
        n_round = ceil( 2*index / n_teams)
        rounds.append(n_round)
    
    data.insert(3, 'round', rounds) 
    
    return data

def bind_last_matches(league_df, n_prev_match):

    for i_row in tqdm(range(len(league_df)), desc='Binding Last Matches'):
        row = league_df.iloc[i_row]
        home_team = row['HomeTeam']
        away_team = row['AwayTeam']
        date = row['Date']
        index = row.name

        league_df = _bind_matches(league_df, home_team, date, n_prev_match, index, home=True)
        league_df = _bind_matches(league_df, away_team, date, n_prev_match, index, home=False)

    return league_df

def _bind_matches(league_df, team, date, n_prev_match, index, home):

    prev_matches = {}

    for home_match in [True, False, None]:
        key = 'home' if home_match==True else 'away' if home_match==False else 'none'
        prev_matches[key] = search_previous_matches(league_df, team, date, n_prev_match, home_match)

    home_factor = 'HOME' if home==True else 'AWAY' if home== False else None
    assert home_factor is not None, f'ERROR: bind_matches - Wrong Home Factor'

    for i in range(0, n_prev_match):
        last_home_col = f'{home_factor}_last-{i+1}-home'
        last_away_col = f'{home_factor}_last-{i+1}-away'
        last_match_col = f'{home_factor}_last-{i+1}'

        league_df.loc[index, last_home_col] = compute_outcome_match(team, prev_matches['home'], i)
        league_df.loc[index, last_away_col] = compute_outcome_match(team, prev_matches['away'], i)
        league_df.loc[index, last_match_col] = compute_outcome_match(team, prev_matches['none'], i)

    return league_df

def _bind_trend_last_previous_match(league_df, n_prev_match):
    
    for i_row in range(len(league_df)):
        row = league_df.iloc[i_row]
        home_team = row['HomeTeam']
        away_team = row['AwayTeam']
#        season = row['season']
        date = row['Date']
        index = row.name
        
        # HOME TEAM
        home_prev_matches = search_previous_matches(league_df, home_team, date, n_prev_match, home=True)
        away_prev_matches = search_previous_matches(league_df, home_team, date, n_prev_match, home=False)
        prev_matches = search_previous_matches(league_df, home_team, date, n_prev_match, home=None)
        
        for i in range(0, n_prev_match):
            last_home_col = 'HOME_last-{}-home'.format(i+1)
            last_away_col = 'HOME_last-{}-away'.format(i+1)
            last_match_col = 'HOME_last-{}'.format(i+1)
            
            league_df.loc[index, last_home_col] = compute_outcome_match(home_team, home_prev_matches, i)
            league_df.loc[index, last_away_col] = compute_outcome_match(home_team, away_prev_matches, i)
            league_df.loc[index, last_match_col] = compute_outcome_match(home_team, prev_matches, i)
                    
        
        # AWAY TEAM
        home_prev_matches = search_previous_matches(league_df, away_team, date, n_prev_match, home=True)
        away_prev_matches = search_previous_matches(league_df, away_team, date, n_prev_match, home=False)
        prev_matches = search_previous_matches(league_df, away_team, date, n_prev_match, home=None)
        
        for i in range(0, n_prev_match):
            last_home_col = 'AWAY_last-{}-home'.format(i+1)
            last_away_col = 'AWAY_last-{}-away'.format(i+1)
            last_match_col = 'AWAY_last-{}'.format(i+1)
            
            league_df.loc[index, last_home_col] = compute_outcome_match(away_team, home_prev_matches, i)
            league_df.loc[index, last_away_col] = compute_outcome_match(away_team, away_prev_matches, i)
            league_df.loc[index, last_match_col] = compute_outcome_match(away_team, prev_matches, i)
        
    return league_df
        

def feature_engineering_league(league_df, n_prev_match):
    
    logger.info('\t\t\t > Feature Engineering for the league')
    
    # league_df = league_df.set_index('match_n')
    
    league_df = league_df.rename(columns={'B365H':'bet_1',
                                          'B365D':'bet_X',
                                          'B365A':'bet_2',
                                          
                                          'FTR':'result_1X2',
                                          'FTHG':'home_goals',
                                          'FTAG':'away_goals'})
    
    league_df.loc[league_df['result_1X2'] == 'H', ['result_1X2']] = '1'
    league_df.loc[league_df['result_1X2'] == 'D', ['result_1X2']] = 'X'
    league_df.loc[league_df['result_1X2'] == 'A', ['result_1X2']] = '2'
    
    league_df = league_df[['league', 'season', 'Date',
                           'HomeTeam', 'AwayTeam', 'home_goals',
                           'away_goals', 'result_1X2',
                           'bet_1', 'bet_X', 'bet_2']]
    
    league_df = league_df.reset_index(drop=True)


    league_df = bind_last_matches(league_df, n_prev_match)

    # league_df = _bind_trend_last_previous_match(league_df, n_prev_match)

    return league_df


def _split_teams_one_row(data, i_row, n_prev_match, home):
    row = data.iloc[i_row]

    assert home == True or home == False, 'ERROR: _split_teams_one_row -> Wrong home value'

    team = row['HomeTeam'] if home==True else row['AwayTeam']
    opponent = row['AwayTeam'] if home==True else row['HomeTeam']
    date = row['Date']
    goal_scored = row['home_goals'] if home==True else row['away_goals']
    goal_conceded = row['away_goals'] if home==True else row['home_goals']
    result_1X2 = row['result_1X2']
    season = row['season']
    league = row['league']

    f_home, f_opponent, f_bet_WD, f_WDL, f_WD = search_future_features(data, team, i_row, season)

    team_features = {'league':league,
                     'season':season,
                     'team': team,
                     'opponent': opponent,
                     'date':date,
                     'goal_scored': goal_scored,
                     'goal_conceded': goal_conceded,
                     'result-WDL': convert_result_1X2_to_WDL(result_1X2, home),
                     'home': home,
                     'f-opponent': f_opponent,
                     'f-home': f_home,
                     'f-bet-WD': f_bet_WD,
                     'f-result-WDL': f_WDL,
                     'f-WD': f_WD
                     }

    home_factor = 'HOME' if home else 'AWAY'
    for n in range(1, n_prev_match + 1):
        team_features[f'last-{n}_home'] = row[f'{home_factor}_last-{n}-home']
        team_features[f'last-{n}_home'] = row[f'{home_factor}_last-{n}-home']
        team_features[f'last-{n}_home'] = row[f'{home_factor}_last-{n}-home']

        team_features[f'last-{n}_away'] = row[f'{home_factor}_last-{n}-away']
        team_features[f'last-{n}_away'] = row[f'{home_factor}_last-{n}-away']
        team_features[f'last-{n}_away'] = row[f'{home_factor}_last-{n}-away']

        team_features[f'last-{n}'] = row[f'{home_factor}_last-{n}']
        team_features[f'last-{n}'] = row[f'{home_factor}_last-{n}']
        team_features[f'last-{n}'] = row[f'{home_factor}_last-{n}']

    team_features['bet-WD'] = 1 / ((1 / row['bet_1']) + (1 / row['bet_X']))

    return team_features

# def _split_teams_one_row(data, i_row, n_prev_match):
#
#     row = data.iloc[i_row]
#
#     # HOME TEAM
#     team = row['HomeTeam']
#     opponent = row['AwayTeam']
#     goal_scored = row['home_goals']
#     goal_conceded = row['away_goals']
#     result_1X2 = row['result_1X2']
#     season = row['season']
#
#     f_home, f_opponent, f_bet_WD, f_WDL, f_WD = search_future_features(data, team, i_row, season)
#
#     home_team = {'team'         : team,
#                  'opponent'     : opponent,
#                  'goal_scored'  : goal_scored,
#                  'goal_conceded': goal_conceded,
#                  'result-WDL'   : convert_result_1X2_to_WDL(result_1X2, home=True),
#                  'home'         : True,
#                  'f-opponent'   : f_opponent,
#                  'f-home'       : f_home,
#                  'f-bet-WD'     : f_bet_WD,
#                  'f-result-WDL' : f_WDL,
#                  'f-WD'         : f_WD
#                 }
#     for n in range(1, n_prev_match+1):
#         home_team[f'last-{n}_home'] = row[f'HOME_last-{n}-home']
#         home_team[f'last-{n}_home'] = row[f'HOME_last-{n}-home']
#         home_team[f'last-{n}_home'] = row[f'HOME_last-{n}-home']
#
#         home_team[f'last-{n}_away'] = row[f'HOME_last-{n}-away']
#         home_team[f'last-{n}_away'] = row[f'HOME_last-{n}-away']
#         home_team[f'last-{n}_away'] = row[f'HOME_last-{n}-away']
#
#         home_team[f'last-{n}'] = row[f'HOME_last-{n}']
#         home_team[f'last-{n}'] = row[f'HOME_last-{n}']
#         home_team[f'last-{n}'] = row[f'HOME_last-{n}']
#
#     home_team['bet-WD'] = 1/((1/row['bet_1']) + (1/row['bet_X']))
#
#
#     # AWAY TEAM
#     team = row['AwayTeam']
#     opponent = row['HomeTeam']
#     goal_scored = row['away_goals']
#     goal_conceded = row['home_goals']
#     result_1X2 = row['result_1X2']
#     season = row['season']
#
#     f_home, f_opponent, f_bet_WD, f_WDL, f_WD = search_future_features(data, team, i_row, season)
#
#     away_team = {'team'         : team,
#                  'opponent'     : opponent,
#                  'goal_scored'  : goal_scored,
#                  'goal_conceded': goal_conceded,
#                  'result-WDL'   : convert_result_1X2_to_WDL(result_1X2, home=True),
#                  'home'         : False,
#                  'f-opponent'   : f_opponent,
#                  'f-home'       : f_home,
#                  'f-bet-WD'     : f_bet_WD,
#                  'f-result-WDL' : f_WDL,
#                  'f-WD'         : f_WD
#                  }
#
#     for n in range(1, n_prev_match+1):
#         away_team[f'last-{n}_home'] = row[f'AWAY_last-{n}-home']
#         away_team[f'last-{n}_home'] = row[f'AWAY_last-{n}-home']
#         away_team[f'last-{n}_home'] = row[f'AWAY_last-{n}-home']
#
#         away_team[f'last-{n}_away'] = row[f'AWAY_last-{n}-away']
#         away_team[f'last-{n}_away'] = row[f'AWAY_last-{n}-away']
#         away_team[f'last-{n}_away'] = row[f'AWAY_last-{n}-away']
#
#         away_team[f'last-{n}'] = row[f'AWAY_last-{n}']
#         away_team[f'last-{n}'] = row[f'AWAY_last-{n}']
#         away_team[f'last-{n}'] = row[f'AWAY_last-{n}']
#
#     away_team['bet-WD'] = 1/((1/row['bet_2']) + (1/row['bet_X']))
#
#     return home_team, away_team

def _split_teams(league_df, n_prev_match):
    """
    Splitting matches data into home data and away data

    Args:
        league_df:
        n_prev_match:

    Returns:

    """
    data = league_df.copy(deep=True)
    home_team_df = pd.DataFrame()
    away_team_df = pd.DataFrame()
    
    for i_row in range(len(data)):
        home_team_dict = _split_teams_one_row(data, i_row, n_prev_match, home=True)
        away_team_dict = _split_teams_one_row(data, i_row, n_prev_match, home=False)
   
        home_team_df = home_team_df.append(pd.DataFrame(home_team_dict, index=[i_row]))
        away_team_df = away_team_df.append(pd.DataFrame(away_team_dict, index=[i_row]))
    
    return {'home':home_team_df,
            'away':away_team_df}
        
@timing
def data_preprocessing(league_df, params):

    n_prev_match = int(params['n_prev_match'])
    train = bool(params['train'])
    test_size = int(params['test_size'])

    data = league_df.copy(deep=True)

    if(train == False):
        data = data.iloc[-test_size:]

    input_data = _split_teams(data, n_prev_match)
    home_data = input_data['home']
    away_data = input_data['away']

    return input_data


def get_last_round(test_data):
    
    indexes = test_data.index.to_list()
    
    gaps = [[s, e] for s, e in zip(indexes, indexes[1:]) if s+1 < e]
    edges = iter(indexes[:1] + sum(gaps, []) + indexes[-1:])
    cons_list = list(zip(edges, edges))
    
    last_round = cons_list[-1]
    
    last_round_df = test_data.loc[last_round[0] : last_round[1]]
    
    return last_round_df
    
    
    
            
            
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        