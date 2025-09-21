import math
import argparse
import numpy as np

import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
from torchvision import datasets, transforms
from tqdm import tqdm
from blitz.modules import BayesianEGRU
from blitz.utils import variational_estimator

import matplotlib.pyplot as plt
from collections import deque

def bitreversal_po2(n):
    m = int(math.log(n) / math.log(2))
    perm = np.arange(n).reshape(n, 1)
    for i in range(m):
        n1 = perm.shape[0] // 2
        perm = np.hstack((perm[:n1], perm[n1:]))
    return perm.squeeze(0)


def bitreversal_permutation(n):
    m = int(math.ceil(math.log(n) / math.log(2)))
    N = 1 << m
    perm = bitreversal_po2(N)
    return np.extract(perm < n, perm)

def sequential_MNIST(batch_size, cuda, data_path, permute=False):
    validation_test_batch_size = batch_size
    kwargs = {'num_workers': 1, 'pin_memory': True} if cuda else {}

    transforms_list = [
        transforms.ToTensor(),
        # transforms.Resize(size=(14, 14)),
        transforms.Lambda(lambda x: x.view(-1, 1))
    ]

    if permute:
        print("Permuting pixels!")
        permutation = bitreversal_permutation(28 * 28)
        transforms_list.append(transforms.Lambda(lambda x: x[permutation]))

    full_train_set = datasets.MNIST(
        data_path, train=True, download=True, transform=transforms.Compose(transforms_list))

    # use 20% of training data for validation
    train_set_size = int(len(full_train_set) * 0.8)
    valid_set_size = len(full_train_set) - train_set_size

    # split the train set into two
    seed = torch.Generator().manual_seed(42)
    train_set, val_set = torch.utils.data.random_split(
        full_train_set, [train_set_size, valid_set_size], generator=seed)

    train_loader = torch.utils.data.DataLoader(
        train_set, batch_size=batch_size, shuffle=True, **kwargs)
    validation_loader = torch.utils.data.DataLoader(val_set, batch_size=validation_test_batch_size, shuffle=True,
                                                    # drop_last=True,
                                                    **kwargs)

    test_loader = torch.utils.data.DataLoader(
        datasets.MNIST(data_path, train=False,
                       transform=transforms.Compose(transforms_list)),
        batch_size=validation_test_batch_size, shuffle=False,
        # drop_last=True,
        **kwargs)

    return train_loader, validation_loader, test_loader

def get_args():
    argparser = argparse.ArgumentParser()
    argparser.add_argument('--seed', type=int, default=3000)
    argparser.add_argument('--resume', type=str)
    argparser.add_argument('--data-path',default='.',type=str)

    argparser.add_argument('--permute', action='store_true')

    argparser.add_argument('--batch-size', type=int, default=256)
    argparser.add_argument('--learning-rate', type=float, default=0.001)
    argparser.add_argument('--zoneout', type=float, default=0.)
    argparser.add_argument('--dropout-connect', type=float, default=0.)
    argparser.add_argument('--dropout-forward', type=float, default=0.)
    argparser.add_argument('--use-rmsprop', action='store_true')
    argparser.add_argument('--learning-rate-decay', action='store_true')
    argparser.add_argument('--use-grad-clipping', action='store_true')
    argparser.add_argument('--grad-clip-norm', type=float, default=2.0)

    argparser.add_argument('--units', type=int, default=256)
    argparser.add_argument('--layers', type=int, default=1)
    argparser.add_argument('--train-epochs', type=int, default=200)
    
    #bayesian_hyperparameters
    argparser.add_argument(
        '--prior-sigma-1', type=float, default=1.)
    argparser.add_argument(
        '--prior-pi', type=float, default=1.)
    argparser.add_argument(
        '--posterior-rho-init', type=float, default=-3.)

    argparser.add_argument('--voltage-regularization', action='store_true')
    argparser.add_argument(
        '--voltage-regularization-constant', type=float, default=1.)
    argparser.add_argument(
        '--voltage-regularization-target', type=float, default=-0.9)

    argparser.add_argument('--activity-regularization', action='store_true')
    argparser.add_argument(
        '--activity-regularization-constant', type=float, default=1.)
    argparser.add_argument(
        '--activity-regularization-target', type=float, default=0.05)

    argparser.add_argument('--pseudo-derivative-width', type=float, default=1.)

    args = argparser.parse_args()
    return args

