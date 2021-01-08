# -*- coding: utf-8 -*-

import torch
from torch.utils.data import Dataset, DataLoader
import pandas as pd

from core.str2bool import str2bool
from scripts.constants.configs import BASE_DATASET, WINDOWED_DATASET, DEFAULT_TEST_SIZE, DEFAULT_EVAL_SIZE, FINAL_PHASE
from scripts.data.dataset_utils import windowed_dataset_split


def data_to_tensor(data):
    return torch.Tensor(data.values)


class Training_Soccer_Dataset(Dataset):

    def __init__(self, train_data, params, target_col='f-WD'):

        self.x = {'home':train_data['home'].drop(target_col, axis=1),
                  'away':train_data['away'].drop(target_col, axis=1)}
        self.y = {'home':train_data['home'][target_col],
                  'away':train_data['away'][target_col]}

        self.window_size = params['window_size']
        self.train = params['train']

        print(f'\t {self.x["home"].shape},{self.y["home"].shape}')

    def _to_tensor(self, data):
        return torch.Tensor(data.values)

    def __len__(self):
        if (self.train):
            return len(self.x['home']) - self.window_size
        else:
            return len(self.x['home'])

    def __getitem__(self, idx):
        if torch.is_tensor(idx):
            idx = idx.tolist()

        if (self.train):
            start, end = idx, idx + self.window_size
        else:
            start, end = idx, idx + 1

        x_home = data_to_tensor(self.x['home'][start:end])
        x_away = data_to_tensor(self.x['away'][start:end])

        y_home = data_to_tensor(self.y['home'][start:end])
        y_away = data_to_tensor(self.y['away'][start:end])

        return x_home, x_away, y_home, y_away

class Test_Soccer_Dataset(Dataset):

    def __init__(self, x):

        self.x = x

        print(f'\t {self.x.shape}')

    def _to_tensor(self, data):
        return torch.Tensor(data.values)

    def __len__(self):
        return len(self.x)

    def __getitem__(self, idx):
        if torch.is_tensor(idx):
            idx = idx.tolist()

        start, end = idx, idx + 1

        x = data_to_tensor(self.x[start:end])

        return x

class Soccer_Dataset(Dataset):
    
    def __init__(self, x,
                 y=None,
                 window_size=None,
                 train=False):

        self.x = x.drop('f-WD', axis=1)
        self.y = y
        self.window_size = window_size
        self.train = train

        if(train):
            assert y is not None, 'ERROR >> SOCCER DATASET: y value required'
            print(f'\t {self.x.shape},{self.y.shape}')

        else:
            print(f'\t {self.x.shape}')
        
    def _to_tensor(self, data):
        return torch.Tensor(data.values)
        
    def __len__(self):
        if(self.train):
            return len(self.x) - self.window_size
        else:
            return len(self.x)

    def __getitem__(self, idx):
        if torch.is_tensor(idx):
            idx = idx.tolist()
            
        if(self.train):
            start, end = idx, idx+self.window_size
        else:
            start, end = idx, idx+1    
            
        x = data_to_tensor(self.x[start:end])
        y = data_to_tensor(self.y[start:end]) if self.y is not None else None

        if(y is not None):
            return x, y
        
        else:
            return x

class Windowed_Soccer_Dataset(Dataset):

    def __init__(self, data, params, target_col='f-WD'):

        max_length = min(len(data['home']), len(data['away']))
        data = {'home':data['home'].iloc[:max_length],
                'away': data['away'].iloc[:max_length]}

        self.x = {'home':data['home'].drop(target_col, axis=1),
                  'away':data['away'].drop(target_col, axis=1)}
        self.y = {'home':data['home'][target_col],
                  'away':data['away'][target_col]}

        self.batch_size = params['batch_size']

    def _to_tensor(self, data):
        return torch.Tensor(data.values)

    def last_n_event(self):
        if(len(self.x['home']) > 0):
            return list(self.x['home'].index)[-1]
        else:
            return 0

    def __len__(self):
        return len(self.x['home'])

    def __getitem__(self, idx):
        if torch.is_tensor(idx):
            idx = idx.tolist()

        x_home = data_to_tensor(self.x['home'])
        x_away = data_to_tensor(self.x['away'])

        y_home = data_to_tensor(self.y['home'])
        y_away = data_to_tensor(self.y['away'])

        return x_home, x_away, y_home, y_away

