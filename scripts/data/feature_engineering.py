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
        scaler = MinMaxScaler(feature_range=(0,1)).fit(series.values.reshape(-1,1))
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

    def __init__(self, field_data, normalize):

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

    # def decoding(self, input_data, outcome=None, true_outcome=None):
    #     output_home = pd.DataFrame()
    #     output_away = pd.DataFrame()
    #
    #     x_home = input_data['home']
    #     x_away = input_data['away']
    #
    #     if (outcome is not None):
    #         pred_home = outcome['home']
    #         pred_away = outcome['away']
    #
    #         output_home['WD'] = pred_home
    #         output_away['WD'] = pred_away
    #
    #     output_home['team'] = x_home['team'].apply(_decoding,
    #                                                args=(self.team_decoder,)).to_list()
    #     output_home['opponent'] = x_home['f-opponent'].apply(_decoding,
    #                                                          args=(self.team_decoder,)).to_list()
    #
    #     #        output_home['home'] = x_home['f-home']
    #
    #     output_away['team'] = x_away['team'].apply(_decoding,
    #                                                args=(self.team_decoder,)).to_list()
    #     output_away['opponent'] = x_away['f-opponent'].apply(_decoding,
    #                                                          args=(self.team_decoder,)).to_list()
    #     #        output_away['home'] = x_away['f-home']
    #
    #     output_home['bet_WD'] = self.home_bet_scaler.inverse_transform(x_home['f-bet-WD'].values)
    #     output_away['bet_WD'] = self.away_bet_scaler.inverse_transform(x_away['f-bet-WD'].values)
    #
    #     #        print(output_home)
    #
    #     if (true_outcome is not None):
    #         output_home['true-WD'] = true_outcome['home']
    #         output_away['true-WD'] = true_outcome['away']
    #
    #     output = {'home': output_home,
    #               'away': output_away}
    #
    #     return output


class Feature_engineering_v2():
    
    def __init__(self, input_data, normalize):
        
        self.normalize = normalize
        
        home_data = input_data['home_data'].copy(deep=True)
        away_data = input_data['away_data'].copy(deep=True)
        # Encoder/Decoder for TEAM, OPPONENT, F-OPPONENT
        self.team_encoder, self.team_decoder = _teams_encoding(home_data['team'])
        # Encoder/Decoder for RESULT_WDL, F-RESULT_WDL, LAST-n[-HOME/AWAY]
        self.res_encoder, self.res_decoder = _result_encoding(home_data['result-WDL'])
        
        if(self.normalize):
            self.goal_scored_scaler = _norm_scaler(home_data['goal_scored'], one_feature=True)
            self.goal_conceded_scaler = _norm_scaler(home_data['goal_conceded'], one_feature=True) 
            
            self.home_bet_scaler = _norm_scaler(home_data['bet-WD'], one_feature=True)
            self.away_bet_scaler = _norm_scaler(away_data['bet-WD'], one_feature=True)
        
    def tranforms(self, input_data):
        
        home_data = input_data['home_data'].copy(deep=True)
        away_data = input_data['away_data'].copy(deep=True)
        # Removing home factor
        home_data = home_data.drop('home', axis=1)
        away_data = away_data.drop('home', axis=1)
        
        home_data = home_data.drop('f-result-WDL', axis=1)
        away_data = away_data.drop('f-result-WDL', axis=1)
        
        # Last-n[-HOME/-AWAY] columns
        columns = home_data.columns
        last_n_cols = [col for col in columns if 'last-' in col]
        # Dropping last-n{-HOME/AWAY} cols
        for col in last_n_cols:
            home_data.drop(col, axis=1)
        
       # Fillna
        home_data['f-opponent'] = home_data['f-opponent'].fillna('None')
        home_data['f-home'] = home_data['f-home'].fillna(0)
        home_data['f-bet-WD'] = home_data['f-bet-WD'].fillna(0)
#        home_data['f-result-WDL'] = home_data['f-result-WDL'].fillna('None')
        home_data['f-WD'] = home_data['f-WD'].fillna(0)
        home_data['bet-WD'] = home_data['bet-WD'].fillna(0)
        
        away_data['f-opponent'] = away_data['f-opponent'].fillna('None')
        away_data['f-home'] = away_data['f-home'].fillna(0)
        away_data['f-bet-WD'] = away_data['f-bet-WD'].fillna(0)
