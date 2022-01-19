from nltk.util import ngrams
from collections import Counter
from xdnlp.utils import read_lines
import math
import joblib
import tqdm

class Gibberish(object):

    def __init__(self):
        self.counts = Counter()
        self.total = 0
        self.threshold = 0

    def adapt(self, filename: str, total=None):
        for line in tqdm.tqdm(read_lines(filename), total=total):
            for a, b in ngrams(line, 2):
                self.counts[a + b] += 1
                self.total += 1

    def adapt_threshold(self, goodfile: str, badfile: str):
        good = [self.average_prob(line) for line in read_lines(goodfile)]
        bad = [self.average_prob(line) for line in read_lines(badfile)]
        assert min(good) > max(bad)
        self.threshold = (min(good) + max(bad)) / 2

    def average_prob(self, query):
        assert self.total > 0, "Gibberish: should adapt first"
        pt = 0
        t = 0
        for a, b in ngrams(query, 2):
            p = self.counts.get(a + b, 1) / self.total
            pt += math.log(p)
            t += 1
        return pt / t

    def load(self, filename: str):
        t = joblib.load(filename)
        self.counts = t.get("counts", self.counts)
        self.total = t.get("total", self.total)
        self.threshold = t.get("threshold", self.threshold)

    def predict(self, query):
        assert self.total > 0, "Gibberish: should adapt first"
        assert self.threshold != 0, "Gibberish: should set threshold first"
        return self.average_prob(query) > self.threshold

    def save(self, filename):
        assert self.total > 0, "Gibberish: should adapt first"
        assert self.threshold != 0, "Gibberish: should set threshold first"
        joblib.dump({"counts": self.counts, "total": self.total, "threshold": self.threshold}, filename)


if __name__ == '__main__':
    gib = Gibberish()
    # gib.adapt("/home/geb/PycharmProjects/xdnlp/local/gibberish_data/data.txt")
    # joblib.dump({"counts": gib.counts, "total": gib.total}, "gib.model")
    gib.load("gib.model")
    e = gib.average_prob("ahsfuia")
    print(e)
    e = gib.average_prob("good")
    print(e)
    e = gib.average_prob("我是你爹")
    print(e)
    e = gib.average_prob("竺諸聞瀧韋")
    print(e)

    e = gib.average_prob("一起喵喵猫")
    print(e)

    e = gib.average_prob("熙熙菋菂夏天")
    print(e)

    e = gib.average_prob("碎花今如梦")
    print(e)

    e = gib.average_prob("若懷ほ稽")
    print(e)
