from core.file_manager.loading import load_json
from scripts.constants.league import LEAGUE_DECODER
from scripts.frontend.list_view import List_Window
from scripts.frontend.result_view import Result_view, Probability_view
from scripts.frontend.api_requests import predict_request
from scripts.frontend.graphic_objects import _insert_match_menus, DEFAULT_TEAM, show_list_view
import tkinter as tk
import pandas as pd

from scripts.frontend.gui_interface import Child_Window, Frame_Window
from scripts.inference.poisson_inference import Event_Probability
from scripts.models.poisson_model import Poisson_Model, create_poisson_model


def league_on_change(args_fn, *args):

    root = args_fn['root']
    frames = args_fn['frames']
    league_var = args_fn['league_var']
    teams_dict = args_fn['teams_dict']
    matches = args_fn['matches']
    next_matches_dict = args_fn.get('next_matches')
    ok_button = args_fn['ok_button']
    load_button = args_fn['load_button']

    print(root)

    league_name = league_var.get()
    teams_list = teams_dict[league_name]
    teams_list.sort()

    print('> Changing League: {}'.format(league_name))

    _insert_match_menus(root, frames, teams_list, matches)

    ok_button.configure(state=tk.ACTIVE)

    available_leagues = list(LEAGUE_DECODER['league2league'].keys())
    if(league_name in available_leagues):
        load_button.configure(state=tk.ACTIVE)
    else:
        load_button.configure(state=tk.DISABLED)

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

def load_matches(args_fn, *args):

    root = args_fn['root']
    league_var = args_fn['league_var']
    matches_vars = args_fn['matches_vars']
    next_matches_dict = args_fn['next_matches']

    league_name = league_var.get()
    next_matches = next_matches_dict[league_name]

    str_matches = [f'{next_matches.loc[i_match, "home_team"]} - {next_matches.loc[i_match, "away_team"]}' for i_match in next_matches.index]

    list_view = List_Window(root, None, str_matches)

    index_items = list_view.get_selected_items()

    league_decoder = LEAGUE_DECODER['league2league'][league_name]

    i_vars = 0
    for i in index_items:
        home_team =  next_matches.iloc[i]['home_team']
        away_team = next_matches.iloc[i]['away_team']

        matches_vars['home_team'][i_vars].set(league_decoder[home_team])
        matches_vars['away_team'][i_vars].set(league_decoder[away_team])
        i_vars += 1

    return

def compute_probability(args_fn, *args):
    root = args_fn['root']
    league_var = args_fn['league']
    match_vars = args_fn['matches']

    home_teams = [var.get() for var in match_vars['home_team'] if var.get() != DEFAULT_TEAM]
    away_teams = [var.get() for var in match_vars['away_team'] if var.get() != DEFAULT_TEAM]
    n_matches = min(len(home_teams), len(away_teams))

    params = {'league_name': league_var.get(),
              'home_teams': home_teams,
              'away_teams': away_teams}

    poisson_model = create_poisson_model(league_var.get())

    result_list = []
    prob_df, odds_df = pd.DataFrame(), pd.DataFrame()

    for i in range(len(home_teams)):
        match_dict = {}
        home_team, away_team = home_teams[i], away_teams[i]
        events = Event_Probability(poisson_model.predict(home_team, away_team))

        match_dict['prob'] = events.get_pred_dict()
        match_dict['prob']['match'] = f'{home_team} - {away_team}'
        match_dict['odds'] = events.get_odds_dict()
        match_dict['odds']['match'] = f'{home_team} - {away_team}'

        result_list.append(match_dict)

        prob_df = prob_df.append(match_dict['prob'], ignore_index=True)
        odds_df = odds_df.append(match_dict['odds'], ignore_index=True)

    result_dfs = {'prob': prob_df,
                  'odds': odds_df}

    result_view = Probability_view(root, None, result_dfs)



