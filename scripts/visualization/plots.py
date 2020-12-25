# -*- coding: utf-8 -*-
import matplotlib
import matplotlib.pyplot as plt

matplotlib.use('agg')

from core.file_manager.os_utils import ensure_folder
from scripts.utils.saving import save_simulation_details


def plot_loss(train_loss, test_loss,
              figsize=(7,5), save=True,
              save_dir='', plot_dir=None, filename=None,
              plot=True):
    
    fig = plt.figure(figsize=figsize)
    plt.title('Model Loss', fontsize=15)
    plt.plot(train_loss, c='r', label='Train')
    plt.plot(test_loss, c='b', label='Eval')
    plt.grid()
    plt.legend(loc='best')
    
    if(save):
        ensure_folder(save_dir)
        filename = 'loss_plot' if filename is None else filename
        filepath = f'{save_dir}{filename}.png'
        plt.savefig(filepath)

        if(plot_dir is not None):
            filepath = f'{plot_dir}training_plot.png'
            plt.savefig(filepath)

    if(plot):
        plt.show()
    
    return fig

def plot_aic_bic(aics, bics, figsize=(7,7),
                 save=True, save_dir=''):
    
    fig, [ax1,ax2] = plt.subplots(2,1, figsize=figsize)
    
    ax1.set_title('AIC')
    ax1.plot(aics, c='green', label='AIC')
    ax1.grid()
    ax1.legend()
    
    ax2.set_title('BIC')
    ax2.plot(bics, c='brown', label='BIC')
    ax2.grid()
    ax2.legend()
    
    if(save):
        filepath = f'{save_dir}aic-bic_plot.png'
        plt.savefig(filepath)
    
    plt.show()


def plot_hist(true, pred, params, outcome,
              labels=['True_Outcome',
                      'Pred_Outcome'],
              plot='True'):

    thr = outcome['thr']
    opt_thr = outcome['opt_thr']
    tpr = outcome['tpr']
    auc = outcome['auc']
    field = params['field']
    save_dir = params['save_dir'] if 'save_dir' in list(params.keys()) else None

    pred = list(pred)
    true = list(true)
    field = str(field).lower()

    assert str(field) == 'home' or str(field) == 'away', 'ERROR - plot_hist: WRONG field provided'
    title = f'{field.upper()}_Histogram'

    fig = plt.figure(figsize=(15,7))
    plt.title(title)

    _ = plt.hist(pred, bins=100, color='b', alpha=0.2, label=labels[0], density=True)
    _ = plt.hist(true, bins=100, color='r', alpha=0.2, label=labels[1], density=True)
    # plt.axvline(x=opt_thr, c='r', linewidth=3, label=f'Opt Thr: {thr} | AUC: {auc}')

    if (thr is not None):
        plt.axvline(x=thr, c='b', linewidth=2, label=f'My Thr: {thr} | AUC: {auc:.3f} | opt thr: {opt_thr:.3f} | tpr: {tpr:.3f}')
        # plt.axvline(x=thr, c='b', linewidth=2, label=f'My Thr: {thr}')

    plt.legend(loc='best', fontsize=7)

    if(save_dir and plot):
        filename = f'{title}_thr={thr}.png'
        filepath = f'{save_dir}{filename}'
        plt.savefig(filepath)
        print(f'> Saving histograms at {filepath}')

    if(plot):
        plt.show()
    else:
        plt.close(fig)


    return fig

def plot_simulation(simulation_result, params, plot=True):

    # filter_bet = params['filter_bet']
    # money_bet = params['money_bet']
    combo_dict = {}
    cols = simulation_result.columns

    i = 2
    for col in cols:
        if('combo' in col):
            combo = simulation_result[col].cumsum()\
                            .fillna(method='bfill')\
                            .fillna(method='ffill').to_list()
            combo_dict[i] = combo
            i += 1

    field = str(params['field'])
    filter_bet = params['filter_bet']
    thr = params['thr']
    save_dir = params['save_dir'] if 'save_dir' in list(params.keys()) else None

    title = f'{field.upper()}_thr={thr}_filter={filter_bet}'

    data = simulation_result
    cum_gain_list = data[data['cum_gain']!=0]['cum_gain'].to_list()

    labels = simulation_result['match'].to_list()
    idxs = range(len(labels))

    # PLOTTING

    fig = plt.figure(figsize=(15,8))
    plt.title(title)

    plt.plot(idxs, cum_gain_list, label='no combo')
    plt.fill_between(idxs, cum_gain_list, alpha=0.3)

    for combo_key in combo_dict:
        combo = combo_dict[combo_key]
        plt.plot(idxs, combo, label=f'combo x{combo_key}')

    plt.xticks(idxs, labels=labels, rotation=90)
    plt.legend()
    plt.grid()
    plt.tight_layout()

    if(save_dir is not None and plot):
        filename = f'5.simulations_plot_{field}_thr={thr}_filter={filter_bet}.png'
        filepath = f'{save_dir}/{filename}'
        plt.savefig(filepath)

    if(plot):
        plt.show()
    else:
        plt.close(fig)

    return fig

def plot_thr_analysis(thr_analysis_df):
    for col in thr_analysis_df:
        thr_analysis_df[col] = thr_analysis_df[col].astype(float)

    thr_analysis_df = thr_analysis_df.dropna()

    thr_list = thr_analysis_df['thr'].to_list()
    support_list = thr_analysis_df['support'].to_list()
    tpr_list = thr_analysis_df['tpr'].to_list()

    plt.plot(thr_list, tpr_list, c='green', label='TPR')
    plt.scatter(x=thr_list, y=tpr_list, c='green')
    plt.plot(thr_list, support_list, c='b', label='Support')
    plt.scatter(x=thr_list, y=support_list, c='b')
    plt.grid()
    plt.xlabel('Thr')
    plt.ylim(0,1)

    plt.legend()
    plt.show()
