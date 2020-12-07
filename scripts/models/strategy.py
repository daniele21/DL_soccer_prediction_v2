from scripts.data.postprocessing import postprocessing_test_data
from scripts.models.evaluation import _select_match_to_bet, thr_analysis, evaluate_results
from scripts.utils.saving import save_simulation_details
from scripts.visualization.plots import plot_simulation
from scripts.visualization.summary import summary_dataframe

import pandas as pd


def summarize_sim_result(sim_result, params, thr_analysis):

    if('combo_list' in list(params.keys())):
        combo_list = params['combo_list']
    elif('combo' in list(params.keys())):
        combo_list = list(params['combo'])
    else:
        combo_list = []

    thr = params['thr']
    filter_bet = params['filter_bet']
    money_bet = params['money_bet']
    field = str(params['field'])
    save_dir = params['save_dir'] if 'save_dir' in list(params.keys()) else None

    cum_gain_list = sim_result[sim_result['cum_gain'] != 0]['cum_gain'].to_list()

    win_bets = len(sim_result[sim_result.roi > 0])
    loss_bets = len(sim_result[sim_result.roi < 0])

    perc_gain = cum_gain_list[-1] / (len(cum_gain_list) * money_bet) if len(cum_gain_list)>0 else None

    config = {'field':params['field'],
              'test_size':params['test_size'],
              'thr': thr,
              'filter_bet': filter_bet,
              'bet_money': money_bet}

    outcome = {'support': thr_analysis['support'],
               'tpr': thr_analysis['tpr'],
               'matches': win_bets + loss_bets,
               'wins': win_bets,
               'losses': loss_bets,}

    reward = {'gain':cum_gain_list[-1]}

    reward_perc = {'gain':perc_gain}

    for n_combo in combo_list:
        key = f'combo_x{n_combo}'
        combo = sim_result[key].cumsum().fillna(method='bfill')
        combo = combo.fillna(method='ffill').to_list()
        perc_combo = combo[-1]/(len(combo * money_bet))
        reward[key] = combo[-1]
        reward_perc[key] = perc_combo

    summary = {'config':config,
               'outcome':outcome,
               'reward':reward,
               'reward_perc':reward_perc}

    if(save_dir is not None):
        save_simulation_details(summary, params, save_dir)

    return summary

def simulation(test_result, params, thr_analysis, plot=False):

    thr = params['thr']
    n_matches = params['n_matches']
    combo = params['combo'] if 'combo' in list(params.keys()) else None
    combo_list = params['combo_list'] if 'combo_list' in list(params.keys()) else None

    data = test_result.iloc[:n_matches]
    simulation_df = pd.DataFrame()

    sim_result, _ = _select_match_to_bet(data, params)
    simulation_df = simulation_df.append(sim_result)

    if(len(simulation_df) == 0):
        return None, None, None

    if(combo_list is not None and combo is None):
        for n_combo in combo_list:
            _, combo_values = _select_match_to_bet(data, params, n_combo)

            pos_col = len(simulation_df.columns)
            combo_col = f'combo_x{n_combo}'
            simulation_df.insert(pos_col, combo_col, combo_values)

    elif(combo_list is None and combo is not None):
        n_combo = combo
        _, combo_values = _select_match_to_bet(data, params, n_combo)
        pos_col = len(simulation_df.columns)
        combo_col = f'combo_x{n_combo}'
        simulation_df.insert(pos_col, combo_col, combo_values)

    summary = summarize_sim_result(simulation_df, params, thr_analysis)

    fig = plot_simulation(simulation_df, params, plot)

    return summary, data, fig

def strategy_stats(testset, pred, true,
                   simulation_params, thr_list, filter_bet_list,
                   save_dir):

    field = simulation_params['field']

    result_df = pd.DataFrame()

    for thr in thr_list:
        for filter_bet in filter_bet_list:
            _, thr_outcome = thr_analysis(true, pred, thr_list, save_dir=save_dir)

            if (thr_outcome[str(thr)]['tpr'] != 'nan'):

                simulation_params['thr'] = thr
                simulation_params['filter_bet'] = filter_bet
                pred_df, outcome, _ = evaluate_results(true, pred, simulation_params, plot=False)
                sim_data = postprocessing_test_data(testset, pred_df)

                summary, sim_result, _ = simulation(sim_data,
                                                    simulation_params,
                                                    thr_outcome[str(thr)],
                                                    plot=False)
                if(summary is None):
                    continue

                summary_df = summary_dataframe(summary)

                result_df = result_df.append(summary_df)


    result_df = result_df.dropna()\
                         .reset_index(drop=True)

    if(save_dir is not None):
        filepath = f'{save_dir}simulation_analysis_{field}.csv'
        result_df.to_csv(filepath, sep=';', decimal=',')

    return result_df

