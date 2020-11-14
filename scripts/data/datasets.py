# -*- coding: utf-8 -*-

import torch
from torch.utils.data import Dataset, DataLoader

def data_to_tensor(data):
    return torch.Tensor(data.values)


class Training_Soccer_Dataset(Dataset):

    def __init__(self, train_data, window_size, train=False):

        self.x = {'home':train_data['home'].drop('f-WD', axis=1),
                  'away':train_data['away'].drop('f-WD', axis=1)}
        self.y = {'home':train_data['home']['f-WD'],
                  'away':train_data['away']['f-WD']}

        self.window_size = window_size
        self.train = train

        print(f'\t {self.x["home"].shape},{self.y["home"].shape}')

    def _to_tensor(self, data):
        return torch.Tensor(data.values)

    def __len__(self):
        if (self.train):
            return len(self.x) - self.window_size
        else:
            return len(self.x)

    def __getitem__(self, idx):
        if torch.is_tensor(idx):
            idx = idx.tolist()

        if (self.train):
            start, end = idx, idx + self.window_size
        else:
            start, end = idx, idx + 1

        x = data_to_tensor(self.x[start:end])
        y = data_to_tensor(self.y[start:end]) if self.y is not None else None

        if (y is not None):
            return x, y

        else:
            return x


class Soccer_Dataset(Dataset):
    
    def __init__(self, x, y=None, window_size=None, train=False):

        self.x = x
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
    
    def __init__(self, data, window_size, train=True):
        
        self.x_home = data['home'].drop('f-WD', axis=1)
        self.y_home = data['home']['f-WD']
        
        self.x_away = data['away'].drop('f-WD', axis=1)
        self.y_away = data['away']['f-WD']
        
        self.window_size = 0 if window_size is None else window_size
        
        self.train = train
        
        print(f'\t {self.x_home.shape},{self.y_home.shape} - {self.x_away.shape},{self.y_away.shape}')
        
    def _to_tensor(self, data):
        return torch.Tensor(data.values)
        
    def __len__(self):
        return len(self.x_home) - self.window_size

    def __getitem__(self, idx):
        if torch.is_tensor(idx):
            idx = idx.tolist()
            
        x_start, x_end = idx, idx+self.window_size-1
        y_start, y_end = idx+self.window_size-1, idx+self.window_size

        x_home = data_to_tensor(self.x_home[x_start:x_end])
        x_away = data_to_tensor(self.x_away[x_start:x_end])
        
        y_home = data_to_tensor(self.y_home[y_start:y_end])
        y_away = data_to_tensor(self.y_away[y_start:y_end])
        
        return x_home, y_home, x_away, y_away
  
def create_training_dataloader(input_data, params):
    
    window = int(params['window_size'])
    split_size = float(params['split_size'])
    
    train_size = int(split_size * len(input_data['home']))
    valid_size = len(input_data['home']) - train_size
    
    train_data, valid_data = {}, {}
    
    train_data['home'] = input_data['home'].iloc[: train_size]
    train_data['away'] = input_data['away'].iloc[: train_size]
    
    if(split_size == 1):
        split = 0.15
        valid_size = int(len(input_data['home']) * split)
        
        valid_data['home'] = input_data['home'].iloc[-valid_size : ]
        valid_data['away'] = input_data['away'].iloc[-valid_size : ]
        
    else:
        valid_data['home'] = input_data['home'].iloc[train_size : train_size+valid_size]
        valid_data['away'] = input_data['away'].iloc[train_size : train_size+valid_size]

    
    dataset = {'train':{},
               'eval':{}}
    
    if(params['dataset'] == 'base'):
        dataset_fn = Training_Soccer_Dataset
        print('> Creating Soccer Dataset')
    else:
        dataset_fn = Training_Soccer_Dataset
        
    # elif(params['dataset'] == 'windowed'):
    #     dataset_fn = Windowed_Soccer_Dataset
    #     print('> Creating Windowed Soccer Dataset')
        
    print('  > Training Set:')
    dataset['train'] = dataset_fn(train_data,
                                  window_size=window,
                                  train=True)

    print('  > Validation Set:')
    dataset['eval'] = dataset_fn(valid_data,
                                 window_size=window,
                                 train=False)


    dataloader = {x:DataLoader(dataset     = dataset[x],
                               batch_size  = int(params['batch_size']),
                               shuffle     = False,
                               num_workers = params['n_workers']
                               ) 
                               for x in ['train', 'eval']
                 }
    
    in_features = len(dataset['train'].x['home'].columns)
    
    return dataloader, in_features

def create_test_dataloader(test_data):

    test_dataset = {}

    for s in ['home', 'away']:
        x = test_data[s]
        y = None

        test_dataset[s] = Soccer_Dataset(x, y, window_size=None, train=False)
    
    test_dataloader = DataLoader(test_dataset,
                                 batch_size=1)
    
    return test_dataloader