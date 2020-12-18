from flask import Flask, make_response, jsonify, request, render_template

from scripts.utils.checker import check_league, check_data_league
from api.v1.utils import show_plot
import scripts.data.constants as K
from core.logger.logging import logger

from scripts.data.data_process import update_data_league
from scripts.data.postprocessing import postprocessing_test_data
from scripts.data.preprocessing import fill_inference_matches
from scripts.models.evaluation import evaluate_results, thr_analysis
from scripts.models.model_inference import generate_test_data, model_inference, generate_output

# from scripts.utils.loading import load_configs
from scripts.models.strategy import simulation
from scripts.visualization.summary import show_summary

from flask import current_app as app


@app.route('/api/v1/predict/<league_name>', methods=['POST'])
def predict(league_name):
    print(league_name)

    outcome, msg = check_league(league_name)
    if not outcome:
        response = make_response(msg, 404)

    else:
        matches = request.json
        thr = matches['thr'] if 'thr' in list(matches.keys()) else None

        # CALL THE MODEL FOR PREDICTION
        # model, config = models[league_name], configs[league_name]

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

