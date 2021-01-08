# -*- coding: utf-8 -*-
from scripts.constants.configs import DEFAULT_TEST_SIZE
from scripts.data.data_process import extract_data_league
from scripts.data.datasets import create_test_dataloader
from scripts.data.postprocessing import labeling_predictions, generate_outcome
from scripts.exceptions.param_exc import ParameterError
from scripts.utils.checker import check_data_params


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
    league_params['test_size'] = 0
    league_params['update'] = False

    league_csv, input_data = extract_data_league(league_params)

    return input_data

def generate_output(matches_df, predictions, thr=None):

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

        if(len(sugg_event) > 0):
            outcome = sugg_event.drop(['outcome_1X', 'outcome_X2', 'home', 'away'], axis=1)\
                            .set_index('match')\
                            .transpose()\
                            .to_dict()
            # outcome = sugg_event[['match', 'event', 'prob']]\
            #                 .set_index('match')\
            #                 .transpose()\
            #                 .to_dict()
        else:
            return None

    else:
        outcome = outcome_df[['match', '1X', 'pred_1X', 'X2', 'pred_X2']]\
                                    .set_index('match')\
                                    .transpose()\
                                    .to_dict()

    return outcome

def real_case_inference(model, params, feat_eng):
    field = params['field']

    # test_size = len(model.testloader[field]) if model.testloader is not None else DEFAULT_TEST_SIZE
    test_size = int(params['test_size']) if 'test_size' in list(params.keys()) else DEFAULT_TEST_SIZE

    params = check_data_params(params)
    test_data = generate_test_data(params)

    test_set = test_data[field][-test_size:]
    test_set = test_set[test_set['f-opponent'].isnull() == False]

    pred, true = model_inference(test_set,
                                 feat_eng,
                                 model,
                                 model_name=field,
                                 train=True)

    return test_set, pred, true
