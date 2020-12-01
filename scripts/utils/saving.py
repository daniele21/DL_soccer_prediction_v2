from core.file_manager.saving import save_json, save_str_file, save_model
from core.logger.logging import logger
from core.file_manager.os_utils import ensure_folder


def _json_item_to_str(json_params):

    json_str = {}

    for k in json_params:
        json_str[k] = str(json_params[k])

    return json_str


def save_simulation_details(field, string, folder_dir):
    filename = f'5.simulations_details_{field}.txt'
    # filepath = f'{os.environ["CKP_MODEL_PATH"]}{os.environ["MODEL_NAME"]}/{filename}'
    filepath = f'{folder_dir}/{filename}'

    content = f'\n\n> Simulation \n'
    content += string

    logger.info(f' > Saving training details at {filepath}')
    with open(filepath, 'a') as f:
        f.write(content)
        f.close()

    return

def save_params(params, filepath, format='json'):

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

    logger.info(f' > Saving params at {filepath}\n')

    return


def save_all_params(save_dir, league_params,
                    data_params, model_params):
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

    logger.info(f'> Saving PARAMS at {save_dir}')

    return


def save_soccer_model(model):
    # folder = f'{model.save_dir}{model.name}/'
    filename = f'{model.name}.pth'
    folder = model.save_dir
    filepath = f'{folder}{filename}'

    ensure_folder(folder)
    save_model(model, filepath)

    logger.info(f'> Saving checkpoint epoch {model.epoch} at {folder}')

    return filepath


def save_training_details(model):
    filename = '4.training_details'
    filepath = f'{model.save_dir}/{filename}'

    training_details = {'epoch': model.epoch,
                        'train_loss': model.losses['train'][-1],
                        'eval_loss': model.losses['eval'][-1]
                        }

    save_params(training_details, filepath, format='json')

    logger.info(f' > Saving training details at {filepath}')

    return

