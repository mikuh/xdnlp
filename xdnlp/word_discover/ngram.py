import pickle
import tqdm
from nltk.util import ngrams
from collections import Counter
from xdnlp.utils import read_lines, logging_run_time


class Ngrams(object):

    def __init__(self):
        self.ngram_list = []
        self.total = 0

    @logging_run_time
    def count_ngram(self, filenames: list, n: int, pre_func=None):
        ngram_list = [Counter() for _ in range(n)]
        total = 0
        for filename in filenames:
            for line in tqdm.tqdm(read_lines(filename, pre_func)):
                end_part = list(" " + line)
                if len(line) >= n:
                    sub_part_list = ngrams(line, n)
                    for sub_part in sub_part_list:
                        total += n
                        for i in range(n):
                            ngram_list[i]["".join(sub_part[:i + 1])] += 1
                    end_part = sub_part
                for i in range(1, l:=len(end_part)):
                    for j in range(i + 1, l + 1):
                        total += 1
                        ngram_list[j - i - 1]["".join(end_part[i:j])] += 1
        self.ngram_list = ngram_list
        self.total = total
        return ngram_list, total

    def to_pickle(self, filename: str):
        with open(filename, 'wb') as f:
            pickle.dump({
                'ngram_list': self.ngram_list,
                'total': self.total
            }, f)


if __name__ == '__main__':
    ng = Ngrams()

    # ngram_list, total = ng.count_ngram("/home/geb/PycharmProjects/word-discovery/data/ro_chat_data.txt", 4)
    # print(ngram_list)
    # ng.to_pickle("ng.pic")

    # from pybolt import bolt_nlp
    #
    # wd = bolt_nlp.WordDiscover()
    #
    # wd.word_discover(["/home/geb/PycharmProjects/word-discovery/data/ro_chat_data.txt"])
