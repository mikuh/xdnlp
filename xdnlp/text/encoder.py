import re
import os
from xdnlp.utils import package_path, read_lines
from xdnlp.text import Normalize, PrefixSet

norm = Normalize()


class FeatureEncoder(object):

    def __init__(self):
        self.feature_contact_pattern = r"([a-zA-Z\d,-,@,\.]{6,24})|[v微q扣]|(wx)|(weixin)"
        self.feature_unknown_pattern = r"[^\u0020-\u007e\u4e00-\u9fa5a-zA-Z\d]"
        self.feature_chinese_pattern = r"[\u0020-\u007e\u4e00-\u9fa5]"
        self.feature_en_num_pattern = r"[a-zA-Z0-9]"
        self.feature_not_chinese_pattern = r"[^\u0020-\u007e\u4e00-\u9fa5]"
        self.lfs = 1300
        self.prefix_set = PrefixSet()
        self.prefix_set.add_keywords_from_list(self._load_specify())
        self._chinese_frequency = self._load_chinese_frequency()

    def _load_specify(self):
        keywords = set()
        for line in read_lines(os.path.join(package_path, "data/ad.txt")):
            keywords.add(norm.pinyin(line.strip()))
        return list(keywords)

    def _load_chinese_frequency(self):
        chinese_frequency = {}
        for line in read_lines(os.path.join(package_path, "data/chinese_frequency.tsv")):
            t = line.split("\t")
            if len(t) > 1:
                chinese_frequency[t[0]] = int(t[1])
        return chinese_frequency

    def chinese_frequency(self, character: str) -> int:
        return self._chinese_frequency.get(character, 0)

    def chinese_frequency_list(self, sentence: str) -> list:
        return [self._chinese_frequency[c] for c in sentence if c in self._chinese_frequency]

    def feature_contact(self, text: str, pattern: str = None) -> int:
        if pattern is None:
            pattern = self.feature_contact_pattern
        if re.search(pattern, text):
            return 1
        return 0

    def feature_unknown(self, text: str, pattern: str = None) -> int:
        if pattern is None:
            pattern = self.feature_unknown_pattern
        if re.search(pattern, text):
            return 1
        else:
            return 0

    def feature_specify(self, text: str) -> int:
        if len(self.prefix_set.extract_keywords(text)) > 0:
            return 1
        return 0

    def feature_low_frequency(self, text: str) -> int:
        for c in text:
            if self._chinese_frequency.get(c, 20000) < 1300:
                return 1
        return 0

    def encode(self, text: str) -> dict:
        features = {'contact': self.feature_contact(text),
                    'unknown': self.feature_unknown(text),
                    'specify': self.feature_specify(text),
                    'length': len(text),
                    'low_frequency': 0,
                    'zh_scale': 0,
                    'en_num_scale': 0,
                    'zh_piece_scale': 0,
                    'not_zh_piece_scale': 0,
                    'pinyin': norm.pinyin(text, sep="")}
        total_count = 0
        zh_count = 0
        en_num_count = 0
        unknow_count = 0
        zh_pieces = re.split(self.feature_not_chinese_pattern, text)
        for character in text:
            if self._chinese_frequency.get(character, 10000) < self.lfs:
                features['low_frequency'] += 1
            if re.match(self.feature_chinese_pattern, character):
                zh_count += 1
                total_count += 1
            elif re.match(self.feature_en_num_pattern, character):
                en_num_count += 1/5
                total_count += 1/5
            elif re.match(self.feature_unknown_pattern, character):
                unknow_count += 1
                total_count += 1
        features["zh_scale"] = zh_count / total_count
        features["en_num_scale"] = en_num_count / total_count
        features["zh_piece_scale"] = len(zh_pieces) / (zh_count + 1)

        return features


if __name__ == '__main__':
    encoder = FeatureEncoder()

    print(encoder.feature_contact("v"))

    print(encoder.chinese_frequency_list("伽企鹅輑、フちqlフq、冲置二浙（格猫金、Zeny）套餐可选"))
    print(encoder.feature_unknown("伽企鹅輑、フちqlフq、冲置二浙（格猫金、Zeny）套餐可选"))
    print(encoder.feature_low_frequency("伽企鹅輑、フちqlフq、冲置二浙（格猫金、Zeny）套餐可选"))

    print(encoder.encode("wo操你妈、フちqlフq、"))