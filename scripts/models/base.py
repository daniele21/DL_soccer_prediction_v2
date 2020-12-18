# -*- coding: utf-8 -*-

import torch
from tqdm import tqdm
from time import time
import numpy as np
import sys

from scripts.visualization.plots import plot_loss
from scripts.utils.utils import spent_time, logger
from scripts.models.checkpoint import checkpoint
from scripts.visualization.tensorboard import tb_update_loss, writer

class Base():

    def __init__(self, network, params, dataloader):

        self.name = params['name']
        self.device = params['device']
        self.model = network.to(self.device)
        self.trainloader = dataloader['train']
        self.evalloader = dataloader['eval']
        self.testloader = dataloader['test'] if 'test' in list(dataloader.keys()) else None

        self.optimizer = params['optimizer'](self.model.parameters(),
                                             lr=params['lr'])
        self.loss_function = params['loss']

        self.epoch = 0
        self.losses = {'train': [],
                       'eval': []}

        # Visualization
        self.plot_type = params['plot_type'] if 'plot_type' in list(params.keys()) else 'pyplot'
        self.plot_freq = params['plot_freq']

        self.seed = params['seed']

        self.save_dir = params['save_dir']
        self.save = True if self.save_dir is not None else False

        # REPRODUCIBILITY
        np.random.seed(self.seed)
        torch.manual_seed(self.seed)

    def _train_one_epoch(self):
        pass

    def _evaluate(self):
        pass

    def train(self, epochs, patience=None):
        start_epoch = self.epoch
        end_epoch = self.epoch + epochs

        curr_patience = 0

        for epoch in range(start_epoch, end_epoch):

            print(f'\n> Epoch {epoch + 1}/{end_epoch}')

            # TRAINING STEP
            start = time()
            train_loss = self._train_one_epoch()

            self.losses['train'].append(train_loss)

            # EVALIUATION STEP
            eval_loss = self._evaluate()
            end = time()
            self.losses['eval'].append(eval_loss)

            print(f'> Time Spent:     {spent_time(start, end)}')
            print(f'> Training Loss:   {train_loss:.5f}')
            print(f'> Evaluation Loss: {eval_loss:.5f}')
            print('')

            # TENSORBOARD plot
            if (self.plot_type == 'tb'):
                tb_update_loss(train_loss, eval_loss, epoch)

            # PYPLOT plot
            if (epoch != 0 and
                    epoch % self.plot_freq == 0 and
                    self.plot_type == 'pyplot'):
                plot_loss(self.losses['train'],
                          self.losses['eval'],
                          save=self.save,
                          save_dir=f'{self.save_dir}')

            if (self.save):
                # CHECKPOINT
                ckp_path = checkpoint(self)

                if (ckp_path is None):
                    curr_patience += 1
                    print(f'> Patience Updated: {curr_patience}')
                else:
                    curr_patience = 0
            #                print(f'> Patience Updated: {curr_patience}')
            #                    best_ckp_path = ckp_path

            # EARLY STOPPING
            if (patience is not None and curr_patience >= patience):
                logger.info(' > Early Stopping: Patience Completed')
                break

            self.epoch += 1

        plot_loss(self.losses['train'],
                  self.losses['eval'],
                  save=self.save,
                  save_dir=f'{self.save_dir}/'
                  )
        if (self.plot_type == 'tb'):
            writer.close()

    def predict(self, input_data, field):
        pass


class Base_Model():
    
    def __init__(self, network, params, dataloader):
        
        self.name = params['name']
        self.device = params['device']
        self.model = network.to(self.device)
        self.trainloader = dataloader['train']
        self.evalloader = dataloader['eval']
        self.testloader = dataloader['test'] if 'test' in list(dataloader.keys()) else None
        
        self.optimizer = params['optimizer'](self.model.parameters(),
                                             lr=params['lr'])
        self.loss_function = params['loss']
        
        self.epoch = 0
        self.losses = {'train':[],
                       'eval':[]}

        # Visualization
        self.plot_type = params['plot_type'] if 'plot_type' in list(params.keys()) else 'pyplot'
        self.plot_freq = params['plot_freq']

        self.seed = params['seed']
        
        self.save_dir = params['save_dir']
        self.save = True
        
        # REPRODUCIBILITY
        np.random.seed(self.seed)
        torch.manual_seed(self.seed)
        
    def _train_one_epoch(self):
        self.model.train()
        
        losses = []
        
        for x_home, x_away, y_home, y_away  in tqdm(self.trainloader,
                                                    desc='> Training  \t',
                                                    file=sys.stdout):
            
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
            
            for x_home, x_away, y_home, y_away  in tqdm(self.evalloader,
                                                        desc='> Evaluation\t',
                                                        file=sys.stdout):
                
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
        
        start_epoch = self.epoch
        end_epoch = self.epoch + epochs
        
        curr_patience = 0
        
        for epoch in range(start_epoch, end_epoch):
            
            print(f'\n> Epoch {epoch+1}/{end_epoch}')
            
            # TRAINING STEP
            start = time()
            train_loss = self._train_one_epoch()
            
            self.losses['train'].append(train_loss)
            
            # EVALIUATION STEP
            eval_loss = self._evaluate()
            end = time()
            self.losses['eval'].append(eval_loss)
            
            
            print(f'> Time Spent:      {spent_time(start, end)}')
            print(f'> Training Loss:   {train_loss:.5f}')
            print(f'> Evaluation Loss: {eval_loss:.5f}')
            print('')

            # TENSORBOARD plot
            if (self.plot_type == 'tb'):
                tb_update_loss(train_loss, eval_loss, epoch)

            # PYPLOT plot
            if(epoch != 0 and
               epoch % self.plot_freq == 0 and
               self.plot_type == 'pyplot'):

                plot_loss(self.losses['train'],
                          self.losses['eval'],
                          save=self.save,
                          save_dir=f'{self.save_dir}')
            
            if(self.save):
                # CHECKPOINT
#                best_ckp_path = None
                ckp_path = checkpoint(self)
                
                if(ckp_path is None):
                    curr_patience += 1
                    print(f'> Patience Updated: {curr_patience}')
                else:
                    curr_patience = 0
    #                print(f'> Patience Updated: {curr_patience}')
#                    best_ckp_path = ckp_path    
                
            # EARLY STOPPING
            if(patience is not None and curr_patience >= patience):
                logger.info(' > Early Stopping: Patience Completed')
                break
                
            self.epoch += 1


        plot_loss(self.losses['train'],
                  self.losses['eval'],
                  save=self.save,
                  save_dir=f'{self.save_dir}/'
                  )
        if(self.plot_type == 'tb'):
            writer.close()

        

    def predict(self, testloader, model_name=None):
        model_name = str(model_name).lower()

        assert model_name == 'home' or model_name == 'away', 'ERROR - model predict: WRONG model name. Give "home" or "away"'

        if(model_name == 'home'):
            logger.info('> Calling Home Network')
            model = self.model.home_network
        elif(model_name == 'away'):
            logger.info('> Calling Away Network')
            model = self.model.away_network
        else:
            raise ValueError('Model - predict: Wrong model name')

        pred = []
        logger.info('> Prediction')

        with torch.no_grad():

            for x in testloader:
                x = torch.Tensor(x).to(self.device)
                out = model(x)

                out = out.squeeze()

                pred.append(out.item())

        return pred










