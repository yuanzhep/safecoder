import os
import argparse
from datetime import datetime
from collections import defaultdict
from datetime import datetime
from pathlib import Path
import pprint
from torch import optim
import torch.nn as nn

word_emb_path = '/yz/SC/data/0102log.txt'
assert(word_emb_path is not None)

username = Path.home().name
project_dir = Path(__file__).resolve().parent.parent
sdk_dir = project_dir.joinpath('iemocap')
data_dir = project_dir.joinpath('datasets')
data_dict = {'iemocap6': data_dir.joinpath('iemocap6'), 'iemocap4': data_dir.joinpath(
    'iemoca4p'), 'ur_funny': data_dir.joinpath('UR_FUNNY')}
optimizer_dict = {'RMSprop': optim.RMSprop, 'Adam': optim.Adam, 'SGD': optim.SGD}
activation_dict = {'elu': nn.ELU, "hardshrink": nn.Hardshrink, "hardtanh": nn.Hardtanh,
                   "leakyrelu": nn.LeakyReLU, "prelu": nn.PReLU, "relu": nn.ReLU, "rrelu": nn.RReLU,
                   "tanh": nn.Tanh}

criterion_dict = {
    'iemocap': 'CrossEntropyLoss',
    'ur_funny': 'CrossEntropyLoss'
}

def get_args():
    parser = argparse.ArgumentParser(description='iemocap Sentiment Analysis')
    parser.add_argument('-f', default='', type=str)

    # Tasks
    parser.add_argument('--dataset', type=str, default='iemocap6', choices=['iemocap4','iemocap6'],
                        help='dataset to use (default: iemocap6)')
    parser.add_argument('--data_path', type=str, default='datasets',
                        help='path for storing the dataset')

    parser.add_argument('--dropout_a', type=float, default=0.1,
                        help='dropout of acoustic LSTM out layer')
    parser.add_argument('--dropout_v', type=float, default=0.1,
                        help='dropout of visual LSTM out layer')
    parser.add_argument('--dropout_prj', type=float, default=0.1,
                        help='dropout of projection layer')

    parser.add_argument('--multiseed', action='store_true', help='training using multiple seed')
    parser.add_argument('--add_va', action='store_true', help='if add module')
    parser.add_argument('--n_layer', type=int, default=1,
                        help='number of layers in LSTM encoders (default: 1)')
    parser.add_argument('--d_vh', type=int, default=16,
                        help='hidden size in visual rnn')
    parser.add_argument('--d_ah', type=int, default=16,
                        help='hidden size in acoustic rnn')
    parser.add_argument('--d_vout', type=int, default=16,
                        help='output size in visual rnn')
    parser.add_argument('--d_aout', type=int, default=16,
                        help='output size in acoustic rnn')
    parser.add_argument('--bidirectional', action='store_true', help='Whether to use bidirectional rnn')
    parser.add_argument('--d_prjh', type=int, default=128,
                        help='hidden size in projection network')
    parser.add_argument('--pretrain_emb', type=int, default=768,
                        help='dimension of pretrained model output')

    parser.add_argument('--mmilb_mid_activation', type=str, default='ReLU',
                        help='Activation layer type')

    parser.add_argument('--batch_size', type=int, default=50, metavar='N',
                        help='batch size (default: 50)')
    parser.add_argument('--clip', type=float, default=1.0,
                        help='gradient clip value (default: 0.8)')
    parser.add_argument('--lr_main', type=float, default=1e-3,
                        help='initial learning rate for main model parameters (default: 1e-3)')
    parser.add_argument('--lr_bert', type=float, default=5e-5,
                        help='initial learning rate for bert parameters (default: 5e-5)')
    parser.add_argument('--lr_mmilb', type=float, default=1e-3,
                        help='initial learning rate for mmilb parameters (default: 1e-3)')
        
    parser.add_argument('--optim', type=str, default='SGD',
                        help='optimizer to use (default: SGD)')
    parser.add_argument('--num_epochs', type=int, default=40,
                        help='number of epochs (default: 40)')
    parser.add_argument('--when', type=int, default=5,
                        help='when to decay learning rate (default: 20)')
    parser.add_argument('--patience', type=int, default=10,
                        help='when to stop training if best never change')
    parser.add_argument('--update_batch', type=int, default=1,
                        help='update batch interval')
    parser.add_argument('--labeled_frac', type=float, default=0.1,
                        help='fraction of data that we considered labeled.')
    parser.add_argument('--seed', type=int, default=1111,
                        help='random seed')
    parser.add_argument('--momentum', type=float, default=0.9,
                        help='Momentum value for SGD')
    parser.add_argument('--server_time', type=float, default=1.0,
                        help='Momentum value for SGD')
    args = parser.parse_args()
    return args

class Config(object):
    def __init__(self, data, labeled_frac, mode='train'):
        self.dataset_dir = data_dict[data.lower()]
        self.sdk_dir = sdk_dir
        self.mode = mode
        self.labeled_frac = labeled_frac
        self.word_emb_path = word_emb_path
        self.data_dir = self.dataset_dir

    def __str__(self):
        config_str = 'Configurations\n'
        config_str += pprint.pformat(self.__dict__)
        return config_str

def get_config(dataset='iemocap', mode='train', batch_size=32, labeled_frac=1.0):
    config = Config(data=dataset, labeled_frac=labeled_frac, mode=mode)
    config.dataset = dataset
    config.batch_size = batch_size

    return config
