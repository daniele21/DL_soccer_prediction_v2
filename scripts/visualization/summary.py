import pandas as pd


def show_summary(summary):

    config = summary['config']
    outcome = summary['outcome']
    reward = summary['reward']
    reward_perc = summary['reward_perc']

    print('---------- Summary ----------')
    print('')
    print('> Config:')
    print('>')
    print(f'> Field:            {config["field"]}')
    print(f'> Test size:        {config["test_size"]}')
    print(f'> Threshold:        {config["thr"]}')
    print(f'> filter bet:       {config["filter_bet"]}')
    print(f'> Bet per match:    {config["bet_money"]} €')
    print('')
    print('> Outcome:')
    print('>')
    print(f'> Support:   {outcome["support"]}')
    print(f'> TPR:       {outcome["tpr"]}')
    print(f'> Matches:   {outcome["matches"]}')
    print(f'> Wins:      {outcome["wins"]}')
    print(f'> Losses:    {outcome["losses"]}')
    print('')
    print('> Reward:')
    print('>')
    print(f'> Gain:       {reward["gain"]:.2f} \t({reward_perc["gain"]*100:.1f} %)')

    i = 2
    for key in reward:
        if('combo' in key):
            print(f'> Combo x{i}:   {reward[key]:.2f}  \t({reward_perc[key] * 100:.1f} %)')
            i += 1

def summary_dataframe(summary):

    config = summary['config']
    outcome = summary['outcome']
    # reward = summary['reward']
    reward_perc = summary['reward_perc']

    summary_dict = {}
    for key in config:
        summary_dict[key] = config[key]
    for key in outcome:
        summary_dict[key] = outcome[key]
    for key in reward_perc:
        summary_dict[key] = reward_perc[key]

    return pd.DataFrame(summary_dict, index=[0])




