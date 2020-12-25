# -*- coding: utf-8 -*-
from scripts.constants.configs import ADAM_OPTIMIZER, BCE_LOSS, CUDA_DEVICE, CPU_DEVICE, BASE_DATASET, WINDOWED_DATASET

import torch
from scripts.models.loss import binary_cross_entropy


def update_lr(model, lr):
    for param_group in model.optimizer.param_groups:
        param_group['lr'] = lr
        
    return


def get_optimizer_from_name(optim_name):

    if(optim_name == ADAM_OPTIMIZER):
        return torch.optim.Adam

    else:
        raise ValueError(f'Optimizer not found: {optim_name}')

def get_loss_from_name(loss_name):

    if(loss_name == BCE_LOSS):
        return binary_cross_entropy()

    else:
        raise ValueError(f'Loss function not found: {loss_name}')

def get_device_from_name(device_name):

    if(device_name == CUDA_DEVICE):
        return torch.device('cuda:0')
    elif(device_name == CPU_DEVICE):
        return torch.device('cpu:0')
    else:
        raise ValueError(f'Device not found: {device_name}')

    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    