from flask import make_response, request
from flask import current_app as app

from scripts.constants.configs import HOME, AWAY
from scripts.data.data_process import extract_data_league, generate_dataset
from scripts.models.evaluation import thr_analysis
from scripts.models.model_inference import real_case_inference
from scripts.models.model_init import model_directory, init_model
from scripts.models.strategy import strategy_stats
from scripts.networks.network_utils import init_network
from scripts.utils.checker import check_training_args, check_training_params
from scripts.utils.paths import init_env_paths
from scripts.utils.saving import save_all_params

from core.logger.logging import logger


@app.route('/api/v1/training', methods=['POST'])
def training():
    """
    Requested Args:
        - epochs
        - patience

    Requested Params: dict{'league': LEAGUE_PARAMS,
                           'data': DATA_PARAMS,
                           'model': MODEL_PARAMS}

        LEAGUE_PARAMS: dict{}
        DATA_PARAMS: dict{}
        MODEL_PARAMS: dict{}

    Returns:
        json_response: dict{'model_dir': str,
                            'model_name': str,
                            'losses': list,
                            'mean loss': float
                             }
    """

    params = request.json
    args = request.args

    check_args = check_training_args(args)
    check_params = check_training_params(params)

    if (not check_args['check'] or not check_args['check']):
        msg = f'> Args: {check_args["msg"]} \n> Params: {check_params["msg"]}'
        logger.error(msg)
        response = make_response(msg, 400)

    else:
        league_params, data_params, model_params = params['league'], params['data'], params['model']
        epochs, patience = args['epochs'], args['patience']

        init_env_paths(model_params['version'])

        model_name, model_dir = model_directory(league_params, data_params, model_params)
        model_params['name'] = model_name
        model_params['save_dir'] = model_dir
        data_params['save_dir'] = model_dir

        # SAVING PARAMS
        save_all_params(model_dir, league_params, data_params, model_params)

        try:
            # EXTRACTION DATA LEAGUE
            league_csv, input_data = extract_data_league(league_params)

            # DATALOADER GENERATION
            dataloader, feat_eng, in_features = generate_dataset(input_data,
                                                                 data_params)

            # NETWORK INITIALIZATION
            network = init_network(in_features, model_params)

            Model = init_model(data_params['dataset'])
            soccer_model = Model(network, model_params, dataloader)

            soccer_model.train(epochs, patience)

            losses, mean_loss = soccer_model.get_losses()

            json_response = {'model_dir': model_dir,
                             'model_name': model_name,
                             'losses': losses,
                             'mean loss': mean_loss
                             }

            params = {**league_params, **data_params}
            for field in [HOME, AWAY]:
                params['field'] = field

                testset, pred, true = real_case_inference(soccer_model, params, feat_eng)
                thr_result, thr_dict, _ = thr_analysis(true, pred, params)
                json_response[field] = thr_dict

                result_home_df = strategy_stats(testset, pred, true, params)
                result_away_df = strategy_stats(testset, pred, true, params)

        except Exception as error:

            response = make_response({'msg': f'General Error: {error}'}, 400)
            return response

        except KeyboardInterrupt:
            return make_response({'Interrupt':'Keyboard Interrupt'})

        response = make_response(json_response, 200)

    return response