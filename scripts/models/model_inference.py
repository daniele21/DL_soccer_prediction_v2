# -*- coding: utf-8 -*-
from scripts.data.data_process import extract_data_league
from scripts.data.datasets import create_test_dataloader
from scripts.data.postprocessing import labeling_predictions, generate_outcome

def model_inference(test_data, feat_eng, model, model_name=None, train=False):

    model_name = str(model_name).lower()
    assert model_name == 'home' or model_name == 'away', 'ERROR - evaluate_data: WRONG model_name'

    testset = feat_eng[model_name].transforms(test_data, train=train)

    true_outcome = testset['f-WD'] if train else None
    testset = testset.drop('f-WD', axis=1) if train else testset

    testloader = create_test_dataloader(testset)

    pred_outcome = model.predict(testloader, model_name)

    return pred_outcome, true_outcome


def generate_test_data(league_params):

    league_params['train'] = False

    league_csv, input_data = extract_data_league(league_params)

    return input_data

def generate_output(matches_df, predictions, thr):

    outcome_df = generate_outcome(matches_df, predictions, thr)

    if(thr is not None):
        sugg_event = outcome_df[(outcome_df['outcome_1X'] == True) |
                                (outcome_df['outcome_X2'] == True)]

        for i in sugg_event.index:
            if(sugg_event.loc[i, 'outcome_1X'] and not sugg_event.loc[i, 'outcome_X2']):
                sugg_event.loc[i, 'event'] = '1X'
                sugg_event.loc[i, 'prob'] = str(sugg_event.loc[i, 'pred_1X'])
            elif(not sugg_event.loc[i, 'outcome_1X'] and sugg_event.loc[i, 'outcome_X2']):
                sugg_event.loc[i, 'event'] = 'X2'
                sugg_event.loc[i, 'prob'] = str(sugg_event.loc[i, 'pred_X2'])
            elif(sugg_event.loc[i, 'outcome_X2'] and sugg_event.loc[i, 'outcome_1X']):
                #TODO -> definire cosa consigliare in caso di overlapping tra 1X e X2 --> consiglio la X?
                sugg_event.loc[i, 'event'] = '1X / X2'
                sugg_event.loc[i, 'prob'] = str(sugg_event.loc[i, 'pred_1X']) + ' / ' + str(sugg_event.loc[i, 'pred_X2'])

        outcome = sugg_event[['match', 'event', 'prob']]\
                        .set_index('match')\
                        .transpose()\
                        .to_dict()

    else:
        outcome = outcome_df[['match', '1X', 'pred_1X', 'X2', 'pred_X2']]\
                                    .set_index('match')\
                                    .transpose()\
                                    .to_dict()

    return outcome
