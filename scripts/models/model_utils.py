# -*- coding: utf-8 -*-

from matplotlib import pyplot as plt
import os

from scripts.utils.utils import logger


def update_lr(model, lr):
    for param_group in model.optimizer.param_groups:
        param_group['lr'] = lr
        
    return

    
def save_evaluation(tpr, pos, total_matches, threshold, params):
    
    filename = '3.model_details.txt'
    filepath = f'{os.environ["CKP_MODEL_PATH"]}{params["name"]}/{filename}'
    
#    content = f'________________________ {params["name"]} ________________________\n\n'
    content = f'\n\n> Threshold: {threshold}\n'
    content += f'> Home TPR: {tpr["home"]:.3f} over {pos["home"]}/{total_matches} matches ({pos["home"]/(total_matches):.3f})\n'
    content += f'> Away TPR: {tpr["away"]:.3f} over {pos["away"]}/{total_matches} matches ({pos["away"]/(total_matches):.3f})\n'
    
    logger.info(f' > Saving evaluation test results at {filepath}')
    with open(filepath, 'a') as f:
        f.write(content)
        f.close()


def find_home_teams(decoded_testloader):
    
    home = decoded_testloader['home']
    away = decoded_testloader['away']
    
    home_h_teams = home[home['home'] == 1]
    home_a_teams = away[away['home'] == 1]
    
    home_teams = []
    home_teams.append(home_h_teams['team'].to_list())
    home_teams.append(home_a_teams['team'].to_list())
    
    return home_teams


    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    