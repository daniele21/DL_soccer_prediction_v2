# -*- coding: utf-8 -*-
import matplotlib.pyplot as plt

from scripts.utils.saving import save_simulation_details


def plot_loss(train_loss, test_loss,
              figsize=(7,5), save=True, save_dir=''):
    
    plt.figure(figsize=figsize)
    plt.title('Model Loss', fontsize=15)
    plt.plot(train_loss, c='r', label='Train')
    plt.plot(test_loss, c='b', label='Eval')
    plt.grid()
    plt.legend(loc='best')
    
    if(save):
        filepath = f'{save_dir}loss_plot.png'
        plt.savefig(filepath)
    
    plt.show()
    
    return

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


def plot_hist(true, pred, params,
              labels=['True_Outcome',
                      'Pred_Outcome'],
              plot='True'):

    thr = params['thr']
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

    if (thr is not None):
        plt.axvline(x=thr, c='r', linewidth=3, label=f'Threshold: {thr}')

    plt.legend(loc='best')

    if(save_dir):
        filename = f'{title}_thr={thr}.png'
        filepath = f'{save_dir}{filename}'
        plt.savefig(filepath)
        print(f'> Saving histograms at {filepath}')

    if(plot):
        plt.show()

    return fig

def plot_simulation(simulation_result, params, plot=True):

    # filter_bet = params['filter_bet']
    # money_bet = params['money_bet']
    n_combo = int(params['combo'])
    field = str(params['field'])
    save_dir = params['save_dir'] if 'save_dir' in list(params.keys()) else None

    data = simulation_result
    cum_gain_list = data[data['cum_gain']!=0]['cum_gain'].to_list()

    combo = data[f'combo_{n_combo}'].cumsum().fillna(method='bfill')
    combo = combo.fillna(method='ffill').to_list()

    labels = simulation_result['match'].to_list()
    idxs = range(len(labels))

    # PLOTTING

    fig = plt.figure(figsize=(17,7))
    plt.title(field.upper())

    plt.plot(idxs, cum_gain_list, label='no combo')
    plt.fill_between(idxs, cum_gain_list, alpha=0.3)
    plt.plot(idxs, combo, c='green', label=f'combo_{n_combo}')

    plt.xticks(idxs, labels=labels, rotation=90)
    plt.legend()
    plt.grid()
    plt.tight_layout()

    if(save_dir is not None):
        filename = f'5.simulations_plot_{field}.png'
        filepath = f'{save_dir}/{filename}'
        plt.savefig(filepath)

    if(plot):
        plt.show()

    return fig
