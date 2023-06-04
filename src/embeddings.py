import numpy as np
import pickle
import zipfile
import torch

from abc import abstractmethod
from typing import List, Dict, Tuple, Union
from utils import graph_utils


class EmbeddingProvider:

    def __init__(self, num_dimensions: int = 100,
                 num_entity_dimensions: int = 100,
                 num_relation_dimensions: int = 100,
                 num_question_dimensions: int = 100):
        self.num_dimensions = num_dimensions
        self.num_entity_dimensions = num_entity_dimensions
        self.num_relation_dimensions = num_relation_dimensions
        self.num_question_dimensions = num_question_dimensions

    @abstractmethod
    def entity_embeddings(self, entities: List[str]):
        pass

    @abstractmethod
    def relation_embeddings(self, relations: Dict[Tuple[int, int], List[str]]):
        pass

    @abstractmethod
    def question_embeddings(self, question: str):
        pass


class DebugEmbeddingProvider(EmbeddingProvider):

    def __init__(self, num_dimensions: int = 300):
        super().__init__(num_dimensions=num_dimensions)
        self.embeddings = {}
        self.num_entity_dimensions = num_dimensions
        self.num_relation_dimensions = num_dimensions
        self.num_question_dimensions = num_dimensions

    def entity_embeddings(self, entities: List[str]):
        return torch.from_numpy(np.random.randn(len(entities), self.num_dimensions)).float()

    def relation_embeddings(self, relations: Dict[Tuple[int, int], List[str]]):
        return {key: torch.from_numpy(np.random.randn(self.num_dimensions)).float() for key, _ in relations.items()}

    def question_embeddings(self, question: str):
        return torch.from_numpy(np.random.randn(self.num_dimensions)).float()


class GloveEmbeddingProvider(EmbeddingProvider):

    def __init__(self, path: str, num_dimensions: int = 300, pickle: bool = False):
        super().__init__(num_dimensions=num_dimensions)
        self.pickle = pickle
        self.embeddings = self._load_embeddings(path)
        self.num_entity_dimensions = num_dimensions
        self.num_relation_dimensions = num_dimensions
        self.num_question_dimensions = num_dimensions

    def _load_embeddings(self, path: str) -> Dict[str, List[float]]:
        if self.pickle:
            with open(path, 'rb') as emb_file:
                embeddings = pickle.load(emb_file)
        else:
            with zipfile.ZipFile(path) as z:
                file_ = [file_name for file_name in z.namelist() if str(self.num_dimensions) in file_name]
                if len(file_) != 1:
                    raise ValueError(f'Can\'t find glove embeddings for {self.num_dimensions}')

                with z.open(file_[0], 'r') as f:
                    embeddings = {}
                    for line in f:
                        line = line.decode('utf-8').strip().split(' ')
                        embeddings[line[0]] = [float(value) for value in line[1:]]
        # with open('glove_embeddings.pickle', 'wb') as file_:
        #    pickle.dump(embeddings, file_)
        return embeddings

    def entity_embeddings(self, entities: List[str]):
        return torch.stack([self._get_embedding(entity.split(' ')) for entity in entities]).float()

    def relation_embeddings(self, relations: Dict[Tuple[int, int], Union[List[str], str]]):
        if isinstance(next(iter(relations.values())), str):
            relation_embs = {relation: self._get_embedding(relation.split(' ')) for relation in set(relations.values())}
            return {key: relation_embs[relation] for key, relation in relations.items()}
        else:
            return {key: self._get_embedding(relation) for key, relation in relations.items()}

    def question_embeddings(self, question: str):
        return self._get_embedding(graph_utils.remove_stop_words(question))

    def _get_embedding(self, parts: List[str]):
        part_embeddings = [np.array(self.embeddings[part]) for part in parts if part in self.embeddings]
        emb = np.mean(part_embeddings, axis=0) if len(part_embeddings) > 0 else np.ones(self.num_dimensions)
        return torch.from_numpy(emb).float()


class BertEmbeddingProvider(EmbeddingProvider):

    def __init__(self, entity_embeddings_path: str,
                 relation_embeddings_path: str,
                 question_embeddings_path_train: str,
                 question_embeddings_path_valid: str,
                 num_dimensions: int = 768):
        super().__init__(num_dimensions=num_dimensions)

        with open(entity_embeddings_path, 'rb') as f:
            self.entity_embeddings_ = pickle.load(f)

        with open(relation_embeddings_path, 'rb') as f:
            self.relation_embeddings_ = pickle.load(f)

        with open(question_embeddings_path_train, 'rb') as f:
            train_embeddings = pickle.load(f)

        with open(question_embeddings_path_valid, 'rb') as f:
            valid_embeddings = pickle.load(f)

        self.question_embeddings_ = {**train_embeddings, **valid_embeddings}
        self.num_entity_dimensions = self.entity_embeddings_.shape[-1]
        self.num_relation_dimensions = next(iter(self.relation_embeddings_.values())).shape[-1]
        self.num_question_dimensions = next(iter(self.question_embeddings_.values())).shape[-1]

    def entity_embeddings(self, _: List[str]):
        return self.entity_embeddings_

    def relation_embeddings(self, _: Dict[Tuple[int, int], List[str]]):
        return self.relation_embeddings_

    def question_embeddings(self, question: str):
        return self.question_embeddings_[question]


class TrainableEmbeddingProvider(EmbeddingProvider):

    def __init__(self, num_dimensions: int = 100):
        super().__init__(num_dimensions=num_dimensions)

    def entity_embeddings(self, entities: List[str]):
        pass

    def relation_embeddings(self, relations: List[str]):
        pass
