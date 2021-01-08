from scripts.constants.league import SERIE_A, PREMIER, JUPILIER

STATIC_DIR = 'api/v1/static/'
DATA_DIR = 'resources/leagues_data/'
MODEL_DIR = 'resources/models/'
PRODUCTION_DIR = 'resources/production/'
SERIE_A_NETWORK = 'network_v1/'
SERIE_A_MODEL_NAME = 'SERIE_A_2020-12-27_17:55:49.780729_windowed_fe=2_net=2'

PRODUCION_SERIA_A = 'SERIE_A_2021-01-06_09:58:31.485528_windowed_fe=2_net=2'
PRODUCTION_PREMIER = 'PREMIER_LEAGUE_2021-01-06_11:22:28.032132_windowed_fe=2_net=2'

# PREMIER_MODEL_NAME = '2020-10-29_10:34:18.765085-premier_league-round=7_v1.0'
JUPILIER_MODEL_NAME = ''

LEAGUE_PARAMS_FILENAME = '1.league_params.json'
DATA_PARAMS_FILENAME = '2.data_params.json'
MODEL_PARAMS_FILENAME = '3.model_params.json'
FEAT_ENG_FILENAME = 'feat_eng'

LEAGUE_DIR = {SERIE_A:f'{DATA_DIR}{SERIE_A}'}

# PRODUCTION REFERENCES

MODEL_PATH = {SERIE_A: f'{PRODUCTION_DIR}{SERIE_A}/{PRODUCION_SERIA_A}/{PRODUCION_SERIA_A}.pth',
              PREMIER: f'{PRODUCTION_DIR}{PREMIER}/{PRODUCTION_PREMIER}/{PRODUCTION_PREMIER}.pth',
              # JUPILIER: f'{PRODUCTION_DIR}{JUPILIER_MODEL_NAME}/{JUPILIER_MODEL_NAME}.pth'
              }

LEAGUE_PARAMS = {SERIE_A: f'{PRODUCTION_DIR}{SERIE_A}/{PRODUCION_SERIA_A}/1.league_params.json',
                 PREMIER: f'{PRODUCTION_DIR}{PREMIER}/{PRODUCTION_PREMIER}/1.league_params.json',
                 # JUPILIER: f'{PRODUCTION_DIR}{JUPILIER_MODEL_NAME}/1.league_params.json'
                 }

DATA_PARAMS = {SERIE_A: f'{PRODUCTION_DIR}{SERIE_A}/{PRODUCION_SERIA_A}/2.data_params.json',
               PREMIER: f'{PRODUCTION_DIR}{PREMIER}/{PRODUCTION_PREMIER}/2.data_params.json',
               # JUPILIER: f'{PRODUCTION_DIR}{JUPILIER_MODEL_NAME}/2.data_params.json'
               }

MODEL_PARAMS = {SERIE_A: f'{PRODUCTION_DIR}{SERIE_A}/{PRODUCION_SERIA_A}/3.model_params.json',
               PREMIER: f'{PRODUCTION_DIR}{PREMIER}/{PRODUCTION_PREMIER}/2.data_params.json',
               # JUPILIER: f'{PRODUCTION_DIR}{JUPILIER_MODEL_NAME}/2.data_params.json'
                }

FEAT_ENG = {SERIE_A: f'{PRODUCTION_DIR}{SERIE_A}/{PRODUCION_SERIA_A}/feat_eng',
            PREMIER: f'{PRODUCTION_DIR}{PREMIER}/{PRODUCTION_PREMIER}/feat_eng',
            # JUPILIER: f'{PRODUCTION_DIR}{PREMIER_MODEL_NAME}/feat_eng_object'
            }

