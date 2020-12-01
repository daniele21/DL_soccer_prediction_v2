# -*- coding: utf-8 -*-

import torch
import numpy as np
import os
from sklearn.metrics import (roc_curve,
                             auc, f1_score,
                             precision_recall_curve,
                             precision_score,
                             accuracy_score,
                             average_precision_score,
                             recall_score)
from scipy.optimize import brentq
from scipy.interpolate import interp1d
from scipy.stats import cumfreq
from matplotlib import pyplot as plt
import pandas as pd

from scripts.data.postprocessing import labeling_predictions
from scripts.models.model_utils import save_evaluation
from scripts.utils.saving import save_simulation_details
from scripts.utils.utils import multiply_all_list_elements
from scripts.visualization.plots import plot_hist, plot_simulation


def eval_inference(testloader, feat_eng, model, model_name=None):

    model_name = str(model_name).lower()
    assert model_name == 'home' or model_name == 'away', 'ERROR - evaluate_data: WRONG model_name'

    true_outcome = testloader['f-WD']
    testloader = testloader.drop('f-WD')
    pred_outcome = model.predict(testloader, model_name)

    return pred_outcome, true_outcome

def evaluate_results(true, pred, eval_params, plot=True):
    thr = eval_params['thr']

    pred_df = labeling_predictions(true, pred, thr)

    my_choise = pred_df
    right_choise = my_choise[my_choise.true == 1]
    # bad_choise = my_choise[my_choise.true == 0]


    fig = plot_hist(right_choise['pred'], my_choise['pred'],
                    params=eval_params,
                    labels=['my_choise', 'right_choise'],
                    plot=plot)
    # plot_hist(my_choise['pred'], bad_choise['pred'], field=field, thr=thr, labels=['true', 'bad'])

    return pred_df, fig


def summarize_sim_result(sim_result, params):

    filter_bet = params['filter_bet']
    money_bet = params['money_bet']
    n_combo = int(params['combo'])
    field = str(params['field'])
    save_dir = params['save_dir'] if 'save_dir' in list(params.keys()) else None

    cum_gain_list = sim_result[sim_result['cum_gain'] != 0]['cum_gain'].to_list()
    combo = sim_result[f'combo_{n_combo}'].cumsum().fillna(method='bfill')
    combo = combo.fillna(method='ffill').to_list()

    win_bets = len(sim_result[sim_result.roi > 0])
    loss_bets = len(sim_result[sim_result.roi < 0])

    perc_gain = cum_gain_list[-1] / (len(cum_gain_list) * money_bet)
    perc_combo = combo[-1]/(len(combo * money_bet))

    result_str = ''
    result_str += f'> Threshold bet:       {filter_bet}\n'
    result_str += f'> Matches bet:         {len(cum_gain_list) * money_bet}\n'
    result_str += f'> Money per match:     {money_bet} €\n'
    result_str += f'> Win/Loss bet:        {win_bets}/{loss_bets} \n'
    result_str += f'> Net Gain:            {cum_gain_list[-1]:.2f} ({perc_gain*100:.0f} %)\n'
    result_str += f'> Combo x{n_combo}:            {combo[-1]:.2f} ({perc_combo*100:.0f} %)\n'

    print(result_str)

    if(save_dir is not None):
        save_simulation_details(field, result_str, save_dir)

    return result_str

def simulation(test_result, params, plot=False):

    n_matches = params['n_matches']
    combo = params['combo']
    field = params['field']
    save_dir = params['save_dir'] if 'save_dir' in list(params.keys()) else None

    data = test_result.iloc[:n_matches]

    sim_result = _select_match_to_bet(data, params)

    summary = summarize_sim_result(sim_result, params)

    fig = plot_simulation(sim_result, params, plot)

    return summary, data, fig


def compute_roc(true_outcome, pred_outcome, info='', plot=False):
    roc_auc, opt_threshold = evaluate_roc(true_outcome,
                                          pred_outcome,
                                          info=info, plot=plot)

    return roc_auc, opt_threshold

def test_prediction(testloader, model):
    home_pred, home_true = [], []
    away_pred, away_true = [], []
    
    
    with torch.no_grad():
        model.model.home_network.lstm.flatten_parameters()
        model.model.away_network.lstm.flatten_parameters()
        
        for x_home, y_home, x_away, y_away in testloader:
            
            x_home = torch.Tensor(x_home).to(model.device)
            x_away = torch.Tensor(x_away).to(model.device)
            
            y_home = torch.Tensor(y_home).to(model.device).squeeze()
            y_away = torch.Tensor(y_away).to(model.device).squeeze()    
            
            _, home_out, away_out = model.model(x_home, x_away)
            
            if(testloader.batch_size > 1):
                home_pred.extend(home_out.tolist())
                away_pred.extend(away_out.tolist())
                home_true.extend(y_home.tolist())
                away_true.extend(y_away.tolist())
            else:
                home_pred.append(home_out.item())
                away_pred.append(away_out.item())
                home_true.append(y_home.item())
                away_true.append(y_away.item())        
                
            pred = {'home':home_pred,
                    'away':away_pred}
            true = {'home':home_true,
                    'away':away_true}
            
        return pred, true

