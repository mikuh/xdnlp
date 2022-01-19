from xdnlp.word_discover.ngram import Ngrams
from xdnlp.utils import logging_run_time, read_lines
from xdnlp.utils import default_logger as logging
from collections import Counter
from tqdm import tqdm
import os
import time
import math

settings = {
    "ngram": "ngram.pic",
    "corpus_name": "corpus.txt",
    "char_vocab_name": "char_vocab.txt",
    "ngram_pmi": "pmi.txt",
    "target_file": "new_words.vocab"
}

ngram = Ngrams()

class SimpleTrie:
    """Trie tree structure: used to search the continuous fragments made up of ngrams
    """

    def __init__(self):
        self.root = {}
        self.end = -1

    def insert(self, word):
        """Insert a word into the trie
        """
        curNode = self.root
        for c in word:
            if c not in curNode:
                curNode[c] = {}
            curNode = curNode[c]
        curNode[self.end] = True

    def tokenize(self, sentence):
        result = []
        start, end = 0, 1
        for i, c1 in enumerate(sentence):
            curNode = self.root
            if i == end:
                word = sentence[start: end]
                result.append(word)
                start, end = i, i + 1
            for j, c2 in enumerate(sentence[i:]):
                if c2 in curNode:
                    curNode = curNode[c2]
                    if self.end in curNode:
                        if i + j + 1 > end:
                            end = i + j + 1
                else:
                    break
        result.append(sentence[start: end])
        return result

    def search(self, word):
        curNode = self.root
        for c in word:
            if c not in curNode:
                return False
            curNode = curNode[c]
        # not end
        if self.end not in curNode:
            return False
        return True

    def max_match_cut(self, sentence, reverse=True):
        result = []
        i = len(sentence)
        if reverse:
            while i > 0:
                for j in range(0, i):
                    if self.search(sentence[j: i]) or i - j == 1:
                        result.append(sentence[j: i])
                        i = j
                        break
            return result[::-1]
        while i < len(sentence):
            max_index = i
            curNode = self.root
            for j in range(i, len(sentence)):
                if sentence[j] in curNode:
                    curNode = curNode[sentence[j]]
                    if self.end in curNode:
                        max_index = j
                else:
                    break
            result.append(sentence[i: max_index + 1])
            i = max_index + 1
        return result


class WordDiscover(object):

    def __init__(self, task_name="word-discover", min_pmi: list = [0, 2, 4, 6], min_count=32, pre_func=None):
        self.__run_at = str(int(time.time()))
        self.__save_path = f"./{task_name}-results/{self.__run_at}"
        self.__min_pmi = min_pmi
        self.__min_count = min_count
        self.__pre_func = pre_func
        self.__n = len(min_pmi)
        self.__candidate_trie = SimpleTrie()
        self.valid_ngrams = None
        self.candidates = None

    @logging_run_time
    def word_discover(self, filenames: list, remove_single_char=True, save_ngram=False):
        os.makedirs(self.__save_path)
        ngram.count_ngram(filenames, self.__n, self.__pre_func)
        if save_ngram:
            ngram.to_pickle(os.path.join(self.__save_path, settings["ngram"]))
        self.__filter_ngrams(ngram.ngram_list, ngram.total)
        self.__expansion_filter(filenames, remove_single_char=remove_single_char)
        self.__save()

    @logging_run_time
    def __filter_ngrams(self, ngrams, total):
        """filter the low pmi parts.
        Generate the candidate trie.
        """
        logging.info("Filter the ngrams by pmi, and create the candidate trie... ")
        output_ngrams = Counter()
        with open(os.path.join(self.__save_path, settings["ngram_pmi"]), 'w', encoding='utf-8') as pmi_file:
            for i in range(self.__n - 1, 0, -1):
                for w, v in ngrams[i].items():
                    pmi = min(
                        [total * v / (ngrams[j].get(w[:j + 1], v) * ngrams[i - j - 1].get(w[j + 1:], v))
                         for j in range(i)])
                    if math.log(pmi) >= self.__min_pmi[i]:
                        output_ngrams[w] = v
                        self.__candidate_trie.insert(w)
                    pmi_file.write(f"{w}\t{pmi}\n")
        self.valid_ngrams = output_ngrams

    def __expansion_filter(self, filenames, remove_single_char=True):
        """Extend the vocabulary using the longest match principle,and twice filter.
        """

        n_max = self.__n
        valid_ngrams = self.valid_ngrams

        def twice_filter(candidates):
            """filter the candidates keep the high mi ngrams
            """
            result = Counter()
            for i, j in candidates.items():
                if len(i) < 3:
                    result[i] = j
                elif len(i) <= n_max and i in valid_ngrams:
                    result[i] = j
                elif len(i) > n_max:
                    flag = True
                    for k in range(len(i) + 1 - n_max):
                        if i[k: k + n_max] not in valid_ngrams:
                            flag = False
                    if flag:
                        result[i] = j
            return result

        candidates = Counter()
        logging.info("Start generate the candidates...")
        for filename in filenames:
            for line in tqdm(read_lines(filename, self.__pre_func)):
                # line = "".join(line.strip().split())
                for w in self.__candidate_trie.tokenize(line.strip()):
                    # remove single char
                    if remove_single_char and len(w) < 2:
                        continue
                    candidates[w] += 1
        # filter by word frequency
        candidates = {i: j for i, j in candidates.items() if j >= self.__min_count}
        logging.info("Complete candidates by frequency.")

        # filter by high mutual information ngrams
        candidates = twice_filter(candidates)
        logging.info("Complete filter by mutual information of ngrams")
        logging.info("Generate word candidates successful!")
        self.candidates = candidates
        del candidates

    def __save(self):
        with open(os.path.join(self.__save_path, settings["target_file"]), 'w', encoding='utf-8') as f:
            for i, j in sorted(self.candidates.items(), key=lambda x: -x[1]):
                s = '%s %s\n' % (i, j)
                f.write(s)
        logging.info(f"Save vocab successfully: {os.path.join(self.__save_path, settings['target_file'])}")