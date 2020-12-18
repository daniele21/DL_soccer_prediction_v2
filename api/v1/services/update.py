from flask import make_response, jsonify, request, render_template

from scripts.utils.checker import check_league, check_data_league
import scripts.constants.league as LEAGUE
from scripts.constants.paths import DATA_DIR
from scripts.data.data_process import update_data_league

from core.logger.logging import logger

from flask import current_app as app


@app.route('/api/v1/update/<league_name>', methods=['GET'])
def update_league(league_name):

    npm = request.args['npm']

    assert int(npm) > 0, 'NPM must be greater than 0'

    league_params = {}

    response_league_name = check_league(league_name)
    response_league_data = check_data_league(league_name, npm) if response_league_name['check'] else {'check':False,
                                                                                                      'msg':''}

    msg = f"League_name: {response_league_name['msg']} \nLeague_data: {response_league_data['msg']}"

    if not response_league_name['check'] or not response_league_data['check']:
        response = make_response(msg, 404)
    else:
        league_params['league_name'] = league_name
        league_params['n_prev_match'] = npm
        league_params['league_dir'] = DATA_DIR

        response = update_data_league(league_params)

        if response['check']:
            succ_msg = f'Successful Update: {league_name} - npm={npm}'
            logger.info(succ_msg)
            response = make_response(f'Successful Update: {league_name} -> npm = {npm}', 200)
        else:
            fail_msg = f'Failed Update: {league_name} - npm={npm} \n {response["msg"]}'
            logger.error(fail_msg)
            response = make_response(f'Failed Update: {league_name} -> npm = {npm} \n {response["msg"]}', 400)

    return response
