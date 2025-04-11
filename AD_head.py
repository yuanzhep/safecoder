import sys
import os
import torch.optim as optim
import sys
sys.path.append('..')
from metrics import *
from models import *
from loader import *
import matplotlib.pyplot as plt
import numpy
import argparse
from facenet_pytorch import InceptionResnetV1
import sklearn.metrics
from statistics import mean
import csv
import matplotlib.pyplot as plt

bs = 128
max_epoch = 300
num_class = 2
for beta in [None]:
    mode=f'beta{beta}'
    figurePath = "../dataset/cel"
    attributePath = "../dataset/attri_test.txt"
    result_dir = f"../params/"
    os.makedirs(result_dir, exist_ok=True)
    print("Loading images from:", figurePath)
    print("Result Dir:", result_dir)

    _, dataloader = init_dataloader(attributePath, figurePath, action='prt', batch_size=bs, n_classes=num_class, skiprows=1, allAttri=True)

    Enc = Encoder()
    Enc = torch.nn.DataParallel(Enc).cuda()
    Enc.eval()
    cf = Classifier(num_class)
    cf = torch.nn.DataParallel(cf).cuda()
    cf.train()

    opt = optim.Adam(cf.parameters())

    loss_fn = torch.nn.CrossEntropyLoss()
    loss_list = []
    for e in range(max_epoch):
        print("Epoch", e)
        for i, (img, label) in enumerate(dataloader):
            img = img.cuda()
            label = label.cuda()
            # label = label[:,[0, 1]].cuda()
            with torch.no_grad():
                feature = Enc(img)
            feature = torch.load(featurePath.format(i))
            opt.zero_grad()
            pred = cf(feature)
            # import pdb;pdb.set_trace()
            loss = loss_fn(pred, label)
            loss.backward()
            loss_list.append(loss.item())
            opt.step()
        # plt.plot(loss_list)
        torch.save(cf.module.state_dict(), os.path.join(result_dir, f"cf_{e}.pkl"))