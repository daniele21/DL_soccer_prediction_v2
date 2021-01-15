
from api.v1.utils import load_models, load_model_and_config
from scripts.constants.configs import HOME, AWAY
from scripts.constants.paths import STATIC_DIR
from scripts.constants.predict import PREDICT_CONFIG, LOW_RISK
from scripts.data.postprocessing import postprocessing_test_data
from scripts.models.evaluation import evaluate_results, thr_analysis
from scripts.models.strategy import strategy_stats
from scripts.utils.checker import check_league, check_predict_paths, check_evaluation_params, check_simulation_params
from scripts.data.preprocessing import fill_inference_matches
from scripts.models.model_inference import generate_test_data, model_inference, generate_output, real_case_inference

from flask import current_app as app
from flask import make_response, jsonify, request

from scripts.utils.loading import load_configs_from_paths
from . import configs, models
# models, configs = None, None



@app.route('/api/v1/process/predict/', methods=['POST'])
def predict():
    """

    Requested Params: dict{'league_name':  str <OPTION_1>,
                            'model_dir':   str <OPTION_2>,
                            'model_name':  str <OPTION_2>,
                            'thr',
                            'round',
                            'home_teams',
                            'away_teams',
                            '1X_odds',
                            'X2_odds'}

    Returns:
        prediction: dict{'match',
                         '1X',
                         'pred_1X',
                         'X2',
                         'pred_X2'}
    """

    params = request.json

    response, model, config = load_model_and_config(params, models, configs)

    if (not response['check']):
        return make_response(response['msg'], 401)

    league_params = config['league']
    data_params = config['data']
    feat_eng = config['feat_eng']

    league_name = params['league_name'] if 'league_name' in params.keys() else league_params['league_name']

    params = {**params, **league_params, **data_params}

    thr_fields = params['thr'] if 'thr' in list(params.keys()) else None

    matches = {'home_teams': params['home_teams'],
               'away_teams': params['away_teams'],
               '1X_odds': params['1X_odds'],
               'X2_odds': params['X2_odds']
               }

    test_data = generate_test_data(params)

    matches_df = fill_inference_matches(test_data, matches)

    predictions = {}
    for field in [HOME, AWAY]:
        # predict_config = PREDICT_CONFIG[league_name][LOW_RISK][field]
        thr = thr_fields[field] if thr_fields is not None else None
        # filter_bet = predict_config['filter_bet']

        pred, _ = model_inference(matches_df[field],
                                  feat_eng,
                                  model,
                                  model_name=field,
                                  train=False)
        predictions[field] = pred

    outcome_dict = generate_output(matches_df, predictions, thr)

    response = make_response(jsonify(outcome_dict), 200)

    return response
#
# @app.route('/api/v1/predict/path', methods=['POST'])
# def predict_from_path():
#     """
#     Requested Params: dict{'model_dir',
#                            'model_name',
#                            'thr',
#                            'round',
#                            'home',
#                            'away',
#                            '1X_odds',
#                            'X2_odds'}
#
#     Returns:
#         prediction: dict{'match',
#                          '1X',
#                          'pred_1X',
#                          'X2',
#                          'pred_X2'}
#
#     """
#     path_dict = request.json
#
#     model_dir = path_dict['model_dir']
#     model_name = path_dict['model_name']
#
#     response = check_predict_paths(model_dir, model_name)
#
#     if not response['check']:
#         response = make_response(response['msg'], 400)
#
#     else:
#         paths = response['paths']
#
#         try:
#             config, model = load_configs_from_paths(paths)
#
#         except FileNotFoundError as error:
#             msg = f'File not found: {error}'
#             response = {'check':False,
#                         'msg':msg}
#
#             return response
#
#         except JSONDecodeError as error:
#             msg = f'Json decoder error: {error}'
#             response = {'check': False,
#                         'msg': msg}
#
#             return response
#
#         # PREDICTION PROCESS
#         matches = request.json
#         thr = matches['thr'] if 'thr' in list(matches.keys()) else None
#
#         league_params = config['league']
#         feat_eng = config['feat_eng']
#
#         test_data = generate_test_data(league_params)
#
#         matches_df = fill_inference_matches(test_data, matches)
#
#         predictions = {}
#         for field in ['home', 'away']:
#             pred, _ = model_inference(matches_df[field],
#                                       feat_eng,
#                                       model,
#                                       model_name=field,
#                                       train=False)
#             predictions[field] = pred
#
#         outcome_dict = generate_output(matches_df, predictions, thr)
#
#         response = make_response(jsonify(outcome_dict), 200)
#
#         return response

@app.route('/api/v1/process/thr_analysis', methods=['POST'])
def process_thr_analysis():
    """

    Requested body:

        params :    dict{   'league_name':  str <OPTION_1>,
                            'model_dir':    str <OPTION_2>,
                            'model_name':   str <OPTION_2>,
                            'field':        str
                            'thr_list':     list <float> (OPTIONAL)


    Returns:
        thr_analysis: dict{ }

    """


    params = request.json

    response, model, config = load_model_and_config(params, models, configs)

    if(not response['check']):
        return make_response(response['msg'], 401)

    league_params = config['league']
    data_params = config['data']
    feat_eng = config['feat_eng']

    params = {**params, **league_params, **data_params}
    # params['save_dir'] = model_dir

    testset, pred, true = real_case_inference(model, params, feat_eng)
    thr_result, thr_dict, _ = thr_analysis(true, pred, params)

    response = make_response(jsonify(thr_dict), 200)

    return response

@app.route('/api/v1/process/strategy', methods=['POST'])
def strategy_analysis():
    """

    Requested Params: dict {'league_name': OPTIONAL 1
                            'model_dir': OPTIONAL 2
                            'model_name': OPTIONAL 2,

                            'thr_list': OPTIONAL,
                            'filter_bet_list': OPTIONAL,
                            'money_bet': OPTIONAL,
                            'combo_list':OPTIONAL,
                            'n_matches':OPTIONAL


    Returns:

    """

    params = request.json

    response, model, config = load_model_and_config(params, models, configs)

    if not response['check']:
        return make_response(response['msg'], 400)

    league_params = config['league']
    data_params = config['data']
    feat_eng = config['feat_eng']

    params = {**params, **league_params, **data_params}
    # params['save_dir'] = STATIC_DIR

    for field in [HOME, AWAY]:
        params['field'] = field
        testset, pred, true = real_case_inference(model, params, feat_eng)

        eval_params = check_evaluation_params(params)
        pred_df, _, _ = evaluate_results(true, pred, eval_params, plot=False)

        simulation_params = check_simulation_params(params)
        result_df, ckp_df = strategy_stats(testset, pred, true, simulation_params)

    response = make_response(f'Strategy stats saved at {params["save_dir"]}', 200)

    return response
