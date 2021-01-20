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

from core.file_manager.saving import save_json
from core.str2bool import str2bool
from scripts.constants.configs import DEFAULT_THR_LIST
from scripts.data.postprocessing import labeling_predictions
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

def thr_analysis(true, pred, params):
    thr_list = params['thr_list'] if 'thr_list' in list(params.keys()) else DEFAULT_THR_LIST
    save_dir = params['save_dir'] if 'save_dir' in list(params.keys()) else None
    field = params['field']

    assert thr_list is not None and isinstance(thr_list, list)

    analysis_per_thr = {}

    for thr in thr_list:
        pred_df = labeling_predictions(pred, thr, true)
        filtered_pred = pred_df[pred_df['to_bet'] == True]

        if(len(filtered_pred) > 0):
            tpr = f"{(filtered_pred['true']==1).sum() / len(filtered_pred['pred']):.3f}"
            support = f"{len(filtered_pred['pred']) / len(pred_df):.2f}"
        else:
            tpr = 'nan'
            support = 0

        analysis_per_thr[str(thr)] = {'support': float(support),
                                      'tpr': float(tpr)}

    thr_result = pd.DataFrame(analysis_per_thr).transpose()

    thr_result = thr_result.reset_index().rename(columns={'index':'thr'})
    thr_dict = {field: [{'thr': thr_result.loc[i,'thr'],
                         'tpr': thr_result.loc[i,'tpr'],
                         'support': thr_result.loc[i,'support']} for i in thr_result.index]}

    if(save_dir is not None):
        filepath = f'{save_dir}6.{field}_thr_analysis.json'
        save_json(thr_dict, filepath)
        thr_result.to_csv(f'{save_dir}6.{field}_thr_analysis.csv', sep=';', decimal=',')

    return thr_result, thr_dict, analysis_per_thr


def evaluate_results(true, pred, eval_params, plot=True):
    thr = eval_params['thr']
    field = eval_params['field']

    pred_df = labeling_predictions(pred, thr, true)
    pred_df.insert(0, 'field', field)

    if(thr is None):
        return pred_df, None, None

    my_score = pred_df
    right_score = my_score[my_score['true'] == True]
    # bad_choise = my_choise[my_choise.true == 0]

    my_score_to_bet = my_score[my_score['to_bet'] == True]
    auc, opt_thr = compute_roc(pred_df['true'].to_list(),
                               pred_df['pred'].to_list())
    if(len(my_score_to_bet) > 0):
        tpr = (my_score_to_bet['true'] == 1).sum() / (len(my_score_to_bet['pred']))
    else:
        tpr = np.nan

    outcome = {'thr':thr,
               'auc':auc,
               'opt_thr':opt_thr,
               'tpr':tpr}

    fig = plot_hist(right_score['pred'], my_score['pred'],
                    params=eval_params,
                    outcome=outcome,
                    labels=['match_prob', 'win_match'],
                    plot=plot)

    return pred_df, outcome, fig




def compute_roc(true_outcome, pred_outcome, info='', plot=False):
    roc_auc, opt_threshold = evaluate_roc(true_outcome,
                                          pred_outcome,
                                          info=info, plot=plot)

    return roc_auc, opt_threshold

def _select_match_to_bet(match_data, params, combo=None):
    '''
        SELECT JUST THE POSITIVE PREDICTIONS
    '''

    filter_bet = params['filter_bet']
    money_bet = params['money_bet']
    n_combo = combo if combo is not None else None

    n_matches, matches = [], []
    roi_list = []
    result_list = []
    cum_gain_list = []
    combo_buffer = []
    combo_reward = {'cum_money_bet':[],
                    'money_bet':[],
                    'list':[],
                    'cum_list':[]}

    data = match_data.reset_index(drop=True)
    data = data[(data['to_bet'] == True) & (data['bet'] > filter_bet) ]

    for i_row in data.index:
        row = data.loc[i_row]
        bet_WD = row['bet']
        true_WD = bool(row['true-WD'])
        # match = f'{i_row} | {row["match"]}'
        match = row["match"]

        matches.append(match)
        n_matches.append(i_row)

        # JUST POSITIVE CASES --> WHERE I WANT TO BET WD
        if(true_WD):
            gain = (money_bet * bet_WD) - money_bet
            result_list.append('Win')
            combo_buffer.append(bet_WD)

        else:
            gain = -money_bet
            result_list.append('Lose')
            combo_buffer.append(-1)

        roi_list.append(gain)
        cum_gain_list.append(sum(roi_list))

        if(len(combo_buffer) == n_combo):
            combo_reward['list'].append(money_bet * multiply_all_list_elements(combo_buffer))
            combo_reward['money_bet'].append(money_bet)
            combo_buffer = []
        else:
            combo_reward['list'].append(np.nan)
            combo_reward['money_bet'].append(np.nan)

        combo_reward['cum_list'].append(pd.Series(combo_reward['list']).sum())
        combo_reward['cum_money_bet'].append(pd.Series(combo_reward['money_bet']).sum())

    data['outcome'] = result_list
    data['roi'] = roi_list
    # data[f'combo_{n_combo}'] = combo_list
    data['cum_gain'] = cum_gain_list
    data['match'] = matches
    data['n_match'] = n_matches
    
    return data, combo_reward

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
            
        # print('> {}'.format(info.upper()))
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
    
    

    
    
    
        