from scripts.data.data_process import extract_data_league
from scripts.utils.checker import check_league, check_npm
from scripts.constants.paths import DATA_DIR

from flask import make_response, jsonify, request, render_template
from flask import current_app as app

from multiprocessing import Process, set_start_method


@app.route('/api/v1/write/league_data', methods=['POST'])
def create_league_data():
    """
    Create and Save league data for some league available

    Method = POST
    Body: { 'league_name': LEAGUE_NAME,
            'n_prev_match': NPM,
          }

    """

    # requested params [league_name, npm]
    params = request.json
    league_name = params['league_name']
    npm = params['n_prev_match']

    response_league_name = check_league(league_name)
    response_npm = check_npm(npm)

    if response_npm['check'] and response_league_name['check']:

        params['league_dir'] = DATA_DIR
        params['train'] = True

        try:
            set_start_method('spawn')
        except RuntimeError:
            pass

        p = Process(target=extract_data_league, args=(params,))
        p.start()
        p.join()
        # league_df, preprocessed_data = extract_data_league(params)

        response = make_response(f'Successfully writing: {league_name.upper()}, npm = {npm}', 200)

    else:
        error_msg = f'League name : {response_league_name["msg"]}'
        error_msg += f'NPM : {response_npm["msg"]}'

        response = make_response(error_msg, 400)

    return response





