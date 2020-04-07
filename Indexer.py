import xml.etree.ElementTree as ET
import re
import os
import argparse
import math


class Indexer:

    stop_words = None
    curr_assign_doc_id = 1
    file_count = 0
    total_docs_num = 0

    file_term = None
    xml_attributes = None
    inverted_idx = None

    vectors = None
    vectors_length = None
    tf = None
    df = None
    idf = None

    def __init__(self, directory, stop_word_path=None):
        self.stop_words = set()
        self.file_term = {}   # regular index
        self.file_name_to_doc_id = {}
        self.doc_id_to_file_name = {}
        self.inverted_idx = {}  # inverted index
        self.xml_attributes = {}
        self.match_pattern = r'[\w]+[\'|-]?[\w]*'
        self.match_pattern_letters_only = r'[a-zA-z]+[\'|-]?[a-zA-z]+'

        self.vectors = {}
        self.vectors_length = {}
        self.tf = {}
        self.df = {}
        self.idf = {}

        if stop_word_path:
            self.build_stop_list(stop_word_path)
        else:
            self.build_stop_list('stop_words.txt')
        self.index_a_directory(directory)

        # self.make_vectors()
        # self.vector_length()
        self.make_idf()
        self.doc_vectors()

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

        doc_id = self.file_count

        pattern = re.compile(self.match_pattern_letters_only)         #[\w]+ before
        data = open(file, 'r').read().lower()
        data = pattern.findall(data)

        words = []
        self.tf[doc_id] = {}
        for word in data:
            if word in self.stop_words:
                continue
            self.df[word] = self.df[word] + 1 if word in self.df.keys() else 1
            self.tf[doc_id][word] = self.tf[doc_id][word] + 1 if word in self.tf[doc_id].keys() else 1
            words.append(word)

        # data = [word for word in data if word not in self.stop_words]

        # add indices for each term in the list and convert filename into dod_id
        # indices = self.add_indices(data)
        self.file_term[doc_id] = words
        self.file_count += 1

    # input = {filename:{w1:[1,2], w2:[3,4},...},...}
    # res = {w: {filename: [pos1, pos2]}, ...}, ...}
    # meanwhile, add support for term freq and docs freq
    def generate_inverted_idx(self):
        total_idx = {}
        for doc_id in self.file_term.keys():
            # self.tf[doc_id] = {}  # add support for term frequency
            for word in self.file_term[doc_id]:
                # self.tf[doc_id][word] = len(self.file_term[doc_id][word])
                # if word in self.df.keys():
                #     self.df[word] += 1
                # else:
                #     self.df[word] = 1
                if word in total_idx.keys():
                    if doc_id not in total_idx[word]:
                        total_idx[word].add(doc_id)
                    # if doc_id in total_idx[word].keys():
                    #     total_idx[word][doc_id].extend(self.file_term[doc_id][word][:])
                    # else:
                    #     total_idx[word][doc_id] = self.file_term[doc_id][word]
                else:
                    total_idx[word] = {doc_id}
        self.inverted_idx = total_idx

    # # convert a list into list with index
    # # [a, b, c, ...] -> {a:[1,2], b:[3, 4]}
    # @staticmethod
    # def add_indices(data_list):
    #     indices = {}
    #     for idx, word in enumerate(data_list):
    #         if word in indices.keys():
    #             indices[word].append(idx)
    #         else:
    #             indices[word] = [idx]
    #     return indices

    # def make_vectors(self):
    #     for file_id in self.doc_id_to_file_name.keys():
    #         vector = []
    #         for word in self.file_term[file_id].keys():
    #             vector.append(len(self.file_term[file_id][word]))
    #         self.vectors[file_id] = vector

    def doc_vectors(self):
        vectors = {}
        for doc_id in self.file_term.keys():
            vector = []
            for word in self.inverted_idx.keys():
                vector.append(self.get_score(word, doc_id))
            vectors[doc_id] = vector
            self.vectors_length[doc_id] = self.vector_length(vector)
        self.vectors = vectors

    @staticmethod
    def vector_length(vector):
        length = 0
        for x in vector:
            length += x ** 2
        return math.pow(length, 0.5)

    def document_frequency(self, word):
        return len(self.inverted_idx[word].keys()) if word in self.inverted_idx.keys() else 0

    # def vector_length(self):
    #     for file_id in self.doc_id_to_file_name.keys():
    #         length = 0
    #         for x in self.vectors[file_id]:
    #             length += x**2
    #         self.vectors_length[file_id] = pow(length, 0.5)

    # def term_frequency(self, word, doc_id):
    #     return self.tf[doc_id][word] / self.vectors_length[doc_id] if word in self.tf[doc_id].keys() else 0

    def invert_document_frequency(self, document_freq):
        n = self.file_count
        return math.log10(n / document_freq) if document_freq != 0 else 0

    def make_idf(self):
        for word in self.inverted_idx.keys():
            self.idf[word] = self.invert_document_frequency(self.df[word])

    def get_score(self, word, doc_id):
        return math.log(1 + (self.tf[doc_id][word] if word in self.tf[doc_id].keys() else 0)) + self.idf[word]



