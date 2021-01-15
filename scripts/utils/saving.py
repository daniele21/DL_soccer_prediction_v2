from core.file_manager.loading import load_json
from core.file_manager.saving import save_json, save_str_file, save_model
from core.logger.logging import logger
from core.file_manager.os_utils import ensure_folder
from scripts.constants.paths import PRODUCTION_DIR
from scripts.utils.loading import load_production_paths


def _json_item_to_str(json_params):

    json_str = {}

    for k in json_params:
        json_str[k] = str(json_params[k])

    return json_str


def save_simulation_details(sim_result, params, folder_dir):
    field = params['field']
    thr = params['thr']
    filter_bet = params['filter_bet']

    # filename = f'5.simulations_details_{field}.txt'
    filename = f'5.simulations_details_{field}_thr={thr}_filter={filter_bet}.json'
    filepath = f'{folder_dir}{filename}'

    if(params['verbose']):
        logger.info(f' > Saving training details at {filepath}')

    save_json(sim_result, filepath)

    return

def save_params(params, filepath, format='json', verbose=True):

    if(format=='json'):
        filepath += '.json'
        params = _json_item_to_str(params)

        save_json(params, filepath)


    elif(format == 'str'):

        str_params = str(params).replace(',' ,',\n')

        filename = filepath.split('/')[-1]
        content = f'\n> {filename}\n\n'
        content += str_params

        filepath += '.txt'

        save_str_file(content, filepath)

    else:
        raise ValueError(f'Format is not recognized: provided --> {format}')

    if verbose:
        logger.info(f' > Saving params at {filepath}\n')

    return


def save_all_params(save_dir, league_params,
                    data_params, model_params, production_params=None):
    ensure_folder(save_dir)

    filename = '1.league_params'
    filepath = f'{save_dir}{filename}'
    save_params(league_params, filepath, format='json')

    filename = '2.data_params'
    filepath = f'{save_dir}{filename}'
    save_params(data_params, filepath, format='json')

    filename = '3.model_params'
    filepath = f'{save_dir}{filename}'
    save_params(model_params, filepath, format='json')

    if(production_params is not None):
        filename = '4.production_params'
        filepath = f'{save_dir}{filename}'
        save_params(model_params, filepath, format='json')

    logger.info(f'> Saving PARAMS at {save_dir}')

    return


def save_soccer_model(model):
    # folder = f'{model.save_dir}{model.name}/'
    filename = f'{model.name}.pth'
    folder = model.save_dir
    filepath = f'{folder}{filename}'

    ensure_folder(folder)
    save_model(model, filepath)

    if(model.verbose):
        logger.info(f'> Saving checkpoint epoch {model.epoch} at {folder}')

    return filepath


def save_training_details(model, save_dir, filename=None):
    filename = '4.training_details' if filename is None else filename
    ensure_folder(save_dir)
    filepath = f'{save_dir}/{filename}'

    training_details = {'epoch': model.epoch,
                        'train_loss': model.losses['train'][-1],
                        'eval_loss': model.losses['eval'][-1]
                        }

    save_params(training_details, filepath, format='json', verbose= model.verbose)

    # logger.info(f' > Saving training details at {filepath}')

    return training_details

def save_simulation(simulation_df, params, folder_dir):

    field = params['field']
    thr = params['thr']
    filter_bet = params['filter_bet']

    filename = f'simulations_details_{field.upper()}_thr={thr}_filter={filter_bet}.csv'
    folder_path = f'{folder_dir}simulations/'
    ensure_folder(folder_path)
    filepath = f'{folder_path}{filename}'

    if (params['verbose']):
        logger.info(f' > Saving training details at {filepath}')

    simulation_df.to_csv(filepath, sep=';', decimal=',')

    return


def save_model_paths_production(league_name, model_dir, model_name):
    production_paths = load_production_paths()

    league_params_path = f'{model_dir}1.league_params.json'
    data_params_path = f'{model_dir}2.data_params.json'
    model_params_path = f'{model_dir}3.model_params.json'
    model_path = f'{model_dir}{model_name}.pth'
    feat_eng_path = f'{model_dir}feat_eng'


    production_paths[league_name] = {'model_params': model_params_path,
                                     'league_params': league_params_path,
                                     'data_params': data_params_path,
                                     'model_path': model_path,
                                     'feat_eng': feat_eng_path}

    save_path = f'{PRODUCTION_DIR}production_paths.json'
    save_json(production_paths, save_path)

    logger.info('---------------------------------------------------------')
    logger.info(f'\n\nUpdating production paths: {league_name.upper()}\n')
    logger.info(f'New Path : {model_dir}')
    logger.info('---------------------------------------------------------')