DEFAULT_THR_LIST = [0.5, 0.55, 0.6, 0.65, 0.7, 0.725, 0.75, 0.775, 0.8, 0.825, 0.85, 0.875, 0.9]
DEFAULT_FILTER_BET_LIST = [1.05, 1.1, 1.15, 1.2]
DEFAULT_COMBO_LIST = [2,3,4,5,6,7]
DEFAULT_FILTER_BET = 1.15
DEFAULT_MONEY_BET = 1
DEFAULT_TEST_SIZE = 200
DEFAULT_EVAL_SIZE = 50
DEFAULT_UPDATE = False
DEFAULT_THR = None
DEFAULT_SAVE_DIR = None
DEFAULT_VERBOSE = True
DEFAULT_CKP_BOUNDS = [(20,30), (30,40), (40,50),
                      (50,60), (60,70), (70,80)]

# DATASET
WINDOWED_DATASET = 'windowed'
BASE_DATASET = 'base'

# NETWORK
NETWORK_V1 = 'network_v1'
NETWORK_V2 = 'network_v2'

# FIELD
HOME = 'home'
AWAY = 'away'

# OPTIMIZER
ADAM_OPTIMIZER = 'adam'

# LOSS
BCE_LOSS = 'bce'

# DEVICE
CUDA_DEVICE = 'gpu'
CPU_DEVICE = 'cpu'

#
LEAGUE_NAME_LABEL = 'league_name'
N_PREV_MATCH_LABEL = 'n_prev_match'
VERSION_LABEL = 'version'
UPDATE_LABEL = 'update'
TRAIN_LABEL = 'train'
TEST_SIZE_LABEL = 'test_size'
LEAGUE_DIR_LABEL = 'league_dir'
THR_LABEL = 'thr'
THR_LIST_LABEL = 'thr_list'
FIELD_LABEL = 'field'
SAVE_DIR_LABEL = 'save_dir'
N_MATCHES_LABEL = 'n_matches'
COMBO_LABEL = 'combo'
COMBO_LIST_LABEL = 'combo_list'
FILTER_BET_LABEL = 'filter_bet'
FILTER_BET_LIST_LABEL = 'filter_bet_list'
MONEY_BET_LABEL = 'money_bet'
VERBOSE_LABEL = 'verbose'

# PRODUCTION PHASE
EVAL_PHASE = 'eval'
FINAL_PHASE = 'final'

# API CONFIG
DEFAULT_HOST = 'localhost'
DEFAULT_PORT = 8080

# HOSTS
API_READ = '/api/v1/read/'
API_WRITE = '/api/v1/write/'
API_PROCESS = '/api/v1/process/'

# GUI
ICON_PATH = 'scripts/frontend/resources/icon.png'


