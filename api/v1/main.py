from flask import Flask, make_response, jsonify, request, render_template

from api.v1.checker import check_league
from api.v1.utils import show_plot
import scripts.data.constants as K

import pandas as pd

from scripts.data.postprocessing import postprocessing_test_data
from scripts.models.evaluation import evaluate_results, simulation
from scripts.models.model_inference import generate_test_data, model_inference
from scripts.utils.loading import load_configs

app = Flask(__name__, template_folder="templates/")

@app.route('/')
def homepage():
    return render_template('index.html')

@app.route('/api/v1/read/league', methods=['GET'])
def get_league_names():
    return make_response(jsonify({'league_name':K.LEAGUE_NAMES}))


@app.route('/api/v1/read/<league_name>/team', methods=['GET'])
def get_teams(league_name):

    outcome, msg = check_league(league_name)
    if(outcome == False):
        response = make_response(msg, 404)
    else:
        teams = sorted(K.TEAMS_LEAGUE[str(league_name).lower()])
        response = make_response(jsonify({'league':league_name,
                                          'teams':teams}))

    return response


@app.route('/api/v1/predict/<league_name>', methods=['POST'])
def predict(league_name):
    print(league_name)

    outcome, msg = check_league(league_name)
    if(outcome == False):
        response = make_response(msg, 404)

    else:
        matches = request.json

        home_teams, away_teams = matches['home_teams'], matches['away_teams']
        odd_1X, odd_X2 = matches['1X_odds'], matches['X2_odds']
        round = matches['round']

        test_df = pd.DataFrame({'round':round,
                                'home':home_teams,
                                '1X_odd':odd_1X,
                                'away':away_teams,
                                'X2_odd':odd_X2})

        matches_list = [f'{home_teams[i]} - {away_teams[i]}'for i in range(len(home_teams))]

        # CALL THE MODEL FOR PREDICTION
        #------------------------------------
        outcome = {'1X': [matches_list[:2]],
                  'X2': [matches_list[2:4]]}

        response = make_response(jsonify({"League": league_name,
                                          "round":round,
                                          "outcome": outcome}), 200)

        #
        # response = make_response(jsonify({"League": league_name,
        #                                   "Matches": matches}), 200)

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
        model, configs = load_configs(league_name)

        if (model.testloader is not None):
            test_size = len(model.testloader[field])
        else:
            test_size = 100

        test_data = generate_test_data(league_name)

        feat_eng = configs['feat_eng']

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
