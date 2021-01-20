from core.file_manager.loading import load_json
from scripts.frontend.Result_view import Result_view
from scripts.frontend.api_requests import predict_request
from scripts.frontend.graphic_objects import _insert_match_menus, DEFAULT_TEAM
import tkinter as tk

from scripts.frontend.gui_interface import Child_Window, Frame_Window


def league_on_change(args_fn, *args):

    root = args_fn['root']
    frames = args_fn['frames']
    league_var = args_fn['league_var']
    teams_dict = args_fn['teams_dict']
    matches = args_fn['matches']
    ok_button = args_fn['ok_button']
    # clear_button = args_fn['clear_button']

    print(root)

    league_name = league_var.get()
    teams_list = teams_dict[league_name]
    teams_list.sort()

    print('> Changing League: {}'.format(league_name))

    _insert_match_menus(root, frames, teams_list, matches)

    ok_button.configure(state=tk.ACTIVE)
    # clear_button.configure(state=tk.ACTIVE)

def calculate_action(args_fn, *args):
    root = args_fn['root']
    round_var = args_fn['round_var']
    league_var = args_fn['league']
    match_vars = args_fn['matches']
    api_config = args_fn['api_config']

    home_teams = [var.get() for var in match_vars['home_team'] if var.get() != DEFAULT_TEAM]
    away_teams = [var.get() for var in match_vars['away_team'] if var.get() != DEFAULT_TEAM]
    n_matches = min(len(home_teams), len(away_teams))

    home_bets = [var.get() for var in match_vars['1X_bet'][:n_matches]]
    away_bets = [var.get() for var in match_vars['X2_bet'][:n_matches]]

    # run api form prediction
    params = {'league_name': league_var.get(),
              'home_teams': home_teams,
              'away_teams': away_teams,
              '1X_odds': home_bets,
              'X2_odds': away_bets}

    if(api_config is not None):
        response = predict_request(api_config, params)
    else:
        response = load_json('/media/daniele/Data/Projects/DL_soccer_prediction_v2/resources/predictions/serie_a/round_17 (copy).json')

    results = {'predict': response}

    result_view = Result_view(root, None, results)
