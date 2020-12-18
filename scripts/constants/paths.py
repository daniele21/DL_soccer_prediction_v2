from scripts.constants.league import SERIE_A, PREMIER, JUPILIER

STATIC_DIR = 'api/v1/static/'
DATA_DIR = 'resources/leagues_data/'
MODEL_DIR = 'resources/models/'
SERIE_A_MODEL_NAME = '2020-11-30_17:08:16.400127-serie_a-model_v1.0'
PREMIER_MODEL_NAME = '2020-10-29_10:34:18.765085-premier_league-round=7_v1.0'
JUPILIER_MODEL_NAME = ''

LEAGUE_DIR = {SERIE_A:f'{DATA_DIR}{SERIE_A}'}

MODEL_PATH = {SERIE_A: f'{MODEL_DIR}{SERIE_A}/{SERIE_A_MODEL_NAME}/{SERIE_A_MODEL_NAME}.pth',
              PREMIER: f'{MODEL_DIR}{PREMIER_MODEL_NAME}/{PREMIER_MODEL_NAME}.pth',
              JUPILIER: f'{MODEL_DIR}{JUPILIER_MODEL_NAME}/{JUPILIER_MODEL_NAME}.pth'}

LEAGUE_PARAMS = {SERIE_A: f'{MODEL_DIR}{SERIE_A}/{SERIE_A_MODEL_NAME}/1.league_params.json',
                 PREMIER: f'{MODEL_DIR}{PREMIER_MODEL_NAME}/1.league_params.json',
                 JUPILIER: f'{MODEL_DIR}{JUPILIER_MODEL_NAME}/1.league_params.json'}

DATA_PARAMS = {SERIE_A: f'{MODEL_DIR}{SERIE_A}/{SERIE_A_MODEL_NAME}/2.data_params.json',
               PREMIER: f'{MODEL_DIR}{PREMIER_MODEL_NAME}/2.data_params.json',
               JUPILIER: f'{MODEL_DIR}{JUPILIER_MODEL_NAME}/2.data_params.json'}

MODEL_PARAMS = {SERIE_A: f'{MODEL_DIR}{SERIE_A}/{SERIE_A_MODEL_NAME}/3.model_params.json',
               PREMIER: f'{MODEL_DIR}{PREMIER_MODEL_NAME}/2.data_params.json',
               JUPILIER: f'{MODEL_DIR}{JUPILIER_MODEL_NAME}/2.data_params.json'}

FEAT_ENG = {SERIE_A: f'{MODEL_DIR}{SERIE_A}/{SERIE_A_MODEL_NAME}/feat_eng',
            PREMIER: f'{MODEL_DIR}{PREMIER_MODEL_NAME}/feat_eng_object',
            JUPILIER: f'{MODEL_DIR}{PREMIER_MODEL_NAME}/feat_eng_object'}

