# -*- coding: utf-8 -*-
import pandas as pd


def labeling_predictions(predictions, thr, true_series=None):
    pred_df = pd.DataFrame()

    if true_series is not None:
        pred_df['true'] = true_series.values

    bet_choise_list = []

    for i, pred in enumerate(predictions):
        bet_choice = True if pred >= thr else False
        bet_choise_list.append(bet_choice)

    pred_df['pred'] = list(predictions)
    pred_df['to_bet'] = bet_choise_list

    return pred_df

def postprocessing_test_data(test_data, pred_df):
    """

    Args:
        test_data: original dataframe passed to model inference function, without
        any encoding

    Returns:

    """

    data = pd.DataFrame()

    matches = []
    bet_odds = []
    events = []

    for i in test_data.index:
        row = test_data.loc[i]
        team, opponent = row['team'], row['f-opponent']
        bet = row['f-bet-WD']
        home = row['f-home']

        if(home == True):
            matches.append(f'{team} - {opponent}')
            events.append('1X')
        elif(home == False):
            matches.append(f'{opponent} - {team}')
            events.append('X2')
        else:
            raise ValueError('Wrong Home feature')

        bet_odds.append(bet)

    data['match'] = matches
    data['event'] = events
    data['bet'] = bet_odds
    data['pred-WD'] = pred_df['pred'].to_list()
    data['to_bet'] = pred_df['to_bet'].to_list()
    data['true-WD'] = pred_df['true'].to_list()

    return data

def generate_outcome(matches_df, predictions, thr=None):

    outcome_df = pd.DataFrame({'match':[],
                               'home':[],
                               'away':[],
                               '1X':[],
                               'pred_1X': [],
                               'outcome_1X': [],
                               'X2':[],
                               'pred_X2': [],
                               'outcome_X2':[]})

    for field in ['home', 'away']:
        field_df = matches_df[field]
        pred_list = predictions[field]

        for i, index in enumerate(field_df.index):
            home = field_df.loc[index]['f-home']
            team = field_df.loc[index]['team']
            opponent = field_df.loc[index]['f-opponent']
            odd = field_df.loc[index]['f-bet-WD']
            pred = pred_list[i]
            outcome = pred > thr if thr is not None else str(None)

            row = pd.DataFrame()

            if home:
                match = f"{team} - {opponent}"
                if match not in outcome_df['match'].values.tolist():
                    row['match'] = [match]
                    row['home'] = [team]
                    row['away'] = [opponent]
                    row['1X'] = [odd]
                    row['pred_1X'] = [pred]
                    row['outcome_1X'] = [outcome]

                    outcome_df = outcome_df.append(row)
                else:
                    outcome_df.loc[outcome_df['home'] == team, '1X'] = odd
                    outcome_df.loc[outcome_df['home'] == team, 'pred_1X'] = pred
                    outcome_df.loc[outcome_df['home'] == team, 'outcome_1X'] = outcome

            else:
                match = f"{opponent} - {team}"
                if match not in outcome_df['match'].values.tolist():
                    row['match'] = [match]
                    row['home'] = [opponent]
                    row['away'] = [team]
                    row['X2'] = [odd]
                    row['pred_X2'] = [pred]
                    row['outcome_X2'] = [outcome]

                    outcome_df = outcome_df.append(row)
                else:
                    outcome_df.loc[outcome_df['away'] == team, 'X2'] = odd
                    outcome_df.loc[outcome_df['away'] == team, 'pred_X2'] = pred
                    outcome_df.loc[outcome_df['away'] == team, 'outcome_X2'] = outcome

    outcome_df['outcome_1X'] = outcome_df['outcome_1X'].astype(bool)
    outcome_df['outcome_X2'] = outcome_df['outcome_X2'].astype(bool)
    outcome_df = outcome_df.reset_index(drop=True)

    return outcome_df



