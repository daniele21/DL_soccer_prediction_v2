# -*- coding: utf-8 -*-
import pandas as pd


def labeling_predictions(true_series, predictions, thr):
    pred_df = pd.DataFrame({'true': true_series.values})

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


