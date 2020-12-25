from flask import make_response, request, render_template

from core.file_manager.saving import save_json, save_str_file
from scripts.constants.configs import HOME, AWAY
from scripts.constants.paths import STATIC_DIR
from scripts.utils.checker import check_league, check_predict_paths
from api.v1.utils import show_plot, load_models, load_model_and_config
from scripts.data.postprocessing import postprocessing_test_data
from scripts.models.evaluation import evaluate_results, thr_analysis
from scripts.models.model_inference import real_case_inference
from scripts.models.strategy import simulation, strategy_stats
from scripts.utils.loading import load_configs_from_paths
from scripts.visualization.summary import show_summary

from flask import current_app as app
# from . import configs, models
models, configs = None, None


@app.route('/api/v1/show/<league_name>/hist', methods=['POST'])
def show_evaluation_hist(league_name):

    # requested params : [thr, field]
    args = request.json
    config = configs[league_name]['league']

    params = {**args, **config}
    params['save_dir'] = STATIC_DIR

    outcome, msg = check_league(league_name)
    if (outcome == False):
        response = make_response(msg, 404)

    else:
        model = models[league_name]
        feat_eng = configs[league_name]['feat_eng']

        testset, pred, true = real_case_inference(model, params, feat_eng)
        pred_df, outcome, fig = evaluate_results(true, pred, params, plot=False)
        response = show_plot(fig)

    return response

@app.route('/api/v1/show/<league_name>/hist/path', methods=['POST'])
def show_evaluation_hist_from_path(league_name):

    # requested params : [thr, field]
    args = request.json
    model_dir = args['model_dir']
    model_name = args['model_name']

    response = check_predict_paths(model_dir, model_name)
    if not response['check']:
        return make_response(response['msg'], 400)

    paths = response['paths']
    config, model = load_configs_from_paths(paths)
    league_params, data_params = config['league'], config['data']

    params = {**args, **league_params, **data_params}
    params['save_dir'] = STATIC_DIR

    outcome, msg = check_league(league_name)
    if (outcome == False):
        response = make_response(msg, 404)

    else:
        # model = models[league_name]
        feat_eng = config['feat_eng']

        testset, pred, true = real_case_inference(model, params, feat_eng)
        pred_df, outcome, fig = evaluate_results(true, pred, params, plot=False)
        response = show_plot(fig)

    return response


# @app.route('/api/v1/show/<league_name>/simulation', methods=['POST'])
# def show_simulation(league_name):
#
#     # requested params : [thr, thr_list, field, filter_bet, money_bet, n_matches, combo]
#
#     args = request.json
#     config = configs[league_name]['league']
#
#     params = {**args, **config}
#     params['save_dir'] = STATIC_DIR
#
#     outcome, msg = check_league(league_name)
#     if (outcome == False):
#         response = make_response(msg, 404)
#
#     else:
#         model = models[league_name]
#         feat_eng = configs[league_name]['feat_eng']
#
#         testset, pred, true = real_case_inference(model, params, feat_eng)
#
#         pred_df, _ = evaluate_results(true, pred, params, plot=False)
#         _, _, _ = thr_analysis(true, pred, params)
#         data_result = postprocessing_test_data(testset, pred_df)
#         summary, sim_result, fig = simulation(data_result, params, plot=False)
#
#         show_summary(summary)
#
#         response = show_plot(fig)
#
#     return response


@app.route('/api/v1/show/<league_name>/simulation', methods=['POST'])
def show_simulation(league_name):

    # requested params : [thr, thr_list, field, filter_bet, money_bet, n_matches, combo]

    params = request.json

    response, model, config = load_model_and_config(params, models, configs)

    if not response['check']:
        return make_response(response['msg'], 400)

    league_params = config['league']
    data_params = config['data']
    feat_eng = config['feat_eng']

    params = {**params, **league_params, **data_params}
    # params['save_dir'] = STATIC_DIR

    testset, pred, true = real_case_inference(model, params, feat_eng)

    pred_df, _, _ = evaluate_results(true, pred, params, plot=False)
    _, _, thr_dict = thr_analysis(true, pred, params)
    thr_outcome = thr_dict[str(params['thr'])]
    data_result = postprocessing_test_data(testset, pred_df)
    summary, sim_result, fig = simulation(data_result, params, thr_outcome, plot=False)

    fig.savefig(f'{STATIC_DIR}simulation.png')
    summary_str = show_summary(summary)
    save_str_file(summary_str, f'{STATIC_DIR}summary', mode='w')
    save_str_file(summary_str, f'{data_params["save_dir"]}summary', mode='w')

    response = show_plot(fig)

    # params['field'] = HOME
    # result_home_df = strategy_stats(testset, pred, true, params)


    # params['field'] = AWAY
    # testset, pred, true = real_case_inference(model, params, feat_eng)
    # result_away_df = strategy_stats(testset, pred, true, params)

    return response

# @app.route('/api/v1/show/<league_name>/strategy', methods=['POST'])
# def strategy_stats(league_name):
