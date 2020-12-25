from json import JSONDecodeError

from api.v1.utils import load_models, load_model_and_config
from scripts.constants.paths import STATIC_DIR
from scripts.models.evaluation import evaluate_results, thr_analysis
from scripts.utils.checker import check_league, check_predict_paths
from scripts.data.preprocessing import fill_inference_matches
from scripts.models.model_inference import generate_test_data, model_inference, generate_output, real_case_inference

from flask import current_app as app
from flask import make_response, jsonify, request

from scripts.utils.loading import load_configs_from_paths
# from . import configs, models
models, configs = None, None

@app.route('/api/v1/predict/<league_name>', methods=['POST'])
def predict(league_name):
    """

    Args:
        league_name: str

    Requested Params: dict{'thr',
                           'round',
                           'home',
                           'away',
                           '1X_odds',
                           'X2_odds'}

    Returns:
        prediction: dict{'match',
                         '1X',
                         'pred_1X',
                         'X2',
                         'pred_X2'}
    """

    outcome, msg = check_league(league_name)
    if not outcome:
        response = make_response(msg, 404)

    else:
        matches = request.json
        thr = matches['thr'] if 'thr' in list(matches.keys()) else None

        model, config = models[league_name], configs[league_name]

        league_params = config['league']
        feat_eng = config['feat_eng']

        test_data = generate_test_data(league_params)

        matches_df = fill_inference_matches(test_data, matches)

        predictions = {}
        for field in ['home', 'away']:
            pred, _ = model_inference(matches_df[field],
                                      feat_eng,
                                      model,
                                      model_name=field,
                                      train=False)
            predictions[field] = pred

        outcome_dict = generate_output(matches_df, predictions, thr)

        response = make_response(jsonify(outcome_dict), 200)

    return response

@app.route('/api/v1/predict/path', methods=['POST'])
def predict_from_path():
    """
    Requested Params: dict{'model_dir',
                           'model_name',
                           'thr',
                           'round',
                           'home',
                           'away',
                           '1X_odds',
                           'X2_odds'}

    Returns:
        prediction: dict{'match',
                         '1X',
                         'pred_1X',
                         'X2',
                         'pred_X2'}

    """
    path_dict = request.json

    model_dir = path_dict['model_dir']
    model_name = path_dict['model_name']

    response = check_predict_paths(model_dir, model_name)

    if not response['check']:
        response = make_response(response['msg'], 400)

    else:
        paths = response['paths']

        try:
            config, model = load_configs_from_paths(paths)

        except FileNotFoundError as error:
            msg = f'File not found: {error}'
            response = {'check':False,
                        'msg':msg}

            return response

        except JSONDecodeError as error:
            msg = f'Json decoder error: {error}'
            response = {'check': False,
                        'msg': msg}

            return response

        # PREDICTION PROCESS
        matches = request.json
        thr = matches['thr'] if 'thr' in list(matches.keys()) else None

        league_params = config['league']
        feat_eng = config['feat_eng']

        test_data = generate_test_data(league_params)

        matches_df = fill_inference_matches(test_data, matches)

        predictions = {}
        for field in ['home', 'away']:
            pred, _ = model_inference(matches_df[field],
                                      feat_eng,
                                      model,
                                      model_name=field,
                                      train=False)
            predictions[field] = pred

        outcome_dict = generate_output(matches_df, predictions, thr)

        response = make_response(jsonify(outcome_dict), 200)

        return response

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

