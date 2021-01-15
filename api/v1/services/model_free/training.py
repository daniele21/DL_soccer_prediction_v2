from flask import make_response, request
from flask import current_app as app

from api.v1.snippets import training_snippet
from core.str2bool import str2bool
from scripts.constants.configs import HOME, AWAY, DEFAULT_EVAL_SIZE
from scripts.data.data_process import extract_data_league, generate_dataset
from scripts.data.dataset_utils import get_split_size
from scripts.models.evaluation import thr_analysis
from scripts.models.model_inference import real_case_inference
from scripts.models.model_init import model_directory, init_model
from scripts.models.strategy import strategy_stats
from scripts.networks.network_utils import init_network
from scripts.utils.checker import check_training_args, check_training_params, check_data_params, \
    check_simulation_params, check_dataset_params
from scripts.utils.paths import init_env_paths
from scripts.utils.saving import save_all_params, save_model_paths_production

from core.logger.logging import logger


@app.route('/api/v1/training', methods=['POST'])
def training():
    """
    Requested Args:
        - epochs
        - patience

    Requested Params: dict{'league': LEAGUE_PARAMS,
                           'data': DATA_PARAMS,
                           'model': MODEL_PARAMS
                           'production': PRODUCTION_PARAMS}

        LEAGUE_PARAMS: dict{}
        DATA_PARAMS: dict{}
        MODEL_PARAMS: dict{}
        PRODUCTION_PARAMS: dict{'active': bool
                                'phase': eval / final,
                                'stop_loss': float}


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
        production_params = params.get('production')

        model_params = {**model_params, **production_params} if production_params is not None else model_params
        data_params = {**data_params, **production_params} if production_params is not None else data_params

        epochs, patience = args['epochs'], args['patience']

        init_env_paths(model_params['version'])

        model_name, model_dir = model_directory(league_params, data_params, model_params)
        model_params['name'] = model_name
        model_params['save_dir'] = model_dir
        data_params['save_dir'] = model_dir

        # SAVING PARAMS
        save_all_params(model_dir, league_params, data_params, model_params, production_params)

        try:
            # EXTRACTION DATA LEAGUE
            params = {**league_params, **data_params}
            params = check_data_params(params)
            league_csv, input_data = extract_data_league(params)

            league_name = params['league_name']
            npm = params['n_prev_match']
            test_size = params['test_size']
            eval_size = data_params['eval_size'] if 'eval_size' in list(data_params.keys()) else DEFAULT_EVAL_SIZE

            if (data_params['split_size'] == 0):
                data_params['split_size'] = get_split_size(league_name, npm, eval_size, test_size)

            # DATALOADER GENERATION
            dataset_params = check_dataset_params(data_params)
            dataloader, feat_eng, in_features = generate_dataset(input_data,
                                                                 dataset_params)

            # NETWORK INITIALIZATION
            network = init_network(in_features, model_params)

            Model = init_model(data_params['dataset'])
            soccer_model = Model(network, model_params, dataloader)

            soccer_model.train(epochs, patience)

            losses, mean_loss = soccer_model.get_losses()

            json_response = {'model_dir': model_dir,
                             'model_name': model_name,
                             'epochs': soccer_model.epoch,
                             'losses': losses,
                             'mean_loss': mean_loss
                             }

            params = {**league_params, **data_params}

            # if(str2bool(model_params.get('production'))):
            #     soccer_model = production_training(dataset_params, model_params)

            if(params['test_size'] > 0):

                for field in [HOME, AWAY]:
                    params['field'] = field

                    testset, pred, true = real_case_inference(soccer_model, params, feat_eng)
                    thr_result, thr_dict, _ = thr_analysis(true, pred, params)
                    json_response = {**json_response, **thr_dict}

                    simulation_params = check_simulation_params(params)
                    result_df = strategy_stats(testset, pred, true, simulation_params)

        # except Exception as error:
        #
        #     response = make_response({'msg': f'General Error: {error}'}, 400)
        #     return response

            if(str2bool(model_params['production'])):
                save_model_paths_production(league_name, model_dir, model_name)

        except KeyboardInterrupt:
            return make_response({'Interrupt':'Keyboard Interrupt'})

        response = make_response(json_response, 200)

    return response

@app.route('/api/v1/multi-training', methods=['POST'])
def multiple_training():
    """
    Requested Args:
        - epochs
        - patience

    Requested Params: dict{'league': LEAGUE_PARAMS,
                           'data': DATA_PARAMS,
                           'model': MODEL_PARAMS
                           'production': PRODUCTION_PARAMS,
                           'multi_training': MULTI_TRAINING_PARAMS}

        LEAGUE_PARAMS: dict{}
        DATA_PARAMS: dict{}
        MODEL_PARAMS: dict{}

        PRODUCTION_PARAMS: dict{'production': bool,
                                'stop_loss': float}

        MULTI_TRAINING_PARAMS: dict{'param': str,
                                    'values': list}



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
        production_params = params.get('production')

        model_params = {**model_params, **production_params} if production_params is not None else model_params
        data_params = {**data_params, **production_params} if production_params is not None else data_params

        epochs, patience = args['epochs'], args['patience']

        # MULTI TRAINING SETUP
        multi_training_params = params['multi_training']
        param_name = multi_training_params['param']
        param_values = multi_training_params['values']

        for value in param_values:
            if(param_name in data_params.keys()):
                data_params[param_name] = value
            elif(param_name in model_params.keys()):
                model_params[param_name] = value
            else:
                raise ValueError(f'Multi-Training: Wrong param name >> {param_name} <<')

            logger.info(f'\n>>> Multi training on {param_name.upper()}: {value} \n')
            response = {param_name:{}}
            init_env_paths(model_params['version'])

            model_name, model_dir = model_directory(league_params, data_params, model_params)
            model_params['name'] = model_name
            model_params['save_dir'] = model_dir
            data_params['save_dir'] = model_dir

            # SAVING PARAMS
            save_all_params(model_dir, league_params, data_params, model_params, production_params)

            try:
                # EXTRACTION DATA LEAGUE
                params = {**league_params, **data_params}
                params = check_data_params(params)
                league_csv, input_data = extract_data_league(params)

                # DATALOADER GENERATION
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
                                 'losses': losses,
                                 'mean_loss': mean_loss
                                 }

                params = {**league_params, **data_params}

                # if(str2bool(model_params.get('production'))):
                #     soccer_model = production_training(dataset_params, model_params)

                if(params['test_size'] > 0):

                    for field in [HOME, AWAY]:
                        params['field'] = field

                        testset, pred, true = real_case_inference(soccer_model, params, feat_eng)
                        thr_result, thr_dict, _ = thr_analysis(true, pred, params)
                        json_response = {**model_response, **thr_dict}

                        simulation_params = check_simulation_params(params)
                        result_df = strategy_stats(testset, pred, true, simulation_params)

            except Exception as error:

                response = make_response({'msg': f'General Error: {error}'}, 400)
                return response

            except KeyboardInterrupt:
                return make_response({'Interrupt':'Keyboard Interrupt'})

            response[param_name][str(value)] = model_response

    return make_response(response, 200)

