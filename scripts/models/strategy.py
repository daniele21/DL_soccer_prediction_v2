from tqdm import tqdm

from scripts.data.postprocessing import postprocessing_test_data
from scripts.models.evaluation import _select_match_to_bet, thr_analysis, evaluate_results
from scripts.utils.checker import check_simulation_params
from scripts.utils.saving import save_simulation_details, save_simulation
from scripts.visualization.plots import plot_simulation
from scripts.visualization.summary import summary_dataframe
from scripts.constants.configs import DEFAULT_CKP_BOUNDS

from core.file_manager.os_utils import ensure_folder

import pandas as pd
import numpy as np


def summarize_sim_result(sim_result, params):

    thr = params['thr']
    combo_list = params['combo_list']
    filter_bet = params['filter_bet']
    money_bet = params['money_bet']
    field = str(params['field'])
    test_size = int(params['test_size'])
    save_dir = params['save_dir']

    try:
        cum_gain_series = sim_result[sim_result['cum_gain'] != 0]['cum_gain']
    except:
        return None

    win_bets = len(sim_result[sim_result.roi > 0])
    loss_bets = len(sim_result[sim_result.roi < 0])

    overall_money_bet = np.arange(1, len(cum_gain_series)+1, 1)
    perc_gain = cum_gain_series / (overall_money_bet)

    matches = win_bets + loss_bets
    support = matches / test_size
    tpr = win_bets / matches

    config = {'field': field,
              'test_size': test_size,
              'thr': thr,
              'filter_bet': filter_bet,
              'bet_money': money_bet}

    outcome = {'support': support,
               'tpr': tpr,
               'matches': win_bets + loss_bets,
               'wins': win_bets,
               'losses': loss_bets,}

    reward = {'gain':cum_gain_series.to_list()}

    reward_perc = {'gain':perc_gain.to_list()}

    for n_combo in combo_list:
        cum_combo_key = f'cum_combo_x{n_combo}'
        combo_key = f'combo_x{n_combo}'
        cum_money_bet_key = f'money_combo_x{n_combo}'

        cum_combo_series = sim_result[cum_combo_key]
        perc_combo = cum_combo_series / sim_result[cum_money_bet_key]

        reward[combo_key] = cum_combo_series.to_list()
        reward_perc[combo_key] = perc_combo.to_list()

    summary = {'config':config,
               'outcome':outcome,
               'reward':reward,
               'reward_perc':reward_perc}

    # if(save_dir is not None):
    #     save_dir = f'{save_dir}5.simulations/'
    #     ensure_folder(save_dir)
    #     save_simulation_details(summary, params, save_dir)

    return summary

def simulation(match_data, params, plot=False):

    n_matches = params['n_matches']
    combo_list = params['combo_list']
    field = params['field']
    save_dir = params.get('save_dir')

    data = match_data.iloc[:n_matches]
    simulation_df = pd.DataFrame()

    sim_result, _ = _select_match_to_bet(data, params)
    simulation_df = simulation_df.append(sim_result)

    if(len(simulation_df) == 0):
        return None, None

    if(combo_list is not None):
        for n_combo in combo_list:
            _, combo_reward = _select_match_to_bet(data, params, n_combo)

            pos_col = len(simulation_df.columns)
            combo_col = f'combo_x{n_combo}'
            simulation_df.insert(pos_col, combo_col, combo_reward['list'])
            combo_col = f'money_combo_x{n_combo}'
            simulation_df.insert(pos_col+1, combo_col, combo_reward['cum_money_bet'])
            combo_col = f'cum_combo_x{n_combo}'
            simulation_df.insert(pos_col+2, combo_col, combo_reward['cum_list'])

    fig = plot_simulation(simulation_df, params, plot)

    if(save_dir is not None):
        save_simulation(simulation_df, params, save_dir)

    return simulation_df, fig

def strategy_stats(testset, pred, true,
                   simulation_params):

    field = simulation_params['field']
    thr_list = simulation_params['thr_list']
    filter_bet_list = simulation_params['filter_bet_list']

    result_df = pd.DataFrame()
    ckp_df = pd.DataFrame()

    for thr in tqdm(thr_list):
        for filter_bet in filter_bet_list:
            _, _, thr_outcome = thr_analysis(true, pred, simulation_params)

            if (thr_outcome[str(thr)]['tpr'] != 'nan'):

                simulation_params['thr'] = thr
                simulation_params['filter_bet'] = filter_bet
                pred_df, outcome, _ = evaluate_results(true, pred, simulation_params, plot=False)
                sim_data = postprocessing_test_data(testset, pred_df)

                sim_result, _ = simulation(sim_data,
                                            simulation_params,
                                            plot=False)

                if(sim_result is not None):
                    summary = summarize_sim_result(sim_result, simulation_params)
                    if(summary is None):
                        continue
                else:
                    continue

                summary_df = summary_dataframe(summary)
                summary_df.insert(0, 'match', sim_result['match'].to_list())
                summary_df.insert(0, 'Match N.', sim_result['n_match'].to_list())
                summary_df.insert(0, 'Bet N.', np.arange(1,len(sim_result)+1))
                result_df = result_df.append(summary_df)
                ckp_df = ckp_df.append(checkpoint_view_df(summary_df))

    result_df = result_df.reset_index(drop=True)

    save_dir = simulation_params['save_dir']
    if(save_dir is not None):
        filepath = f'{save_dir}simulation_analysis_{field}.csv'
        result_df.to_csv(filepath, sep=';', decimal=',')

        filepath = f'{save_dir}simulation_ckp_analysis_{field}.csv'
        ckp_df.to_csv(filepath, sep=';', decimal=',')

    return result_df, ckp_df

def checkpoint_view_df(summary_df):

    ckp_df = pd.DataFrame()

    for lower_bound, upper_bound in DEFAULT_CKP_BOUNDS:

        ckp_row = summary_df[(summary_df['Match N.'] >= lower_bound) &
                             (summary_df['Match N.'] < upper_bound)].iloc[0:1]

        ckp_df = ckp_df.append(ckp_row)

    ckp_df = ckp_df.drop(['bet_money', 'losses', 'matches', 'match',
                          'support', 'test_size', 'tpr', 'wins'], axis=1)

    return ckp_df