from flask import make_response, jsonify, request, render_template

from scripts.utils.checker import check_league

import scripts.constants.league as LEAGUE


from flask import current_app as app


@app.route('/api/v1/read/league', methods=['GET'])
def get_league_names():
    return make_response(jsonify({'league_name': LEAGUE.LEAGUE_NAMES}))


@app.route('/api/v1/read/<league_name>/team', methods=['GET'])
def get_teams(league_name):

    outcome, msg = check_league(league_name)
    if not outcome:
        response = make_response(msg, 404)
    else:
        teams = sorted(LEAGUE.TEAMS_LEAGUE[str(league_name).lower()])
        response = make_response(jsonify({'league': league_name,
                                          'teams': teams}))

    return response