def create_training_dataloader(input_data, params):

    if(params['dataset'] == BASE_DATASET):
        dataset = base_dataset(input_data, params)
        batch_size = int(params['batch_size'])

    elif(params['dataset'] == WINDOWED_DATASET):
        dataset = windowed_dataset(input_data, params)
        in_feature = len(dataset['train'][0].x['home'].columns)

        return dataset, in_feature

    else:
        dataset = base_dataset(input_data, params)
        batch_size = int(params['batch_size'])


    dataloader = {x:DataLoader(dataset     = dataset[x],
                               batch_size  = batch_size,
                               shuffle     = False,
                               ) 
                               for x in ['train', 'eval']
                 }
    
    in_features = len(dataset['train'].x['home'].columns)

    # if test_size > 0:
    #     print('  > Test Set:')
    #     dataloader['test'] = {}
    #     dataloader['test']['home'] = create_test_dataloader(test_data['home'])
    #     dataloader['test']['away'] = create_test_dataloader(test_data['away'])
    
    return dataloader, in_features

def windowed_dataset(data, params):
    if('active' in list(params.keys()) and 'phase' in list(params.keys())):
        production = str2bool(params['active']) and params['phase'] == FINAL_PHASE
    else:
        production = False

    train_params = {'train': True,
                    'batch_size': params['batch_size']}
    eval_params = {**train_params}
    eval_params['train'] = False

    test_size = params['test_size'] if 'test_size' in list(params.keys()) else DEFAULT_TEST_SIZE
    data_slice = slice(-test_size) if test_size >0 else slice(None)

    data_size = len(data['home'])
    splitter = windowed_dataset_split(data_size, params)
    n_folds = splitter.get_n_splits()

    train_set_folds = {'home':[],
                       'away':[]}
    eval_set_folds = {'home': [],
                      'away': []}

    for field in ['home', 'away']:
        i_fold = 1
        data[field] = data[field].iloc[data_slice]
        for train_index, eval_index in splitter.split(data[field]):
            if(production and i_fold==n_folds):
                train_slice, eval_slice = slice(train_index[0], None), slice(0)
            else:
                train_slice, eval_slice = slice(train_index[0], train_index[-1]), \
                                          slice(eval_index[0], eval_index[-1])

            train_set = data[field].iloc[train_slice]
            eval_set = data[field].iloc[eval_slice]

            train_set_folds[field].append(train_set)
            eval_set_folds[field].append(eval_set)

            i_fold += 1

    dataset = {'train': [],
               'eval': []}

    for i in range(n_folds):
        train_home, train_away = train_set_folds['home'][i], train_set_folds['away'][i]
        eval_home, eval_away = eval_set_folds['home'][i], eval_set_folds['away'][i]

        train_data = {'home': train_home,
                      'away': train_away}

        eval_data = {'home': eval_home,
                     'away': eval_away}

        train_dataset = Windowed_Soccer_Dataset(train_data, train_params)
        eval_dataset = Windowed_Soccer_Dataset(eval_data, eval_params)

        dataset['train'].append(train_dataset)
        dataset['eval'].append(eval_dataset)

    return dataset

def base_dataset(data, params):
    window = int(params['window_size'])
    split_size = float(params['split_size'])
    test_size = int(params['test_size']) if 'test_size' in list(params.keys()) else DEFAULT_TEST_SIZE

    train_size = int(split_size * (len(data['home']) - test_size))
    valid_size = (len(data['home']) - train_size - test_size)

    train_data, valid_data, test_data = {}, {}, {}

    train_data['home'] = data['home'].iloc[: train_size]
    train_data['away'] = data['away'].iloc[: train_size]

    if (split_size == 1):

        valid_data['home'] = pd.DataFrame()
        valid_data['away'] = pd.DataFrame()

    else:
        valid_data['home'] = data['home'].iloc[train_size: train_size + valid_size]
        valid_data['away'] = data['away'].iloc[train_size: train_size + valid_size]

        # test_data['home'] = data['home'].iloc[train_size + valid_size:] if test_size > 0 else None
        # test_data['away'] = data['away'].iloc[train_size + valid_size:] if test_size > 0 else None

    train_params = {'train': True,
                    'window_size': window}
    eval_params = train_params

    dataset = {}
    dataset['train'] = Training_Soccer_Dataset(train_data, train_params)
    dataset['eval'] = Training_Soccer_Dataset(valid_data, eval_params)

    return dataset

def create_test_dataloader(test_data):
    print('> Test Set:')
    test_dataset = Test_Soccer_Dataset(test_data)

    test_dataloader = DataLoader(test_dataset,
                                 batch_size=1)
    
    return test_dataloader