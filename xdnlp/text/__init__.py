from xdnlp.text.prefix_set import PrefixSet
from xdnlp.text.normalize import Normalize
from xdnlp.text.encoder import FeatureEncoder
from joblib import Parallel, delayed
import multiprocessing
import re

n_cpus = multiprocessing.cpu_count()
default_pattern = re.compile("[^\u4E00-\u9FEF\u3400-\u4DB5a-zA-Z0-9]+", re.U)


class Text(object):

    def __init__(self):
        self.ps = PrefixSet()
        self.norm = Normalize()
        self.feature_encoder = FeatureEncoder()
        self.add_keyword = self.ps.add_keyword
        self.add_keywords_from_list = self.ps.add_keywords_from_list
        self.add_keywords_replace_map_from_dict = self.ps.add_keywords_replace_map_from_dict
        self.get_keywords = self.ps.get_keywords
        self.get_replace_map = self.ps.get_replace_map
        self.replace_keywords = self.ps.replace_keywords
        self.remove_keyword = self.ps.remove_keyword
        self.remove_keywords_from_list = self.ps.remove_keywords_from_list
        self.extract_keywords = self.ps.extract_keywords
        self.extract_keywords_with_index = self.ps.extract_keywords_with_index
        self.normalize = self.norm.normalize
        self.pinyin = self.norm.pinyin
        self.encode = self.feature_encoder.encode

    def clean(self, sentence, patten: str = None, keep_space: bool = True, norm: bool = True, lower: bool = True,
              digital_norm: bool = False, max_repeat: int = 0) -> str:
        if patten is None:
            patten = default_pattern
        else:
            patten = re.compile(patten, re.U)
        if norm:
            sentence = self.normalize(sentence)
        if lower:
            sentence = sentence.lower()
        sentence = patten.sub(" ", sentence)
        if keep_space:
            sentence = re.sub(r" +", " ", sentence)
        else:
            sentence = re.sub(r" +", "", sentence)
        if digital_norm:
            sentence = re.sub(r'\d+', '𝝢', sentence)
        if max_repeat > 0:
            sentence = re.sub(r'(.)\1{' + str(max_repeat) + r',}', r'\1' * max_repeat, sentence)
        return sentence

    def batch_extract_keywords(self, sentences, n_jobs=n_cpus, batch_size=1000):
        out = Parallel(n_jobs=n_jobs, verbose=9, batch_size=batch_size)(delayed(self.extract_keywords)(s) for s in sentences)
        return out

    def batch_replace_keywords(self, sentences, n_jobs=n_cpus, batch_size=1000):
        out = Parallel(n_jobs=n_jobs, verbose=9, batch_size=batch_size)(delayed(self.replace_keywords)(s) for s in sentences)
        return out

    def batch_clean(self, sentences, n_jobs=n_cpus, batch_size=1000, patten: str = None, keep_space: bool = True, norm: bool = True,
                    lower: bool = True, digital_norm: bool = False, max_repeat: int = 0):
        out = Parallel(n_jobs=n_jobs, verbose=9, batch_size=batch_size)(
            delayed(self.clean)(s, patten, keep_space, norm, lower, digital_norm, max_repeat) for s in sentences)
        return out

    def batch_cut(self, sentences, tokenizer, n_jobs=n_cpus, verbose=10, batch_size=1000):
        assert hasattr(tokenizer, 'lcut')

        def cut(s):
            return tokenizer.lcut(s)

        out = Parallel(n_jobs=n_jobs, verbose=verbose, batch_size=batch_size)(delayed(cut)(s) for s in sentences)
        return out
