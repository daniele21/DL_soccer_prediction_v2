import torch
from torch.utils.data import DataLoader
from tqdm import tqdm
import sys
import numpy as np

from scripts.models.base import Base
from core.logger.logging import logger

class Window_model(Base):

    def __init__(self, network, params, dataloader):
        super(Window_model, self).__init__(network, params, dataloader)

        self.window_size = params['window']

    def _train_one_fold(self, trainloader, n_fold):
        losses = []

        # TRAINING ONE FOLD
        for x_home, x_away, y_home, y_away in trainloader:

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

    def _train_one_epoch(self):
        self.model.train()

        losses = []
        n_fold = 0

        # WALKING FORWARD TRAINING - TRAINING FOR EACH FOLD
        for dataset in tqdm(self.trainloader, desc='> Training  \t', file=sys.stdout):
            n_fold += 1
            dataloader = DataLoader(dataset,
                                   batch_size=dataset.batch_size,
                                   shuffle=False,
                                   )

            # TRAINING ONE FOLD
            mean_loss = self._train_one_fold(dataloader, n_fold)
            losses.append(mean_loss)

        return np.mean(losses)

    def _eval_one_fold(self, evalloader, n_fold):
        losses = []

        # EVALUATING ONE FOLD
        for x_home, x_away, y_home, y_away in evalloader:

            x_home = torch.Tensor(x_home).to(self.device)
            x_away = torch.Tensor(x_away).to(self.device)

            target = torch.cat([y_home, y_away]).to(self.device)

            # FORWARDING
            output, home_out, away_out = self.model(x_home, x_away)

            # COMPUTING LOSS
            loss = self.loss_function(output, target)
            losses.append(loss.item())

        return np.mean(losses)


    def _evaluate(self):
        self.model.eval()

        losses = []
        n_fold = 0

        with torch.no_grad():

            # WALKING FORWARD TRAINING - EVALUATING FOR EACH FOLD
            for dataset in tqdm(self.evalloader, desc='> Evaluation  \t', file=sys.stdout):
                n_fold += 1
                dataloader = DataLoader(dataset,
                                        batch_size=dataset.batch_size,
                                        shuffle=False,
                                        )

                # TRAINING ONE FOLD
                mean_loss = self._eval_one_fold(dataloader, n_fold)
                losses.append(mean_loss)

        return np.mean(losses)

    def train(self, epochs, patience=None):
        super(Window_model, self).train(epochs, patience)

    def predict(self, input_data, field):
        model_name = str(field).lower()

        assert model_name == 'home' or model_name == 'away', 'ERROR - model predict: WRONG model name. Give "home" or "away"'

        if (model_name == 'home'):
            logger.info('> Calling Home Network')
            model = self.model.home_network
        elif (model_name == 'away'):
            logger.info('> Calling Away Network')
            model = self.model.away_network
        else:
            raise ValueError('Model - predict: Wrong model name')

        pred = []
        logger.info('> Prediction')

        with torch.no_grad():

            for x in input_data:
                x = torch.Tensor(x).to(self.device)
                out = model(x)

                out = out.squeeze()

                pred.append(out.item())

        return pred