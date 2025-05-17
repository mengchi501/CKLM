import torch
import torch.nn as nn
import torch.nn.functional as F
import os
import random

from codex import Codex

class MyGraph:
    def __init__(self):
        self.graph = None
        self.node_types = {}
        self.relation_types = {}
        self.entity_embeddings = None
        self.relation_embeddings = None
        self.num_nodes = 0
        self.num_rels = 0
        self.num_edges = 0
        self.unique_nodes = set()
        self.unique_rels = set()
        self.adjacency_list = {}

    # def count_nodes(self):


    def load_triples(self, dataset):
        '''
        Loads the data from the specified path.
        해당 함수는 처음에 from scratch 단계에서 그래프를 생성할 때만 사용
        '''

        data_path = os.path.join(os.path.dirname(__file__), f'data/{dataset}')
        if not os.path.exists(data_path):
            raise FileNotFoundError(f"Data path {data_path} does not exist.")
        if dataset == 'codex':
            codex = Codex(size='s')
            with open(f'{data_path}/triples/test.txt', 'r') as f: # 일단 임의로 test.txt로 설정
                lines = f.readlines()
                for line in lines:
                    head, relation, tail = line.strip().split('\t')
                    if head not in self.unique_nodes:
                        self.unique_nodes.add(head)
                        self.adjacency_list[head] = set()
                        self.adjacency_list[head].add(head) # self loop edge 추가 
                    else:
                        self.adjacency_list[head].add(tail)
                    if tail not in self.unique_nodes:
                        self.unique_nodes.add(tail)
                        self.adjacency_list[tail] = set()
                        self.adjacency_list[tail].add(tail)
                    else:
                        self.adjacency_list[tail].add(head)
                    self.unique_rels.add(relation)

                    self.num_edges += 1
            self.num_nodes = len(self.unique_nodes)
            self.num_rels = len(self.unique_rels)



class MyKG(MyGraph):
    def __init__(self):
        super(MyKG, self).__init__()
        

    # def get_sub_graph(self, )