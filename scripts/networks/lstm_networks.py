# -*- coding: utf-8 -*-
import torch
import torch.nn as nn

class LSTM_Network(nn.Module):
    
    def __init__(self, name, in_features, params):
        super(LSTM_Network, self).__init__()
        self.name = name
        self.dataset_type = params['dataset']
        
        self.window = params['window']-1 if params['window'] is not None else None
        torch.manual_seed(params['seed'])
        
        out_features = params['out_lstm']
        self.lstm = nn.LSTM(input_size = in_features,
                            hidden_size= out_features,
                            num_layers = params['n_lstm_layer'],
                            bidirectional=params['bidirectional'])
            
        in_features = out_features * 2 if params['bidirectional'] else in_features
        
        out_features = in_features // 2
        self.dense = nn.Linear(in_features, out_features)
        self.dense_act = nn.ReLU()
        in_features = out_features
        
        out_features = 1
        self.fc = nn.Linear(in_features, out_features)
        self.fc_act = nn.Sigmoid()
        
    def forward(self, x):
        
        h_lstm, _ = self.lstm(x)
        
        h_dense = self.dense_act(self.dense(h_lstm))
        
        out = self.fc_act(self.fc(h_dense))
        # out = out.squeeze()

        return out


class LSTM_FCN_Network(nn.Module):

    def __init__(self, name, in_features, params):
        super(LSTM_FCN_Network, self).__init__()
        self.name = name
        self.dataset_type = params['dataset']

        self.window = params['window'] - 1 if params['window'] is not None else None
        torch.manual_seed(params['seed'])

        out_features = params['out_lstm']
        self.lstm = nn.LSTM(input_size=in_features,
                            hidden_size=out_features,
                            num_layers=params['n_lstm_layer'],
                            bidirectional=params['bidirectional'])


        in_features = out_features * 2 if params['bidirectional'] else in_features
        kernel = int(params['kernel'])
        n_conv_layers = int(params['conv_layers'])

        self.conv_layers = nn.Sequential()

        for i_layer in range(n_conv_layers - 1):
            out_features = in_features // 2
            self.conv_layers.add_module(f'Conv-1d-{i_layer+1}', nn.Conv1d(in_features,
                                                             out_features,
                                                             kernel_size=kernel))
            self.conv_layers.add_module(f'Relu-{i_layer}', nn.ReLU())
            in_features = out_features

        out_features = 1
        self.fc = nn.Conv1d(in_features,
                            out_features,
                            kernel_size=1)
        self.fc_act = nn.Sigmoid()

    def forward(self, x):

        h, _ = self.lstm(x)
        h = h.transpose(1,2)

        h = self.conv_layers(h)

        out = self.fc_act(self.fc(h))
        out = out.squeeze()

        return out


class LSTM_Soccer_Network_v1(nn.Module):
    
    def __init__(self, in_features, params):
        super(LSTM_Soccer_Network_v1, self).__init__()
        
        in_features = in_features          
        
        self.home_network = LSTM_Network('home', in_features, params)
        self.away_network = LSTM_Network('away', in_features, params)
        
    def forward(self, x_home, x_away):
        
        out_home = self.home_network(x_home)
        out_away = self.away_network(x_away)
        
        output = torch.cat([out_home, out_away])
        
        out_home = out_home.squeeze()
        out_away = out_away.squeeze()
        output = output.squeeze()
        
        return output, out_home, out_away


class LSTM_Soccer_Network_v2(nn.Module):

    def __init__(self, in_features, params):
        super(LSTM_Soccer_Network_v2, self).__init__()

        in_features = in_features

        self.home_network = LSTM_FCN_Network('home', in_features, params)
        self.away_network = LSTM_FCN_Network('away', in_features, params)

    def forward(self, x_home, x_away):
        out_home = self.home_network(x_home)
        out_away = self.away_network(x_away)

        output = torch.cat([out_home, out_away])

        return output, out_home, out_away


        
        
        
        
        
        
        
        
        
        
        
        
        
        