# -*- coding: utf-8 -*-
from scripts.utils.saving import save_soccer_model

def checkpoint(model, early_stopping=True):
    
    losses = model.losses
    patience_rate = model.es_patience

    if(len(losses['train']) > 1 and len(losses['eval']) > 1 and early_stopping):
        last_train_loss = losses['train'][-2]
        curr_train_loss = losses['train'][-1]
        train_loss_diff = curr_train_loss - last_train_loss

        # try:
        #     last_five_eval_loss = losses['eval'][-6]
        #     last_three_eval_loss = losses['eval'][-4]
        # except:
        #     last_five_eval_loss = 10000
        #     last_three_eval_loss = 10000

        last_eval_loss = losses['eval'][-2]
        curr_eval_loss = losses['eval'][-1]
        eval_loss_diff = curr_eval_loss - last_eval_loss

        if(last_train_loss > curr_train_loss and
           last_eval_loss > curr_eval_loss):

            filepath = save_soccer_model(model)
            return filepath
        # else:
            # if (train_loss_diff < last_train_loss * patience_rate and
            #         eval_loss_diff < last_eval_loss * patience_rate and
            #         curr_eval_loss - last_three_eval_loss < last_three_eval_loss * patience_rate and
            #         curr_eval_loss - last_five_eval_loss < last_five_eval_loss * patience_rate
            #     ):

                # filepath = save_soccer_model(model)
                # return filepath
    else:
        filepath = save_soccer_model(model)
        return filepath
        
    return None


