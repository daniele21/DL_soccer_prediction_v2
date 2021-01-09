from torch.utils.data import DataLoader
import numpy as np
import torch
from tqdm import tqdm
from copy import deepcopy
from torch.multiprocessing import Process, set_start_method

from scripts.constants.configs import HOME, AWAY
from scripts.models.base import Base_Model
from scripts.models.model_utils import get_device_from_name
from scripts.utils.loading import load_model
from core.logger.logging import logger
from core.file_manager.saving import save_model, save_json


class K_fold_model():

    def __init__(self, network, params, dataloader):

        self.name = params['name']
        self.seed = params['seed']
        self.device = get_device_from_name(params['device'])
        self.n_folds = len(dataloader['train'])
        trainloaders = [DataLoader(d,
                                   batch_size=d.batch_size,
                                   shuffle=False)  for d in dataloader['train']]

        evalloaders = [DataLoader(d,
                                   batch_size=d.batch_size,
                                   shuffle=False) for d in dataloader['eval']]

        self.dataloaders = [{'train':trainloader, 'eval':evalloader}
                                    for trainloader, evalloader in zip(trainloaders, evalloaders)]


        self.models = [Base_Model(deepcopy(network), params, self.dataloaders[i]) for i in range(self.n_folds)]

        for i, model in enumerate(self.models):
            model.save_dir += f'fold_{i}/'

        self.save_dir = params['save_dir'] if 'save_dir' in list(params.keys()) else None

        # REPRODUCIBILITY
        np.random.seed(self.seed)
        torch.manual_seed(self.seed)

        # Dataset size
        last_train_event = trainloaders[-1].dataset.last_n_event()
        last_eval_event = evalloaders[-1].dataset.last_n_event()
        print(f'> Last Training Index: {last_train_event}')
        print(f'> Last Evaluation Index: {last_eval_event}')

    def train(self, epochs, patience=None):
        try:
            set_start_method('spawn')
        except RuntimeError:
            pass

        for model in tqdm(self.models, desc='> Folds '):
            p = Process(target=model.train, args=(epochs, patience))
            p.start()
            p.join()

        updated_models = []
        for model in self.models:
            ckp_model = f'{model.save_dir}{model.name}.pth'
            updated_models.append(load_model(ckp_model))

        self.models = updated_models

        if(self.save_dir is not None):
            filepath = f'{self.save_dir}{self.name}.pth'
            save_model(self, filepath)

            losses, mean_loss = self.get_losses()
            model_loss = {'losses':losses,
                          'mean_loss':mean_loss}
            filepath = f'{self.save_dir}losses.json'
            save_json(model_loss, filepath)

        return


    def predict(self, testloader, field=None):
        """
        Inference with all models, in a dict

        Args:
            testloader: dataloader containing the test data
            field:      type of match [HOME / AWAY]

        Returns:
            preds: dict{ KEY:   model number
                         VALUE: list of predictions}

        """
        model_name = str(field).lower()

        assert field == HOME or field == AWAY, 'ERROR - model predict: WRONG model name. Give "home" or "away"'

        preds = {}

        for i, model in enumerate(self.models):
            if (model_name == HOME):
                # logger.info('> Calling Home Network')
                field_net = model.model.home_network
            elif (model_name == AWAY):
                # logger.info('> Calling Away Network')
                field_net = model.model.away_network
            else:
                raise ValueError('Model - predict: Wrong model name')

            model_preds = []
            with torch.no_grad():

                for x in testloader:
                    x = torch.Tensor(x).to(self.device)
                    out = field_net(x)

                    out = out.squeeze()

                    model_preds.append(out.item())

            preds[i] = model_preds

        return preds


    def get_losses(self):
        losses = {'train':[],
                  'eval':[]}

        for model in self.models:
            losses['train'].append(model.losses['train'][-1])
            losses['eval'].append(model.losses['eval'][-1])

        mean_loss = {'train':np.mean(losses['train']),
                     'eval':np.mean(losses['eval'])}

        return losses, mean_loss
