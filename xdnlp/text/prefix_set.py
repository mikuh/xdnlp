

class PrefixSet(object):

    def __init__(self):
        self._prefix_dic = {}
        self._replace_map = {}

    def get_keywords(self):
        return {w for w, f in self._prefix_dic.items() if f == 1}

    def get_replace_map(self):
        return {a: b for a, b in self._replace_map.items() if b is not None}

    def add_keywords_from_list(self, words: list):
        for word in words:
            self.add_keyword(word)

    def add_keyword(self, word):
        w = ""
        for ch in word:
            w += ch
            if w not in self._prefix_dic:
                self._prefix_dic[w] = 0
        self._prefix_dic[w] = 1

    def add_keywords_replace_map_from_dict(self, source_target_map: dict):
        for a, b in source_target_map.items():
            w = ""
            for ch in a:
                w += ch
                if w not in self._replace_map:
                    self._replace_map[w] = None
            self._replace_map[a] = b

    def remove_keywords_from_list(self, words: list):
        for word in words:
            self.remove_keyword(word)

    def remove_keyword(self, word: str):
        self._prefix_dic[word] = 0

    def extract_keywords(self, sentence: str, longest_only=False) -> list:
        """Extract keywords involved in sentences
        Args:
            sentence: str, Sentences to be extracted.
            longest_only: bool,Whether to match only the longest keyword,default False;
                        for a example sentence: `category`, and keywords is ['cat', 'category'],
                        if set False, return: ['cat', 'category'],
                        if set True, return the longest only: ['category']
        """
        N = len(sentence)
        keywords = []
        for i in range(N):
            flag = sentence[i]
            j = i
            word = None
            while j < N and (flag in self._prefix_dic):
                if self._prefix_dic[flag] == 1:
                    if not longest_only:
                        keywords.append(flag)
                    else:
                        word = flag
                j += 1
                flag = sentence[i: j + 1]
            if longest_only and word:
                keywords.append(word)
        return keywords

    def extract_keywords_with_index(self, sentence: str, longest_only=False):
        N = len(sentence)
        keywords = []
        for i in range(N):
            flag, index = sentence[i], [i, i + 1]
            j = i
            word = None
            while j < N and (flag in self._prefix_dic):
                if self._prefix_dic[flag] == 1:
                    if not longest_only:
                        keywords.append((flag, index))
                    else:
                        word, _index = flag, index
                j += 1
                flag, index = sentence[i: j + 1], [i, j + 1]
            if longest_only and word:
                keywords.append((word, _index))
        return keywords

    def replace_keywords(self, sentence: str) -> str:
        """Replace word use keywords map.
        Args:
            sentence: str, Sentences that need to replace keywords.
        Return:
            the new sentence after replace keywords.
        """
        N = len(sentence)
        new_sentence = ""
        i = 0
        while i < N:
            flag = sentence[i]
            j = i
            word = None
            while j < N and (flag in self._replace_map):
                if self._replace_map[flag]:
                    word = flag
                j += 1
                flag = sentence[i: j + 1]
            if word:
                new_sentence += self._replace_map[word]
                i = j
            else:
                new_sentence += sentence[i]
                i += 1
        return new_sentence