def main():
    args = get_args()
    cuda = torch.cuda.is_available()
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    training_data, validation_data,testing_data = sequential_MNIST(args.batch_size,cuda,args.data_path,permute=args.permute)
    #Model definiton
    # @variational_estimator
    # class NN(nn.Module):
    #     def __init__(self,layers,units,prior_sigma_1,prior_pi,posterior_rho_init):
    #         super(NN, self).__init__()
    #         self.layers= layers
    #         self.layers = []
    #         for layers in range(layers):
    #             if layers==0:
    #                 self.layers.append(BayesianEGRU(
    #                     in_features=1,              
    #                     out_features=units,            
    #                     prior_sigma_1=prior_sigma_1,            
    #                     prior_pi=prior_pi,                 
    #                     posterior_rho_init=posterior_rho_init     
    #                 ))
    #             else:
    #                 self.layers.append(BayesianEGRU(
    #                     in_features=units,           
    #                     out_features=units,
    #                     prior_sigma_1=prior_sigma_1,         
    #                     prior_pi=prior_pi,                 
    #                     posterior_rho_init=posterior_rho_init     
    #                 ))
    #         self.linear = nn.Linear(units, 10)

    #     def forward(self, x, hidden_states=None, sharpen_loss=None):
    #         for layer in self.layers:
    #             x,_ = layer(x,hidden_states,sharpen_loss)
    #         x_ = x_[:, -1, :]
    #         x_ = self.linear(x_)
    #         return x_
    # model = NN(layers=args.layers,units=args.units,prior_sigma_1=args.prior_sigma_1,
    #            prior_pi=args.prior_pi,
    #            posterior_rho_init=args.posterior_rho_init)
    # model = model.to(device)
    @variational_estimator
    class NN(nn.Module):
        def __init__(self,n_units):
            super(NN, self).__init__()
            self.n_units = n_units
            self.egru_1 = BayesianEGRU(
                in_features=1,              
                out_features=n_units,            
                prior_sigma_1=1,            
                prior_pi=1,                 
                posterior_rho_init=-3.0     
            )
            self.linear = nn.Linear(self.n_units, 10)

        def forward(self, x, hidden_states=None, sharpen_loss=None):
            x_, _ = self.egru_1(x, hidden_states, sharpen_loss)
            x_ = x_[:, -1, :]
            x_ = self.linear(x_)
            return x_

    model = NN(n_units=args.units)
    model.to(device)


    #Optmizerf
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=args.learning_rate)
    #Traing
    training_data = tqdm(training_data)
    model.train()
    for epoch in range(args.train_epochs):
        for current_batch, (inputs, targets) in enumerate(training_data):
            inputs = inputs.to(device)
            targets = targets.to(device)
            optimizer.zero_grad()  # Clear previous gradients

            # Forward pass using sample_elbo (provided by @variational_estimator)
            loss = model.sample_elbo(
                inputs=inputs,
                labels=targets,
                criterion=criterion,
                sample_nbr=3,  # Number of Monte Carlo samples #FIXME: hardcode
                complexity_cost_weight=1 / 50000 #FIXME: hardcode
            )
            loss.backward()  # Backward pass to compute gradients
            optimizer.step()  # Update weights
            
        #TODO: validation and test
            # VALIDATION
        model.eval()
        with torch.no_grad():
            loss, success_rate = 0., 0.
            validation_data = tqdm(validation_data)
            for current_batch, (inputs, targets) in enumerate(validation_data):
                torch.cuda.empty_cache()
                inputs = inputs.to(device)
                targets = targets.to(device)
                actual_output = model(inputs)
                actual_output = torch.argmax(actual_output, -1)
                success_rate_ = (actual_output == targets).float().mean()
                success_rate += success_rate_

        success_rate_ = success_rate.data.item() / (current_batch + 1)

        print(f"Validation in {epoch} :: \nSuccess rate {success_rate_:.4f}")
    
if __name__ == '__main__':
    main()
    