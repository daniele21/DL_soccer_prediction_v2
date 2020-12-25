import os

from scripts.constants.configs import BASE_DATASET, WINDOWED_DATASET
from scripts.models.base import Base_Model
from scripts.models.k_fold_model import K_fold_model
from scripts.utils.date_utils import get_timestamp_string


def init_model(dataset_type):

    if(dataset_type == BASE_DATASET):
        model = Base_Model
    elif(dataset_type == WINDOWED_DATASET):
        model = K_fold_model
    else:
        raise ValueError(f'Wrong Dataset type provided: {dataset_type}')

    return model

def model_directory(league_params, data_params, model_params):
    league_name = league_params['league_name']
    dataset_type = data_params['dataset']
    feat_eng_v = data_params['version']
    network_v = model_params['version']

    name = f'{dataset_type}_fe={feat_eng_v}_net={network_v}'

    timestamp = get_timestamp_string()
    ckp_model_path = os.environ['CKP_MODEL_PATH']

    model_name = f'{league_name.upper()}_{timestamp}_{name}'
    model_dir = f'{ckp_model_path}{league_name}/{model_name}/'

    return model_name, model_dir