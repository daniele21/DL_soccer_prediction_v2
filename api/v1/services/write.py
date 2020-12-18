from scripts.data.data_process import extract_data_league
from scripts.utils.checker import check_league, check_npm
from scripts.constants.paths import DATA_DIR

from flask import make_response, jsonify, request, render_template
from flask import current_app as app


@app.route('/api/v1/write/league_data', methods=['POST'])
def create_league_data():

    # requested params [league_name, npm]
    params = request.json
    league_name = params['league_name']
    npm = params['n_prev_match']

    response_league_name = check_league(league_name)
    response_npm = check_npm(npm)

    if response_npm['check'] and response_league_name['check']:

        params['league_dir'] = DATA_DIR
        params['train'] = True
        league_df, preprocessed_data = extract_data_league(params)

        response = make_response(f'Successfully writing: {league_name.upper()}, npm = {npm}', 200)

    else:
        error_msg = f'League name : {response_league_name["msg"]}'
        error_msg += f'NPM : {response_npm["msg"]}'

        response = make_response(error_msg, 400)

    return response





