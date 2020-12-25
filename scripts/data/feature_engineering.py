# -*- coding: utf-8 -*-

import pandas as pd
from sklearn.preprocessing import StandardScaler, MinMaxScaler

def __categorical_encoding(series, pad_space=0):
    
    encoder = {x:(i+pad_space) for i, x in enumerate(series.unique())}
    decoder = {(i+pad_space):x for i, x in enumerate(series.unique())}
    
    return encoder, decoder

def _teams_encoding(series):
    
    encoder, decoder = __categorical_encoding(series, pad_space=2)

    encoder['UNK']=0
    encoder['None']=1
    
    decoder[0]='UNK'
    decoder[1]='None'
    
    return encoder, decoder


def _result_encoding():
    encoder = {0:0,
               1:1,
               3:2}

    decoder = {0:0,
               1:1,
               2:3}

    return encoder, decoder
#
# def _result_encoding(series):
#
#     encoder, decoder = __categorical_encoding(series, pad_space=1)
#
#     encoder['None']=0
#     decoder[0]='None'
#
#     return encoder, decoder
    
def _encoding(x, encoder):
    try:
        result = encoder[x]
    except:
        print(f'>>>> {x} not found --> substituted with UNK')
        result = 0
        
    return result

def _decoding(x, decoder):
    return decoder[x]

def _norm_scaler(series, one_feature=False):
    
    if(one_feature):
        scaler = StandardScaler().fit(series.values.reshape(-1,1))
    else:
        scaler = StandardScaler().fit(series.values)
    
    return scaler

def _minmax_scaler(series, one_feature=False):
    if(one_feature):
        scaler = MinMaxScaler(feature_range=(0, 1)).fit(series.values.reshape(-1,1))
    else:
        scaler = MinMaxScaler(feature_range=(0, 1)).fit(series.values)

    return scaler

def _scale(series, scaler, one_feature=False):
    
    if(one_feature):
        scaled_values = scaler.transform(series.values.reshape(-1,1))
    else:
        scaled_values = scaler.transform(series.values)
    
    return scaled_values


class Feature_engineering_v1():

    def __init__(self, field_data, normalize, field):

        self.normalize = normalize

        data = field_data.copy(deep=True)

        # Encoder/Decoder for TEAM, OPPONENT, F-OPPONENT
        self.team_encoder, self.team_decoder = _teams_encoding(data['team'])

        # Encoder/Decoder for RESULT_WDL, F-RESULT_WDL, LAST-n[-HOME/AWAY]
        self.res_encoder, self.res_decoder = _result_encoding()

        if (self.normalize):
            self.goal_scaler = _minmax_scaler(data['goal_scored'], one_feature=True)
            self.last_match_scaler = _minmax_scaler(data[data.columns[-1]], one_feature=True)
            self.bet_scaler = _norm_scaler(data['bet-WD'], one_feature=True)

    def transforms(self, field_data, train):

        data = field_data.copy(deep=True)

        # Removing useless features
        data = data.drop('home', axis=1)
        data = data.drop('league', axis=1)
        data = data.drop('season', axis=1)
        data = data.drop('date', axis=1)
        data = data.drop('f-result-WDL', axis=1)

        # Last-n[-HOME/-AWAY] columns
        columns = data.columns
        selected_columns = ['team', 'opponent', 'goal_scored', 'goal_conceded',
                            'points', 'f-opponent', 'f-home', 'f-bet-WD',
                            'bet-WD', 'f-WD']

        last_n_cols = [col for col in columns if 'last-' in col]
        selected_columns.extend(last_n_cols)
        data = data[selected_columns]
        data = data.drop('f-WD', axis=1) if (train == False) else data

        for col in last_n_cols:
            data[col] = data[col].fillna(0)
            data[col] = _scale(data[col],
                               self.last_match_scaler,
                               one_feature=True)


        # assert data['f-opponent'].isnull().sum() <= 12, 'ERROR: Transform Feat.Eng V1 --> to many NaNs'
        if(train):
            data = data.drop(data[data['f-opponent'].isnull()].index)
        else:
            data = data.drop(data[data['f-opponent'].isnull()].index)

        assert data.isnull().sum().sum() == 0, 'ERROR: Transform Feat.Eng V1 --> There are some NaNs'

        # From Categorical to Numeric
        data['team'] = data['team'].apply(_encoding, args=(self.team_encoder,))
        data['opponent'] = data['opponent'].apply(_encoding, args=(self.team_encoder,))
        data['f-opponent'] = data['f-opponent'].apply(_encoding, args=(self.team_encoder,))
        data['points'] = data['points'].astype(int).apply(_encoding, args=(self.res_encoder,))

        # Normalization
        if (self.normalize):
            data['goal_scored'] = _scale(data['goal_scored'],
                                              self.goal_scaler,
                                              one_feature=True)

            data['goal_conceded'] = _scale(data['goal_conceded'],
                                                self.goal_scaler,
                                                one_feature=True)

            data['f-bet-WD'] = _scale(data['f-bet-WD'],
                                           self.bet_scaler,
                                           one_feature=True)

            data['bet-WD'] = _scale(data['bet-WD'],
                                         self.bet_scaler,
                                         one_feature=True)



        return data

    def decoding(self, input_data):

        data = input_data.copy(deep=True)

        data['team'] = data['team'].apply(_decoding,
                                                   args=(self.team_decoder,)).to_list()
        data['f-opponent'] = data['f-opponent'].apply(_decoding,
                                                             args=(self.team_decoder,)).to_list()

        data['f-bet_WD'] = self.bet_scaler.inverse_transform(data['f-bet-WD'].values)

        return data