def _select_match_to_bet(test_data, params):
    '''
        SELECT JUST THE POSITIVE PREDICTIONS
    '''

    filter_bet = params['filter_bet']
    money_bet = params['money_bet']
    n_combo = params['combo']

    matches = []
    roi_list = []
    result_list = []
    cum_gain_list = []
    combo_buffer = []
    combo_list = []

    data = test_data.reset_index(drop=True)
    data = data[(data['to_bet'] == True) & (data['bet'] > filter_bet) ]

    for i_row in data.index:
        row = data.loc[i_row]
        bet_WD = row['bet']
        true_result = bool(row['true-WD'])
        match = f'{i_row} | {row["match"]}'

        # JUST POSITIVE CASES --> WHERE I WANT TO BET WD

        if(true_result):
            gain = (money_bet * bet_WD) - money_bet
            result_list.append('Win')
            combo_buffer.append(bet_WD)

        else:
            gain = -money_bet
            result_list.append('Lose')
            combo_buffer.append(-1)

        roi_list.append(gain)
        matches.append(match)
        cum_gain_list.append(sum(roi_list))

        if(len(combo_buffer) == n_combo):
            combo_list.append(money_bet * multiply_all_list_elements(combo_buffer))
            combo_buffer = []
        else:
            combo_list.append(np.nan)

    data['outcome'] = result_list
    data['roi'] = roi_list
    data[f'combo_{n_combo}'] = combo_list
    data['cum_gain'] = cum_gain_list
    data['match'] = matches
    
    return data

# def simulation(testloader, pred, true,
#                feat_eng, params):
#
#     data = {'home':testloader.dataset.x_home[:len(pred['home'])],
#             'away':testloader.dataset.x_away[:len(pred['away'])]}
#
#     sim_data = feat_eng.decoding(data, pred, true)
#
#     data = {}
#     index = {}
#
#     n_matches = params['n_matches']
#     combo = params['combo']
#
#     for x in ['home', 'away']:
#
#         data[x] = sim_data[x][:n_matches]
#
#         result = _select_match_to_bet(data[x], params)
#
#         data[x]['outcome'] = result['result_list']
#         data[x]['roi'] = result['roi_list']
#         data[x][f'combo_{combo}'] = result['cum_combo_list']
#         data[x]['cum_gain'] = result['cum_gain_list']
#
#         index[x] = result['index']
#
#     return data, index

# def test_evaluation(evalloader, model, params,
#                     threshold=None, n_matches=None,
#                     save=True):
#
#     pred, true = test_prediction(evalloader, model)
#
#     if(n_matches is not None):
#         pred = {'home':pred['home'][:n_matches],
#                 'away':pred['away'][:n_matches]}
#
#         true = {'home':true['home'][:n_matches],
#                 'away':true['away'][:n_matches]}
#
#     if(threshold is None):
#         for x in ['home', 'away']:
#             evaluate_roc(true[x], pred[x], info=x, plot=True)
#
#     else:
#         tpr = {}
#         n_pos = {}
#         pred_thr = {}
#
#         for x in ['home', 'away']:
#             _plot_hist(true[x], pred[x],
#                        threshold, x.upper(),
#                        save_folder=save)
#
#             pred_thr[x] = [1 if x >= threshold else 0 for x in pred[x]]
#             tpr_x, n_pos_x = _true_positive_rate(true[x],
#                                                  pred_thr[x],
#                                                  threshold)
#             tpr[x] = tpr_x
#             n_pos[x] = n_pos_x
#
#             print(f'> {x.upper()} TPR: {tpr[x]:.2f} over {n_pos[x]}/{len(pred["home"])} matches ({n_pos[x]/len(pred["home"]):.3f})')
#
#         tot_matches = len(pred['home'])
#         save_evaluation(tpr, n_pos, tot_matches, threshold, params)
#
#         return pred_thr, true

def computing_test_outcome(testloader, feat_eng, pred, params):
    
    pred_thr = {}
    thr = params['thr']
    filter_bet = params['filter_bet']
    
    for x in ['home', 'away']:
        pred_thr[x] = [1 if x >= thr else 0 for x in pred[x]]
        
        
    data = {'home':testloader.dataset.x_home,
            'away':testloader.dataset.x_away}
    
    sim_result = feat_eng.decoding(data, pred_thr, None)
    
    filt_result = sim_result[(sim_result['bet_WD'] > filter_bet) & 
                             (sim_result['WD'] == 1)]
    
    return filt_result
    
