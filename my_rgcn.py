import torch
import torch.nn as nn
import torch.nn.functional as F

class RGCN(nn.Module):
    def __init__(self, in_feat, hid_feat, out_feat, num_relations, num_bases=None):
        '''
        in_feat은 LLM encoder가 사용하는 dimension으로 사용 혹은 그걸 변형 
        '''
        super(RGCN, self).__init__()
        self.in_feat = in_feat
        self.hid_feat = hid_feat
        self.out_feat = out_feat
        self.num_relations = num_relations
        self.num_bases = num_bases if num_bases is not None else num_relations

        self.weight = nn.Parameter(torch.Tensor(hid_feat, hid_feat)) # 일단은 출력 feat hid feat로 설정, 나중에 변경 예정 

        self.linear = nn.Linear(self.in_feat, self.hid_feat)

        # Initialize bias
        self.bias = nn.Parameter(torch.Tensor(out_feat))
        nn.init.zeros_(self.bias)

    def forward(self, h, adj):
        '''
        h : input node features
        adj : adjacency list
        '''
        

        
    
    def aggregate(self, x, graph, hidden_features):
        '''
        x : node id
        '''
        hs = self.linear(hidden_features[x])
        adj = graph.adjacency_list
        # for neighbor in adj[x]:
            