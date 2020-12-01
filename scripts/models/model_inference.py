# -*- coding: utf-8 -*-
import torch

import scripts.data.constants as K
from scripts.data.data_process import extract_data_league
from scripts.data.datasets import create_test_dataloader
from scripts.utils.loading import load_configs


def model_inference(test_data, feat_eng, model, model_name=None, train=False):

    model_name = str(model_name).lower()
    assert model_name == 'home' or model_name == 'away', 'ERROR - evaluate_data: WRONG model_name'

    testset = feat_eng[model_name].transforms(test_data, train=train)
    true_outcome = testset['f-WD']
    testloader = create_test_dataloader(testset.drop('f-WD', axis=1))

    pred_outcome = model.predict(testloader, model_name)

    return pred_outcome, true_outcome

def generate_test_data(league_name):

    league_name = league_name

    model, config = load_configs(league_name)

    league_params = config['league']
    league_params['train'] = False

    league_csv, input_data = extract_data_league(league_params)

    return input_data






