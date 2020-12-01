# -*- coding: utf-8 -*-
from scripts.utils.saving import save_soccer_model

def checkpoint(model):
    
    losses = model.losses
    
    if(len(losses['train']) > 1 and len(losses['eval']) > 1):
        last_train_loss = losses['train'][-2]
        curr_train_loss = losses['train'][-1]
        
        last_eval_loss = losses['eval'][-2]
        curr_eval_loss = losses['eval'][-1]
        
        if(last_train_loss > curr_train_loss and 
           last_eval_loss > curr_eval_loss):
            
            filepath = save_soccer_model(model) 
            return filepath
    else:
        filepath = save_soccer_model(model)
        return filepath
        
    return None


