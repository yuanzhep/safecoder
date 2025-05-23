import torchvision
import torch
import torch.nn
from torch.optim import Adam
import sys
sys.path.append('..')
import loader
from plot_loss import plot_loss
import os
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-d', action='store_true', default=False, help='debug')
parser.add_argument('-whole', action='store_true', default=False, help='Train resnet/not FC')
args = parser.parse_args()

pubpath = '../dataset/pub'
attrpath = '../dataset/pub_attri.csv'
result_dir = '../params/enc/'

net = torchvision.models.resnet18(pretrained=True)

if not args.whole:
    for p in net.parameters():
        p.requires_grad_(False)

net.fc = torch.nn.Linear(in_features=512, out_features=40)
net = torch.nn.DataParallel(net).cuda()
if args.d:
    import pdb;pdb.set_trace()
if args.whole:
    optim = Adam(net.parameters())
else:
    optim = Adam(net.module.fc.parameters())
criteria = torch.nn.BCELoss()

_, pubLoader = loader.init_dataloader(attrpath,pubpath,batch_size=64, n_classes=2, skiprows=1, allAttri=True)


loss_list = list()

net.train()

if args.d:
    import pdb;pdb.set_trace()
for eid in range(30):
    for (bid, (img, label)) in enumerate(pubLoader):
        img = img.cuda()
        label = label.cuda()
        pred = torch.sigmoid(net(img))
        optim.zero_grad()
        loss = criteria(pred, label)
        loss.backward()
        loss_list.append(loss.item())
        optim.step()
    plot_loss(loss_list,result_dir,'trainLoss','training loss')
    if args.whole:
        torch.save(net.module.state_dict(), os.path.join(result_dir,'param_epoch_{}.pt'.format(eid)))
    else:
        torch.save(net.module.fc.state_dict(), os.path.join(result_dir,'param_epoch_{}.pt'.format(eid)))

if args.whole:
    torch.save(net.module.state_dict(), '../params/enc.pt')
else:
    torch.save(net.module.fc.state_dict(), '../params/enc.pt')