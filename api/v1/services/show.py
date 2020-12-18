from flask import make_response, request

from scripts.constants.paths import STATIC_DIR
from scripts.utils.checker import check_league
from api.v1.utils import show_plot
from scripts.data.postprocessing import postprocessing_test_data
from scripts.models.evaluation import evaluate_results, thr_analysis
from scripts.models.model_inference import real_case_inference
from scripts.models.strategy import simulation
from scripts.visualization.summary import show_summary

from flask import current_app as app
from . import models, configs


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

@app.route('/api/v1/show/<league_name>/thr_analysis', methods=['POST'])
def show_evaluation_thr(league_name):

    # requested params : [thr, field, thr_list]
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

        testset, pred, true = real_case_inference(league_name, model, params, feat_eng)
        pred_df, outcome, _ = evaluate_results(true, pred, params, plot=False)
        analysis_df = thr_analysis(true, pred, params)

        response = make_response(analysis_df.transpose().to_dict(), 200)

    return response


@app.route('/api/v1/show/<league_name>/simulation', methods=['POST'])
def show_simulation(league_name):

    # requested params : [thr, thr_list, field, filter_bet, money_bet, n_matches, combo]

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

        pred_df, _ = evaluate_results(true, pred, params, plot=False)
        analysis_df = thr_analysis(true, pred, params)
        data_result = postprocessing_test_data(testset, pred_df)
        summary, sim_result, fig = simulation(data_result, params, plot=False)

        show_summary(summary)

        response = show_plot(fig)

    return response
