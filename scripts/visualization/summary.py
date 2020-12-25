import pandas as pd


def show_summary(summary):

    config = summary['config']
    outcome = summary['outcome']
    reward = summary['reward']
    reward_perc = summary['reward_perc']

    result_str = '---------- Summary ----------' + '\n\n'
    result_str += f'> Field:            {config["field"]}' + '\n'
    result_str += f'> Test size:        {config["test_size"]}' + '\n'
    result_str += f'> Threshold:        {config["thr"]}' + '\n'
    result_str += f'> Filter bet:       {config["filter_bet"]}' + '\n'
    result_str += f'> Bet per match:    {config["bet_money"]} €' + '\n\n'
    result_str += f'> Support:   {outcome["support"]}' + '\n'
    result_str += f'> TPR:       {outcome["tpr"]}' + '\n'
    result_str += f'> Matches:   {outcome["matches"]}' + '\n'
    result_str += f'> Wins:      {outcome["wins"]}' + '\n'
    result_str += f'> Losses:    {outcome["losses"]}' + '\n\n'
    result_str += f'> Gain:       {reward["gain"]:.2f} \t({reward_perc["gain"]*100:.1f} %)' + '\n'
    i = 2
    for key in reward:
        if('combo' in key):
            result_str += f'> Combo x{i}:   {reward[key]:.2f}  \t({reward_perc[key] * 100:.1f} %)' + '\n'
            i += 1

    # print('---------- Summary ----------')
    # print('')
    # print('> Config:')
    # print('>')
    # print(f'> Field:            {config["field"]}')
    # print(f'> Test size:        {config["test_size"]}')
    # print(f'> Threshold:        {config["thr"]}')
    # print(f'> filter bet:       {config["filter_bet"]}')
    # print(f'> Bet per match:    {config["bet_money"]} €')
    # print('')
    # print('> Outcome:')
    # print('>')
    # print(f'> Support:   {outcome["support"]}')
    # print(f'> TPR:       {outcome["tpr"]}')
    # print(f'> Matches:   {outcome["matches"]}')
    # print(f'> Wins:      {outcome["wins"]}')
    # print(f'> Losses:    {outcome["losses"]}')
    # print('')
    # print('> Reward:')
    # print('>')
    # print(f'> Gain:       {reward["gain"]:.2f} \t({reward_perc["gain"]*100:.1f} %)')
    #
    # i = 2
    # for key in reward:
    #     if('combo' in key):
    #         print(f'> Combo x{i}:   {reward[key]:.2f}  \t({reward_perc[key] * 100:.1f} %)')
    #         i += 1

    print(result_str)

    return result_str

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