@app.route('/api/v1/training/production', methods=['POST'])
def production_training():
    """
    Requested Args:
        - epochs
        - patience

    Requested Params: dict{'league': LEAGUE_PARAMS,
                           'data': DATA_PARAMS,
                           'model': MODEL_PARAMS
                           'production': PRODUCTION_PARAMS}

        LEAGUE_PARAMS: dict {
                                "league_name": "serie_a",
                                "n_prev_match": int,
                                "league_dir": DATA_DIR,
                                "train": bool
                            }

        DATA_PARAMS: dict{
                            "normalize": bool,
                            "window_size": int,
                            "dataset": ["base" | "windowed"],
                            "batch_size": int,
                            "split_size": float,
                            "test_size": int,
                            "version": [1 | 2],
                            "league_dir": DATA_DIR,
                            "train": bool
                        }

        MODEL_PARAMS: dict{
                            "dataset": ["base" | "windowed"],
                            "version": [1 | 2],
                            "out_lstm": int,
                            "n_lstm_layer": int,
                            "bidirectional": bool,
                            "kernel": int,
                            "padding": int,
                            "conv_layers": int,
                            "optimizer": "adam",
                            "lr": float,
                            "loss": "bce",
                            "seed": int,
                            "device": "gpu",
                            "verbose": bool,
                            "plot": bool,
                            "static_dir": STATIC_DIR
                        }

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
        return make_response(msg, 400)

    else:
        epochs, patience = args['epochs'], args['patience']
        league_name = params['league']['league_name']
        logger.info(f'> Training {league_name.upper()}\n')

        # TRAINING FOR CATCHING OPTIMAL TRAIN LOSS
        params['data']['test_size'] = 0
        params['data']['split_size'] = 0
        print(f'\n\n>>> Params: \n{params}\n\n')
        model_response = training_snippet(epochs, patience, params, production=True)
        print(model_response)

        optimal_train_loss = model_response['losses']['train'] if model_response['mean_loss'] is None else \
                             model_response['mean_loss']['train']


        # TRAINING FOR PRODUCTION SETTINGS
        params['data']['split_size'] = 1
        params['model']['stop_loss'] = optimal_train_loss
        print(f'\n\n>>> Params: \n{params}\n\n')
        model_response = training_snippet(epochs, patience, params, production=True)

        model_dir, model_name = model_response['model_dir'], model_response['model_name']
        save_model_paths_production(league_name, model_dir, model_name)

        return make_response(model_response, 200)
