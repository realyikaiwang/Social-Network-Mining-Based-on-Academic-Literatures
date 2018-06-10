#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Yikai Wang
"""
import random
import numpy as np
import pickle
import json
from argparse import ArgumentParser,ArgumentDefaultsHelpFormatter

def AUC(task,nonexist,missing_edges,authors,times,node_vector,confs=[]):
    if task == 'cp' or task == 're':
        n1 = 0
        n2 = 0
        for i in range(times):
            missing_edge = random.sample(missing_edges,1)[0]
            nonexist_edge = []
            while True:
                tmp1 = random.randint(0,len(authors)-1)
                tmp2 = random.randint(0,len(authors)-1)
                if tmp1 == tmp2 or (not nonexist[tmp1][tmp2]):
                    continue
                else:
                    if nonexist[tmp1][tmp2] and nonexist_edge == []:
                        nonexist_edge = [authors[tmp1],authors[tmp2]]
                if nonexist_edge != []:
                    break
            score_miss = np.sum(np.array(node_vector[missing_edge[0]])*np.array(node_vector[missing_edge[1]]))
            score_none = np.sum(np.array(node_vector[nonexist_edge[0]])*np.array(node_vector[nonexist_edge[1]]))
            if score_miss > score_none:
                n1 += 1
            elif score_miss == score_none:
                n2 += 1
            print(i)
        result = (n1+0.5*n2)/times
        print(result)
        return result
    if task == 'conf':
        return

def Precision(task,nonexist,authors,L,node_vector,confs=[]):
    if task == 'cp' or task == 're':
        non_observed_edges = []
        for i in range(len(authors)-1):
            for j in range(i+1, len(authors)):
                score = np.sum(np.array(node_vector[i])*np.array(node_vector[j]))
                non_observed_edges.append([[i,j],score])
        non_observed_edges.sort(key= lambda x: -x[1])
        Lr = 0
        for i in range(L):
            if not nonexist[non_observed_edges[i][0][0]][non_observed_edges[i][0][1]]:
                Lr += 1
        result = Lr/L
        print(result)
        return result
    if task =='conf':
        return


def load_pickle(path):
    pkl_file = open(path, 'rb')
    data = pickle.load(pkl_file)
    pkl_file.close()
    return data

def load_txt(path):
    with open(path,'r') as f:
        data = []
        while True:
            a = f.readline().split()
            if a:
                data.append(a[0])
            else:
                break
    return data

def load_json(dir):
   data = []
   with open(dir, 'r') as f:
       while True:
           a = f.readline()
           if not a:
               break
           b = json.loads(a)
           data.append(b)
   return data
parser = ArgumentParser('evaluation',
                            formatter_class=ArgumentDefaultsHelpFormatter,
                            conflict_handler='resolve')
parser.add_argument('--task', default=False,
                        help='cp/re/conf')
args = parser.parse_args()
if args.task=='cp':
    vectors = load_pickle('data/task3'+args.task+'.pkl')
    valid_id = load_txt('data/valid_id_4task3.txt')
    chosen_authors = list(vectors.keys())
    authors2num = dict()
    for i in range(len(chosen_authors)):
        authors2num[chosen_authors[i]]=i
    nonexist = [[True]*len(chosen_authors)]*len(chosen_authors)
    papers = load_json('data/allpaper.txt')
    missing_edges= []
    for i in range(len(papers)):
        if str(i) in valid_id:
            authors = papers[i]['authors']
            new_authors = [au.replace(' ','') for au in authors]
            for i in range(len(new_authors)-1):
                if new_authors[i] in chosen_authors:
                    for j in range(i+1,len(authors)):
                        if new_authors[j] in chosen_authors:
                            nonexist[authors2num[new_authors[i]]][authors2num[new_authors[j]]]=False
                            nonexist[authors2num[new_authors[j]]][authors2num[new_authors[i]]]=False
                            missing_edges.append([new_authors[i],new_authors[j]])
    print('Finished Loading!')
    AUC(task=args.task,nonexist=nonexist,missing_edges=missing_edges,authors=chosen_authors,times=5000,node_vector=vectors)
    #Precision(task=args.task,nonexist=nonexist,authors=chosen_authors,L=5000,node_vector=vectors)
elif args.task=='re':
    vectors = load_pickle('data/task3'+args.task+'.pkl')
    valid_id = load_txt('data/valid_id_4task3.txt')
    chosen_authors = list(vectors.keys())
    authors2num = dict()
    for i in range(len(chosen_authors)):
        authors2num[chosen_authors[i]]=i
    nonexist = [[False]*len(chosen_authors)]*len(chosen_authors)
    papers = load_json('data/allpaper.txt')
    for i in range(len(papers)):
        if str(i) in valid_id:
            authors = papers[i]['authors']
            new_authors = [au.replace(' ','') for au in authors]
            for i in range(len(new_authors)-1):
                if new_authors[i] in chosen_authors:
                    for j in range(i+1,len(authors)):
                        if new_authors[j] in chosen_authors:
                            nonexist[authors2num[new_authors[i]]][authors2num[new_authors[j]]]=False
                            nonexist[authors2num[new_authors[j]]][authors2num[new_authors[i]]]=False
    AUC(task=args.task,nonexist=nonexist,authors=chosen_authors,times=5000,node_vector=vectors)
if args.task =='conf':
    vectors = load_pickle('data/task3' + args.task + '.pkl')
    train_id = load_txt('data/train_id_4task3.txt')
    valid_id = load_txt('data/valid_id_4task3.txt')
    chosen_authors = list(vectors['authors'].keys())
    chosen_confs = list(vectors['conf'].keys())
    exist_edges = []
    missing_edges = []
    papers = load_json('data/allpaper.txt')
    for i in range(len(papers)):
        if str(i) in train_id:
            authors = papers[i]['authors']
            new_authors = [au.replace(' ', '') for au in authors]
            for i in range(len(new_authors) - 1):
                if new_authors[i] in chosen_authors:
                    for j in range(i + 1, len(authors)):
                        if new_authors[j] in chosen_authors:
                            exist_edges.append([new_authors[i], new_authors[j]])
        elif str(i) in valid_id:
            authors = papers[i]['authors']
            new_authors = [au.replace(' ', '') for au in authors]
            for i in range(len(new_authors) - 1):
                if new_authors[i] in chosen_authors:
                    for j in range(i + 1, len(authors)):
                        if new_authors[j] in chosen_authors:
                            missing_edges.append([new_authors[i], new_authors[j]])
    AUC(task=args.task, exist_edges=exist_edges, missing_edges=missing_edges, authors=chosen_authors, times=5000,
        node_vector=vectors)
    #Precision(task=args.task, exist_edges=exist_edges, missing_edges=missing_edges, authors=chosen_authors, L=5000,
              #node_vector=vectors)