class Feature_engineering_v2():

    def __init__(self, field_data, normalize, field):

        self.normalize = normalize
        self.field = field

        data = field_data.copy(deep=True)

        # Encoder/Decoder for TEAM, OPPONENT, F-OPPONENT
        self.team_encoder, self.team_decoder = _teams_encoding(data['team'])

        # Encoder/Decoder for RESULT_WDL, F-RESULT_WDL, LAST-n[-HOME/AWAY]
        self.res_encoder, self.res_decoder = _result_encoding()

        if (self.normalize):
            self.goal_scaler = _minmax_scaler(data['goal_scored'], one_feature=True)
            self.last_match_scaler = _minmax_scaler(data[data.columns[-1]], one_feature=True)
            self.cum_field_points_scaler = _minmax_scaler(data[f'cum_{field}_points'], one_feature=True)
            self.cum_field_goals_scaler = _minmax_scaler(data[f'cum_{field}_goals'], one_feature=True)
            self.league_points_scaler = _minmax_scaler(data['league_points'], one_feature=True)
            self.league_goals_scaler = _minmax_scaler(data['league_goals'], one_feature=True)
            self.point_diff_scaler = _minmax_scaler(data['point_diff'], one_feature=True)
            self.goals_diff_scaler = _minmax_scaler(data['goals_diff'], one_feature=True)
            self.bet_scaler = _norm_scaler(data['bet-WD'], one_feature=True)

    def transforms(self, field_data, train):

        data = field_data.copy(deep=True)

        # Removing useless features
        data = data.drop('home', axis=1)
        data = data.drop('league', axis=1)
        data = data.drop('season', axis=1)
        data = data.drop('date', axis=1)
        data = data.drop('f-result-WDL', axis=1)

        # Last-n[-HOME/-AWAY] columns
        columns = data.columns
        selected_columns = ['team', 'opponent', 'goal_scored', 'goal_conceded',
                            'points', 'f-opponent', 'f-home', 'f-bet-WD',
                            'bet-WD', 'f-WD', f'cum_{self.field}_points',
                            f'cum_{self.field}_goals', 'league_points', 'league_goals',
                            'point_diff', 'goals_diff']

        last_n_cols = [col for col in columns if 'last-' in col]
        selected_columns.extend(last_n_cols)
        data = data[selected_columns]
        data = data.drop('f-WD', axis=1) if (train == False) else data

        for col in last_n_cols:
            data[col] = data[col].fillna(0)
            data[col] = _scale(data[col],
                               self.last_match_scaler,
                               one_feature=True)


        # assert data['f-opponent'].isnull().sum() <= 12, 'ERROR: Transform Feat.Eng V1 --> to many NaNs'
        if(train):
            data = data.drop(data[data['f-opponent'].isnull()].index)
        else:
            data = data.drop(data[data['f-opponent'].isnull()].index)

        assert data.isnull().sum().sum() == 0, 'ERROR: Transform Feat.Eng V1 --> There are some NaNs'

        # From Categorical to Numeric
        data['team'] = data['team'].apply(_encoding, args=(self.team_encoder,))
        data['opponent'] = data['opponent'].apply(_encoding, args=(self.team_encoder,))
        data['f-opponent'] = data['f-opponent'].apply(_encoding, args=(self.team_encoder,))
        data['points'] = data['points'].astype(int).apply(_encoding, args=(self.res_encoder,))

        # Normalization
        if (self.normalize):
            data['goal_scored'] = _scale(data['goal_scored'],
                                              self.goal_scaler,
                                              one_feature=True)

            data['goal_conceded'] = _scale(data['goal_conceded'],
                                                self.goal_scaler,
                                                one_feature=True)

            data['f-bet-WD'] = _scale(data['f-bet-WD'],
                                           self.bet_scaler,
                                           one_feature=True)

            data['bet-WD'] = _scale(data['bet-WD'],
                                         self.bet_scaler,
                                         one_feature=True)

            data[f'cum_{self.field}_points'] = _scale(data[f'cum_{self.field}_points'],
                                                      self.cum_field_points_scaler,
                                                      one_feature=True)

            data[f'cum_{self.field}_goals'] = _scale(data[f'cum_{self.field}_goals'],
                                                      self.cum_field_goals_scaler,
                                                      one_feature=True)

            data['league_points'] = _scale(data['league_points'],
                                                 self.league_points_scaler,
                                                 one_feature=True)

            data['league_goals'] = _scale(data['league_goals'],
                                           self.league_goals_scaler,
                                           one_feature=True)

            data['point_diff'] = _scale(data['point_diff'],
                                          self.point_diff_scaler,
                                          one_feature=True)

            data['goals_diff'] = _scale(data['goals_diff'],
                                        self.goals_diff_scaler,
                                        one_feature=True)

        return data

    def decoding(self, input_data):

        data = input_data.copy(deep=True)

        data['team'] = data['team'].apply(_decoding,
                                                   args=(self.team_decoder,)).to_list()
        data['f-opponent'] = data['f-opponent'].apply(_decoding,
                                                             args=(self.team_decoder,)).to_list()

        data['f-bet_WD'] = self.bet_scaler.inverse_transform(data['f-bet-WD'].values)

        return data