#        away_data['f-result-WDL'] = away_data['f-result-WDL'].fillna('None')
        away_data['f-WD'] = away_data['f-WD'].fillna(0)
        away_data['bet-WD'] = away_data['bet-WD'].fillna(0)
        
        
        
        # From Categorical to Numeric
        home_data['team'] = home_data['team'].apply(_encoding, args=(self.team_encoder,))
        home_data['opponent'] = home_data['opponent'].apply(_encoding, args=(self.team_encoder,))
        home_data['f-opponent'] = home_data['f-opponent'].apply(_encoding, args=(self.team_encoder,))
        
        away_data['team'] = away_data['team'].apply(_encoding, args=(self.team_encoder,))
        away_data['opponent'] = away_data['opponent'].apply(_encoding, args=(self.team_encoder,))
        away_data['f-opponent'] = away_data['f-opponent'].apply(_encoding, args=(self.team_encoder,))
        
        home_data['result-WDL'] = home_data['result-WDL'].apply(_encoding, args=(self.res_encoder,))
#        home_data['f-result-WDL'] = home_data['f-result-WDL'].apply(_encoding, args=(res_encoder,))
        
        away_data['result-WDL'] = away_data['result-WDL'].apply(_encoding, args=(self.res_encoder,))
#        away_data['f-result-WDL'] = away_data['f-result-WDL'].apply(_encoding, args=(res_encoder,))
        
        
            
        # Normalization
        if(self.normalize):
            
            home_data['goal_scored'] = _scale(home_data['goal_scored'],
                                              self.goal_scored_scaler,
                                              one_feature=True)
    
            home_data['goal_conceded'] = _scale(home_data['goal_conceded'],
                                                          self.goal_conceded_scaler,
                                                          one_feature=True)
    
            away_data['goal_scored'] = _scale(away_data['goal_scored'],
                                              self.goal_conceded_scaler,
                                              one_feature=True)
    
            away_data['goal_conceded'] = _scale(away_data['goal_conceded'],
                                                          self.goal_scored_scaler,
                                                          one_feature=True)
            
            home_data['f-bet-WD'] = _scale(home_data['f-bet-WD'],
                                           self.home_bet_scaler,
                                           one_feature=True)
            
            home_data['bet-WD'] = _scale(home_data['bet-WD'],
                                           self.home_bet_scaler,
                                           one_feature=True)
            
            away_data['f-bet-WD'] = _scale(away_data['f-bet-WD'],
                                           self.away_bet_scaler,
                                           one_feature=True)
            
            away_data['bet-WD'] = _scale(away_data['bet-WD'],
                                           self.away_bet_scaler,
                                           one_feature=True)
            
        dataset = {'home':home_data,
                   'away':away_data}   
        
        return dataset
    
    def decoding(self, input_data, outcome, true_outcome):
        output_home = pd.DataFrame()
        output_away = pd.DataFrame()
        
        x_home = input_data['home']
        x_away = input_data['away']
        
        pred_home = outcome['home']
        pred_away = outcome['away']
        
        output_home['team'] = x_home['team'].apply(_decoding,
                                                   args=(self.team_decoder,))
        output_home['opponent'] = x_home['f-opponent'].apply(_decoding,
                                                             args=(self.team_decoder,))
        
        output_away['team'] = x_away['team'].apply(_decoding,
                                                   args=(self.team_decoder,))
        output_away['f-opponent'] = x_away['f-opponent'].apply(_decoding,
                                                               args=(self.team_decoder,))
        
        output_home['bet_WD'] = self.home_bet_scaler.inverse_transform(x_home['f-bet-WD'].values)
        output_away['bet_WD'] = self.away_bet_scaler.inverse_transform(x_away['f-bet-WD'].values)

    
        output_home['WD'] = pred_home
        output_away['WD'] = pred_away
        
        output_home['true-WD'] = true_outcome['home']
        output_away['true-WD'] = true_outcome['away']
        
        output = {'home':output_home, 'away':output_away}
        
        return output
    