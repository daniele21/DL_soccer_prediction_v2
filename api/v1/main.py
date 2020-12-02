from flask import Flask, make_response, jsonify, request, render_template

from api.v1.checker import check_league
from api.v1.utils import show_plot, load_models
import scripts.data.constants as K

import pandas as pd

from scripts.data.postprocessing import postprocessing_test_data
from scripts.data.preprocessing import fill_inference_matches
from scripts.models.evaluation import evaluate_results, simulation
from scripts.models.model_inference import generate_test_data, model_inference, generate_output

# from scripts.utils.loading import load_configs

app = Flask(__name__, template_folder="templates/")
model, config = load_models('serie_a')


@app.route('/')
def homepage():
    return render_template('index.html')


@app.route('/api/v1/read/league', methods=['GET'])
def get_league_names():
    return make_response(jsonify({'league_name': K.LEAGUE_NAMES}))


@app.route('/api/v1/read/<league_name>/team', methods=['GET'])
def get_teams(league_name):

    outcome, msg = check_league(league_name)
    if not outcome:
        response = make_response(msg, 404)
    else:
        teams = sorted(K.TEAMS_LEAGUE[str(league_name).lower()])
        response = make_response(jsonify({'league': league_name,
                                          'teams': teams}))

    return response


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

@app.route('/api/v1/show/<league_name>/hist', methods=['POST'])
def show_evaluation(league_name):

    params = request.json  # requested params : [thr, field]
    params['save_dir'] = 'api/v1/templates/static/'
    field = params['field']

    outcome, msg = check_league(league_name)
    if (outcome == False):
        response = make_response(msg, 404)

    else:
        testset, pred, true = inference(league_name)
        pred_df, fig = evaluate_results(true, pred, params, plot=False)
        response = show_plot(fig)

    return response

@app.route('/api/v1/show/<league_name>/simulation', methods=['POST'])
def show_simulation(league_name):

    params = request.json  # requested params : [thr, field, filter_bet, money_bet, n_matches, combo]
    params['save_dir'] = 'api/v1/templates/static/'
    field = params['field']

    outcome, msg = check_league(league_name)
    if (outcome == False):
        response = make_response(msg, 404)

    else:
        testset, pred, true = inference(league_name)

        pred_df, _ = evaluate_results(true, pred, params, plot=False)
        data_result = postprocessing_test_data(testset, pred_df)
        summary, sim_result, fig = simulation(data_result, params, plot=False)

        response = show_plot(fig)

    return response

    # return render_template('test.html', note=summary)

def inference(league_name):
    params = request.json  # requested params : [thr, field, filter_bet, money_bet, n_matches, combo]

    field = params['field']

    outcome, msg = check_league(league_name)
    if (outcome == False):
        response = make_response(msg, 404)

    else:
        league_name = str(league_name).lower()
        params['league_name'] = league_name
        # model, configs = load_configs(league_name)
        # model, config = models[league_name], configs[league_name]

        if (model.testloader is not None):
            test_size = len(model.testloader[field])
        else:
            test_size = 100

        test_data = generate_test_data(league_name)

        feat_eng = config['feat_eng']

        testset = test_data[field][-test_size:]
        testset = testset[testset['f-opponent'].isnull() == False]

        pred, true = model_inference(testset,
                                     feat_eng,
                                     model,
                                     model_name=field,
                                     train=True)

        return testset, pred, true

if __name__ == '__main__':
    app.run(host='localhost', port=8080, debug=True)
