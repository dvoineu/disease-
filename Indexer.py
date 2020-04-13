
import re
import os
import math
import pickle


class Indexer:

    stop_words = None
    file_count = 0

    file_term = None
    inverted_idx = None

    vectors = None
    vectors_length = None
    tf = None
    df = None
    idf = None

    def __init__(self, directory, load_file=False, stop_word_path=None):
        self.stop_words = set()
        self.file_term = {}   # regular index
        self.inverted_idx = {}  # inverted index
        self.match_pattern = r'[\w]+[\'|-]?[\w]*'
        self.match_pattern_letters_only = r'[a-zA-z]+[\'|-]?[a-zA-z]+'

        self.vectors_length = {}
        self.tf = {}
        self.df = {}
        self.idf = {}

        if stop_word_path:
            self.build_stop_list(stop_word_path)
        else:
            self.build_stop_list('stop_words.txt')

        if load_file:
            with open('cache/inverted_idx', 'rb') as f:
                self.inverted_idx = pickle.load(f)
            with open('cache/vectors_length', 'rb') as f:
                self.vectors_length = pickle.load(f)
            with open('cache/tf', 'rb') as f:
                self.tf = pickle.load(f)
            with open('cache/idf', 'rb') as f:
                self.idf = pickle.load(f)
            with open('cache/df', 'rb') as f:
                self.df = pickle.load(f)

            self.file_count = len(self.file_term)
            return

        self.index_a_directory(directory)

        self.make_idf()
        self.doc_vectors()

        self.save_index_to_file()

    def save_index_to_file(self):

        f = open('cache/inverted_idx', 'wb')
        pickle.dump(self.inverted_idx, f)
        f.close()

        f = open('cache/vectors_length', 'wb')
        pickle.dump(self.vectors_length, f)
        f.close()

        f = open('cache/tf', 'wb')
        pickle.dump(self.tf, f)
        f.close()

        f = open('cache/df', 'wb')
        pickle.dump(self.df, f)
        f.close()

        f = open('cache/idf', 'wb')
        pickle.dump(self.idf, f)
        f.close()

    def index_a_directory(self, file_path):
        for file in os.listdir(file_path):
            current = os.path.join(file_path, file)
            if os.path.isfile(current):
                if "stop_words" in file:
                    continue
                if "txt" in file:
                    self.file_parser(current)

        self.generate_inverted_idx()
        return self.inverted_idx

    def get_inverted_index(self):
        return self.inverted_idx

    # generate a set of stop word by predefined
    def build_stop_list(self, stop_word_path):
        with open(stop_word_path) as file:
            for line in file:
                if not line or line.startswith("#"):
                    continue
                else:
                    self.stop_words.add(line.strip())

    # convert all term in to file into a {filename:{w1:[1,2], w2:[3,4},...},...} pair inserted in map
    # String is the file_name. list is a list of all term.
    def file_parser(self, file):

        doc_id = int(file.split("/")[-1].split(".")[0])

        pattern = re.compile(self.match_pattern_letters_only)         #[\w]+ before
        data = open(file, 'r').read().lower()
        data = pattern.findall(data)

        print(doc_id)

        words = []
        self.tf[doc_id] = {}
        for word in data:
            if word in self.stop_words:
                continue
            self.df[word] = self.df[word] + 1 if word in self.df.keys() else 1
            self.tf[doc_id][word] = self.tf[doc_id][word] + 1 if word in self.tf[doc_id].keys() else 1
            words.append(word)

        self.file_term[doc_id] = words
        self.file_count += 1

    # input = {filename:{w1:[1,2], w2:[3,4},...},...}
    # res = {w: {filename: [pos1, pos2]}, ...}, ...}
    # meanwhile, add support for term freq and docs freq
    def generate_inverted_idx(self):
        total_idx = {}
        for doc_id in self.file_term.keys():
            for word in self.file_term[doc_id]:
                if word in total_idx.keys():
                    total_idx[word].add(doc_id)
                else:
                    total_idx[word] = {doc_id}
        self.inverted_idx = total_idx

    def doc_vectors(self):
        print("make vectors")
        vectors = {}
        for doc_id in self.file_term.keys():
            print(doc_id)
            vector = []
            for word in self.inverted_idx.keys():
                vector.append(self.get_score(word, doc_id))
            vectors[doc_id] = vector
            self.vectors_length[doc_id] = self.vector_length(vector)

    @staticmethod
    def vector_length(vector):
        length = 0
        for x in vector:
            length += x ** 2
        return math.pow(length, 0.5)

    def invert_document_frequency(self, document_freq):
        n = self.file_count
        return math.log10(n / document_freq) if document_freq != 0 else 0

    def make_idf(self):
        for word in self.inverted_idx.keys():
            self.idf[word] = self.invert_document_frequency(self.df[word])

    def get_score(self, word, doc_id):
        return math.log(1 + (self.tf[doc_id][word] if word in self.tf[doc_id].keys() else 0)) + self.idf[word]



