# -*- coding: utf-8 -*-

import torch
from tqdm import tqdm
from time import time
import numpy as np
import sys

from core.file_manager.saving import save_json
from core.str2bool import str2bool
from scripts.models.model_utils import get_optimizer_from_name, get_loss_from_name, get_device_from_name
from scripts.visualization.plots import plot_loss
from scripts.utils.utils import spent_time, logger
from scripts.models.checkpoint import checkpoint
from scripts.visualization.tensorboard import tb_update_loss, writer

class Base_Model():
    
    def __init__(self, network, params, dataloader):
        
        self.name = params['name']
        self.device = get_device_from_name(params['device'])
        self.model = network.to(self.device)
        self.trainloader = dataloader['train']
        self.evalloader = dataloader['eval']
        # self.testloader = dataloader['test'] if 'test' in list(dataloader.keys()) else None
        
        self.optimizer = get_optimizer_from_name(params['optimizer'])(self.model.parameters(),
                                                                      lr=params['lr'])
        self.loss_function = get_loss_from_name(params['loss'])
        
        self.epoch = 0
        self.losses = {'train':[],
                       'eval':[]}

        # Visualization
        self.plot_type = params['plot_type'] if 'plot_type' in list(params.keys()) else 'pyplot'
        self.plot_freq = params['plot_freq'] if 'plot_freq' in list(params.keys()) else None

        self.seed = params['seed']
        
        self.save_dir = params['save_dir']
        self.static_dir = params['static_dir'] if 'static_dir' in list(params.keys()) else None
        self.save = True

        self.verbose = str2bool(params['verbose']) if 'verbose' in list(params.keys()) else True
        self.plot = str2bool(params['plot']) if 'plot' in list(params.keys()) else True

        # REPRODUCIBILITY
        np.random.seed(self.seed)
        torch.manual_seed(self.seed)

        # EARLY STOPPING
        self.es_patience = params['es_patience'] if 'es_patience' in list(params.keys()) else 0.005

        # PRODUCTION PARAMS
        self.production = str2bool(params['production'])
        self.stop_loss = float(params['stop_loss'])
        
    def _train_one_epoch(self):
        self.model.train()
        
        losses = []
        
        for x_home, x_away, y_home, y_away  in self.trainloader:
            
            x_home = torch.Tensor(x_home).to(self.device)
            x_away = torch.Tensor(x_away).to(self.device)
            
            target = torch.cat([y_home, y_away]).to(self.device)
            
            # FORWARDING
            output, home_out, away_out = self.model(x_home, x_away)
            
            # COMPUTING LOSS
            loss = self.loss_function(output, target)
            losses.append(loss.item())
            
            # OPTIMIZATION
            self.optimizer.zero_grad()
            loss.backward()
            self.optimizer.step()
            
        return np.mean(losses)
    
    def _evaluate(self):
        self.model.eval() 
        
        losses = []
        
        with torch.no_grad():
            
            for x_home, x_away, y_home, y_away  in self.evalloader:

                x_home = torch.Tensor(x_home).to(self.device)
                x_away = torch.Tensor(x_away).to(self.device)
                
                target = torch.cat([y_home, y_away]).to(self.device).squeeze()
                
                # FORWARDING
                output, home_out, away_out = self.model(x_home, x_away)
                
                # COMPUTING LOSS
                loss = self.loss_function(output, target)
                losses.append(loss.item())
            
        return np.mean(losses)  
       
    def train(self, epochs, patience=None):
        epochs = int(epochs)
        patience = int(patience)

        start_epoch = self.epoch
        end_epoch = self.epoch + epochs
        
        self.curr_patience = 0
        
        for epoch in tqdm(range(start_epoch, end_epoch), desc='> Epochs  '):
            
            # TRAINING STEP
            start = time()
            train_loss = self._train_one_epoch()
            
            self.losses['train'].append(train_loss)
            
            # EVALIUATION STEP
            eval_loss = self._evaluate()
            end = time()
            self.losses['eval'].append(eval_loss)

            if (self.verbose):
                self.print_epoch_result(start, end, train_loss, eval_loss, epoch, end_epoch)
            
            if(self.save):
                self.save_ckp()
                
            # EARLY STOPPING
            if(self.early_stopping(patience) and not self.production):
                break
                
            self.epoch += 1

            if(self.production_stop_loss(train_loss)):
                break

        plot_loss(self.losses['train'],
                  self.losses['eval'],
                  save=self.save,
                  save_dir=f'{self.save_dir}/',
                  plot=self.plot,
                  plot_dir=self.static_dir
                  )
        if(self.plot_type == 'tb'):
            writer.close()

        

    def predict(self, testloader, model_name=None):
        model_name = str(model_name).lower()

        assert model_name == 'home' or model_name == 'away', 'ERROR - model predict: WRONG model name. Give "home" or "away"'

        if(model_name == 'home'):
            # logger.info('> Calling Home Network')
            model = self.model.home_network
        elif(model_name == 'away'):
            # logger.info('> Calling Away Network')
            model = self.model.away_network
        else:
            raise ValueError('Model - predict: Wrong model name')

        pred = []

        with torch.no_grad():

            for x in testloader:
                x = torch.Tensor(x).to(self.device)
                out = model(x)

                out = out.squeeze()

                pred.append(out.item())

        return pred

    def production_stop_loss(self, train_loss):

        if(self.production):
            if(train_loss < self.stop_loss):
                return True
            else:
                return False
        else:
            return False

    def print_epoch_result(self, start, end, train_loss, eval_loss, epoch, end_epoch):
        print(f'\n> Epoch {epoch + 1}/{end_epoch}')
        print(f'> Time Spent:     {spent_time(start, end)}')
        print(f'> Training Loss:   {train_loss:.5f}')
        print(f'> Evaluation Loss: {eval_loss:.5f}')
        print('')

        # TENSORBOARD plot
        if (self.plot_type == 'tb'):
            tb_update_loss(train_loss, eval_loss, epoch)

        # PYPLOT plot
        if (epoch != 0 and self.plot_freq is not None and
                epoch % self.plot_freq == 0 and
                self.plot_type == 'pyplot'):
            plot_loss(self.losses['train'],
                      self.losses['eval'],
                      save=self.save,
                      save_dir=f'{self.save_dir}',
                      plot_dir=self.static_dir)

        loss_filepath = f'{self.static_dir}losses.json'
        save_json(self.losses, loss_filepath)

    def save_ckp(self):
        # CHECKPOINT
        #                best_ckp_path = None
        ckp_path = checkpoint(self) if not self.production else checkpoint(self, early_stopping=False)

        if (ckp_path is None):
            self.curr_patience += 1
            print(f'> Patience Updated: {self.curr_patience}')
        else:
            self.curr_patience = 0

    def early_stopping(self, patience):

        if (patience is not None and
                self.curr_patience >= patience and
                    self.epoch > 1):
            if(self.verbose):
                logger.info(' > Early Stopping: Patience Completed')
            stop = True
        else:
            stop = False

        return stop

    def get_losses(self):
        return {'train':self.losses['train'][-1],
                'eval':self.losses['eval'][-1]}, None






