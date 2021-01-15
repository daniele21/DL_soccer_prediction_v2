from flask import make_response

from scripts.data.data_process import extract_data_league, generate_dataset
from scripts.data.dataset_utils import get_split_size
from scripts.models.model_init import model_directory, init_model
from scripts.networks.network_utils import init_network
from scripts.utils.checker import check_data_params, check_dataset_params, DEFAULT_EVAL_SIZE, HOME
from scripts.utils.paths import init_env_paths
from scripts.utils.saving import save_all_params


def training_snippet(epochs, patience, params, production=False):
    league_params, data_params, model_params = params['league'], params['data'], params['model']
    data_params['production'] = production
    model_params['production'] = production

    init_env_paths(model_params['version'])

    model_name, model_dir = model_directory(league_params, data_params, model_params,
                                            production)
    model_params['name'] = model_name
    model_params['save_dir'] = model_dir
    data_params['save_dir'] = model_dir

    # SAVING PARAMS
    save_all_params(model_dir, league_params, data_params, model_params)

    # TRAINING FOR CATCHING OPTIMAL TRAIN LOSS
    try:
        # EXTRACTION DATA LEAGUE
        params = {**league_params, **data_params}
        params = check_data_params(params)
        league_csv, input_data = extract_data_league(params)

        # DATALOADER GENERATION
        league_name = params['league_name']
        npm = params['n_prev_match']
        test_size = params['test_size']
        eval_size = data_params['eval_size'] if 'eval_size' in list(data_params.keys()) else DEFAULT_EVAL_SIZE

        if(data_params['split_size'] == 0):
            data_params['split_size'] = get_split_size(league_name, npm, eval_size, test_size)

        dataset_params = check_dataset_params(data_params)
        dataloader, feat_eng, in_features = generate_dataset(input_data,
                                                             dataset_params)

        # NETWORK INITIALIZATION
        network = init_network(in_features, model_params)

        Model = init_model(data_params['dataset'])
        soccer_model = Model(network, model_params, dataloader)

        soccer_model.train(epochs, patience)

        losses, mean_loss = soccer_model.get_losses()

        model_response = {'model_dir': model_dir,
                          'model_name': model_name,
                          'epoch': soccer_model.epoch,
                          'losses': losses,
                          'mean_loss': mean_loss
                         }

    # except Exception as error:
    #     response = make_response({'msg': f'General Error: {error}'}, 400)
    #     print(error)
    #     return response

    except KeyboardInterrupt:
        return

    return model_response

