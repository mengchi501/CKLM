import numpy
import torch
import torch.nn as nn

import os
import random
import copy

from tqdm import tqdm
import prettytable

class GraphDataset:
    def __init__(self):
        self.data_path = os.path.abspath('')
        self.dataset_size = ''
        self.num_entities = 0
        self.num_relations = 0
        self.unique_entities = set()
        self.unique_relations = set()
        self.unique_triples = set()

    def load_data(self):
        # Load the data from the specified path
        pass

    def preprocess_data(self):
        # Preprocess the data for training
        pass

    def get_train_data(self):
        # Return training data
        pass

    def get_valid_data(self):
        # Return validation data
        pass

    def get_test_data(self):
        # Return test data
        pass

    # 일단 codex-S부터 분석 
    def load_codex_data(self, size, which):
        '''
        size : s, m, l
        which : train, valid, test
        '''

        self.dataset_size = size

        degree_per_entity = {}
        frequency_per_relation = {}

        file_path = os.path.join(os.path.abspath(''), 'triples', f'codex-{self.dataset_size}', f'{which}.txt')
        with open(file_path, 'r') as f:
            for line in f:
                h, r, t = line.strip().split()
                self.unique_entities.add(h)
                self.unique_entities.add(t)
                self.unique_relations.add(r)
                if h not in degree_per_entity:
                    degree_per_entity[h] = 0
                else:
                    degree_per_entity[h] += 1
                if t not in degree_per_entity:
                    degree_per_entity[t] = 0
                else:
                    degree_per_entity[t] += 1
                if r not in frequency_per_relation:
                    frequency_per_relation[r] = 0
                else:
                    frequency_per_relation[r] += 1
                if (h, r, t) not in self.unique_triples:
                    self.unique_triples.add((h, r, t))
        degree_per_entity = {k: v for k, v in sorted(degree_per_entity.items(), key=lambda item: item[1], reverse=True)}
        frequency_per_relation = {k: v for k, v in sorted(frequency_per_relation.items(), key=lambda item: item[1], reverse=True)}

        print(f'Unique entities: {len(self.unique_entities)}')
        print(f'Unique relations: {len(self.unique_relations)}')
        print(f'Unique triples: {len(self.unique_triples)}')
        print(f'Degree per entity: {degree_per_entity}')
        print(f'Frequency per relation: {frequency_per_relation}')
        print(f'Average degree per entity: {sum(degree_per_entity.values()) / len(degree_per_entity)}')

    def construct_element_centric(self, element, num_snapshots):
        '''
        element : 'entity', 'relation', 'fact', 'hybrid'
        num_snapshots : Number of snapshots to be constructed
        '''
        sample_triples = copy.deepcopy(self.unique_triples)
        accumulated_triples_cnt = []
        
        snapshot_entities = [set()]
        snapshot_relations = [set()]
        snapshot_triples = [set()]
        for i in tqdm(range(num_snapshots)):
            if i == 0:
                seed_triples = []
                for _ in range(10):
                    seed_triple = random.choice(list(sample_triples))
                    seed_triples.append(seed_triple)
                    sample_triples.remove(seed_triples[-1])
                    h, r, t = seed_triple
                    snapshot_entities[0].add(h)
                    snapshot_entities[0].add(t)
                    snapshot_relations[0].add(r)
                    snapshot_triples[0].add(seed_triple)
            while len(sample_triples) > 0:
                if element == 'entity' and len(snapshot_entities[i]) >= len(self.unique_entities) * (i + 1) / num_snapshots:
                    break
                elif element == 'relation' and len(snapshot_relations[i]) >= len(self.unique_relations) * (i + 1) / num_snapshots:
                    break
                elif element == 'fact' and len(snapshot_triples[i]) >= len(self.unique_triples) / num_snapshots:
                    break
                sample_triple = random.sample(sample_triples, 1)[0]
                h, r, t = sample_triple
                if h not in snapshot_entities[i] and t not in snapshot_entities[i]:
                    continue
                snapshot_entities[i].add(h)
                snapshot_entities[i].add(t)
                snapshot_relations[i].add(r)
                snapshot_triples[i].add(sample_triple)
                sample_triples.remove(sample_triple)
            if i == num_snapshots - 1:
                # add remaining triples to the last snapshot
                snapshot_triples[-1].update(sample_triples)
            else:
                # add all triples containing seen entities & relations to the current snapshot
                for sample_triple in sample_triples:
                    h, r, t = sample_triple
                    if h in snapshot_entities[i] and t in snapshot_entities[i] and r in snapshot_relations[i]:
                        snapshot_triples[i].add(sample_triple)
                        sample_triples.remove(sample_triple)
            print(f'Snapshot {i}: {len(snapshot_entities[i])} entities, {len(snapshot_relations[i])} relations, {len(snapshot_triples[i])} triples')

            file_path = os.path.join(os.path.abspath(''), 'triples', f'codex-{self.dataset_size}', f'{element.upper()}_snapshot_{i}.txt')

            with open(file_path, 'w') as f:
                for h, r, t in snapshot_triples[i]:
                    f.write(f'{h}\t{r}\t{t}\n')
            
            if i == 0:
                accumulated_triples_cnt.append(len(snapshot_triples[i]))
            else:
                accumulated_triples_cnt.append(len(snapshot_triples[i]) + accumulated_triples_cnt[i - 1])

            snapshot_entities.append(copy.deepcopy(snapshot_entities[i]))
            snapshot_relations.append(copy.deepcopy(snapshot_relations[i]))
            snapshot_triples.append(set())

            i += 1

        # print results
        t = prettytable.PrettyTable(['Snapshot', 'Entities', 'Relations', 'Accumulated Triples', 'New Triples'])
        for i in range(num_snapshots):
            t.add_row([i, len(snapshot_entities[i]), len(snapshot_relations[i]), accumulated_triples_cnt[i], len(snapshot_triples[i])])
        print(t)
