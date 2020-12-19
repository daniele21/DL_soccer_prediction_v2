import torch
from torch.utils.data import DataLoader
from tqdm import tqdm
import sys
import numpy as np
import copy

from scripts.models.base import Base
from core.logger.logging import logger
from scripts.networks.lstm_networks import init_weights
from scripts.utils.saving import save_training_details
from scripts.visualization.plots import plot_loss


class Window_model(Base):

    def __init__(self, network, params, dataloader):
        super(Window_model, self).__init__(network, params, dataloader)

        self.window_size = params['window']

        self.trainloaders = [DataLoader(d,
                                       batch_size=d.batch_size,
                                       shuffle=False)  for d in self.trainloader]

        self.evalloaders = [DataLoader(d,
                                       batch_size=d.batch_size,
                                       shuffle=False) for d in self.evalloader]

        self.n_folds = len(self.trainloaders)

        self.fold_model = [copy.deepcopy(self.model) for i in range(self.n_folds)]
        self.optimizers = [params['optimizer'](model.parameters(),
                                               lr=params['lr']) for model in self.fold_model]
        self.fold_losses = []


    def _train_one_epoch(self):
        losses = []

        # TRAINING ONE EPOCH
        for x_home, x_away, y_home, y_away in self.trainloaders[self.i_fold]:

            x_home = torch.Tensor(x_home).to(self.device)
            x_away = torch.Tensor(x_away).to(self.device)

            target = torch.cat([y_home, y_away]).to(self.device)

            # FORWARDING
            output, home_out, away_out = self.fold_model[self.i_fold](x_home, x_away)

            # COMPUTING LOSS
            loss = self.loss_function(output, target)
            losses.append(loss.item())

            # OPTIMIZATION
            self.optimizers[self.i_fold].zero_grad()
            loss.backward()
            self.optimizers[self.i_fold].step()

        return np.mean(losses)

    def _evaluate(self):
        losses = []

        # EVALUATING ONE EPOCH
        for x_home, x_away, y_home, y_away in self.evalloaders[self.i_fold]:

            x_home = torch.Tensor(x_home).to(self.device)
            x_away = torch.Tensor(x_away).to(self.device)

            target = torch.cat([y_home, y_away]).to(self.device)

            # FORWARDING
            output, home_out, away_out = self.fold_model[self.i_fold](x_home, x_away)

            # COMPUTING LOSS
            loss = self.loss_function(output, target)
            losses.append(loss.item())

        return np.mean(losses)

    def walk_forward_train(self, epochs, patience=None):

        for i in tqdm(range(self.n_folds),
                      desc='> Folds  ',
                      file=sys.stdout):

            self.losses = {'train':[], 'eval':[]}
            self.epoch = 0
            self.i_fold = i

            self.train(epochs, patience)

            self.fold_losses.append(self.losses)

            save_training_details(self,
                                  save_dir=f'{self.save_dir}training_details/',
                                  filename=f'4-{i}.training_details')
            plot_loss(self.losses['train'],
                      self.losses['eval'],
                      save=self.save,
                      save_dir=f'{self.save_dir}plot/',
                      filename=f'plot_loss_{i}.png')

        return self.fold_losses

    def train(self, epochs, patience=None):
        super(Window_model, self).train(epochs, patience)

    def predict(self, input_data, field):
        model_name = str(field).lower()

        assert model_name == 'home' or model_name == 'away', 'ERROR - model predict: WRONG model name. Give "home" or "away"'

        preds = []
        for i_fold in range(self.n_folds):

            if (model_name == 'home'):
                logger.info('> Calling Home Network')
                field_model = self.fold_model[i_fold].home_network
            elif (model_name == 'away'):
                logger.info('> Calling Away Network')
                field_model = self.fold_model[i_fold].away_network
            else:
                raise ValueError('Model - predict: Wrong model name')

            logger.info('> Prediction')

            with torch.no_grad():

                for x in input_data:
                    x = torch.Tensor(x).to(self.device)
                    out = field_model(x)

                    out = out.squeeze()

                    preds.append(out.item())


        return np.mean(preds)