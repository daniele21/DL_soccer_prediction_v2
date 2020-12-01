# -*- coding: utf-8 -*-
import torch.nn as nn


def cat_cross_entropy_loss():
    return nn.CrossEntropyLoss()

def binary_cross_entropy():
    return nn.BCELoss()

def mse():
    return nn.MSELoss()