import Indexer
import re

import heapq



class Query:
    indexer = None
    inverted_index = {}
    stop_list = {}

    def __init__(self, directory, load_file=False, stop_word_path=None):
        self.indexer = Indexer.Indexer(directory, load_file, stop_word_path)
        self.inverted_index = self.indexer.inverted_idx
        self.stop_list = self.indexer.stop_words

    def query(self, query):
        pattern = re.compile(self.indexer.match_pattern)
        query = pattern.findall(query)
        query = [word for word in query if word not in self.stop_list]
        docs = []
        for word in query:
            if word in self.inverted_index.keys():
                docs += self.inverted_index[word]
        return self.cosine_score(list(set(docs)), query)

    def one_word_query(self, query):
        if query not in self.inverted_index.keys():
            return []
        return self.cosine_score([doc_id for doc_id in self.inverted_index[query]], [query])

    @staticmethod
    def query_term_frequency(query, target):
        count = 1
        for word in query:
            if word == target:
                count += 1
        return count

    def cosine_score(self, doc_ids, query):
        score = dict.fromkeys(doc_ids, 0.0)
        for word in query:
            # for query word not in docs, skip, (0)
            if word not in self.inverted_index.keys():
                continue
            # weight of query term is the idf
            weight_tq = self.indexer.idf[word]
            for doc_id in self.inverted_index[word]:
                weight_td = self.indexer.get_score(word, doc_id)
                score[doc_id] += weight_tq * weight_td

        for doc_id in doc_ids:
            length = self.indexer.vectors_length[doc_id]
            score[doc_id] /= length

        # x = {1: 2, 3: 4, 4: 3, 2: 1, 0: 0}
        # {k: v for k, v in sorted(x.items(), key=lambda item: item[1])}
        # {0: 0, 2: 1, 1: 2, 4: 3, 3: 4}
        return self.top_20(score)

    @staticmethod
    def top_20(scores):  # score is a dict, key: docid, value score
        item_list = []
        for item in scores.items():
            item_list.append((-item[1], item[0]))
        heapq.heapify(item_list)
        res = []
        for i in range(10):
            if not item_list:
                break
            dd = heapq.heappop(item_list)
            print(dd[0])
            print(dd[1])
            res.append(dd[1])
        return res

if __name__ == "__main__":
    query = Query('./data', True)
    query.query('coronavirus' )





