import torch
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms, datasets
import json
import PIL
import numpy as np
import torch.nn.functional as F
import tqdm
import transformers
import os
import copy
import random

import pandas as pd
import csv
import pickle


      
class PaperDataset(Dataset):
    def __init__(self, root_path, seq_length = 512, voc_size = 32000,keep_author = True, keep_bib = True):
        #elems = all filenames in tokenized directory
        elems = os.listdir(root_path)
        self.root_path = root_path
        self.elems = elems
        self.voc_size = voc_size
        self.seq_length = seq_length
        self.keep_author = keep_author
        self.keep_bib = keep_bib
    
    def __len__(self):
        return len(self.elems)
    
    def __getitem__(self,idx):
        #root path is path/to/tokenized/text
        npy_path =  self.root_path + '/'+ self.elems[idx]
        #loads BatchEncoding object's input_ids in each tokenized file as np array
        data = np.asarray(pickle.load(open(npy_path,'rb'))["input_ids"])
        #takes random subsection of 512 tokens from each tokenized file
        #see PMC LLaMA for more information on why
        input_id = self.random_subsection(data)
        label = copy.deepcopy(input_id)
        return dict(input_ids=input_id, labels=label)
    
    #takes 512 tokens randomly from the array of input tokens for each tokenized file
    def random_subsection(self, arr):
        if len(arr) < self.seq_length:
            arr = np.pad(arr, (0, self.seq_length - len(arr)), 'constant', constant_values=2)
        if len(arr) - self.seq_length == 0:
            start = 0
            return arr[start:start+self.seq_length]
        start = np.random.randint(0, len(arr) - self.seq_length)
        while(np.sum(arr[start:start+self.seq_length] == self.voc_size) %2 !=0):
            start = np.random.randint(0, len(arr) - self.seq_length)
        return arr[start:start+self.seq_length]
    