def _true_positive_rate(labels, scores, threshold):
#    scores = [1 if x >= threshold else 0 for x in scores]
    pred_pos = [labels[i] == x for i, x in enumerate(scores) if x == 1]
    n_right_pred = len(np.where(pred_pos)[0])
    tpr_rate = n_right_pred / (len(pred_pos) + 0.00001)
    
    return tpr_rate, len(pred_pos)
    
def _getOptimalThreshold(fpr, tpr, threshold):
    
    i = np.arange(len(tpr)) 
    roc = pd.DataFrame({'tf' : pd.Series(tpr-(1-fpr), index=i),
                        'threshold' : pd.Series(threshold, index=i)})
    roc_t = roc.loc[roc.tf.abs() == roc.tf.abs().min()]
    opt_threshold = roc_t.threshold
    
    return opt_threshold.values[0]
     
def evaluate_roc(labels, scores, info='', plot=False):
    """Compute ROC curve and ROC area for each class"""
    fpr = dict()
    tpr = dict()
    roc_auc = dict()
    
    fpr, tpr, threshold = roc_curve(labels, scores)
    
    opt_threshold = _getOptimalThreshold(fpr, tpr, threshold)
    
    roc_auc = auc(fpr, tpr)

    # Equal Error Rate
    eer = brentq(lambda x: 1. - x - interp1d(fpr, tpr)(x), 0., 1.)      
    
    if(plot):
        fig, ax1 = plt.subplots(1,1, figsize=(5,3))
        
        lw = 2
        
        # PLOTTING AUC
        ax1.plot(fpr, tpr, color='darkorange', lw=lw, label='(AUC = %0.3f, EER = %0.3f)' % (roc_auc, eer))
        ax1.plot([eer], [1-eer], marker='o', markersize=5, color="navy")
        ax1.fill_between(fpr, tpr, alpha=0.3, color='orange')
        ax1.plot([0, 1], [1, 0], color='navy', lw=1, linestyle=':')
        ax1.plot(fpr, threshold, markeredgecolor='r',linestyle='dashed', color='r', label='Threshold = {:.5f}'.format(opt_threshold))
        ax1.set_xlim([0.0, 1.0])
        ax1.set_ylim([0.0, 1.05])
        ax1.set_xlabel('False Positive Rate')
        ax1.set_ylabel('True Positive Rate')
        ax1.set_title('Receiver operating characteristic {}'.format(info.upper()))
        ax1.legend(loc="lower right")
        
        fig.tight_layout()        
        plt.show()
            
    print('> {}'.format(info.upper()))
    print('> AUC       :\t{:.3f}'.format(roc_auc))
    print('> EER       :\t{:.3f}'.format(eer))
    print('> Threshold :\t{:.5f}\n'.format(opt_threshold))

    return roc_auc, opt_threshold

def _plot_hist(labels, scores, thr=None, title='',
               save_folder=None):
    
    pos_true = []
    
    for i, label in enumerate(labels):
        if(label):
            pos_true.append(scores[i])
    
    plt.figure(figsize=(15,7))
    plt.title(title)
    n, _, _ = plt.hist(scores, bins=100, color='b', alpha=0.2, label='Pred_POS_WD')
    _, _, _ = plt.hist(pos_true, bins=100, color='r', alpha=0.2, label='True_POS_WD')

    if(thr is not None):
#        print(thr)
        plt.axvline(x=thr, c='r', linewidth=3, label=f'Threshold: {thr}')

    plt.legend(loc='best')
    
    if(save_folder):
        filename = f'histogram_{title}_thr={thr}.png'
        filepath = f'{save_folder}{filename}'
        plt.savefig(filepath)
        print(f'> Saving histograms at {filepath}')
    
    plt.show()
    
def inference_hist(matches, scores, thr=None, title='', save_folder=None):
    
    for i, score in enumerate(scores):
        matches[i] += f' || {score:.2f}'
    
    plt.figure(figsize=(15,7))
    plt.title(title)
    n, _, _ = plt.hist(scores, bins=100, color='b', alpha=0.2, label='Pred_POS_WD')
    plt.xticks(scores, labels=matches, rotation=90)
    
    if(thr is not None):
#        print(thr)
        plt.axvline(x=thr, c='r', linewidth=3, label=f'Threshold: {thr}')
        
    plt.legend(loc='best')
    plt.tight_layout()
    
    if(save_folder):
        filename = f'histogram_{title}_{thr}.png'
        filepath = f'{save_folder}{filename}'
        plt.savefig(filepath)
        print(f'> Saving histograms at {filepath}')
    
    plt.show()
    
    

    
    
    
        