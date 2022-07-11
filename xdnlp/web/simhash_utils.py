import hashlib
import numpy as np
from itertools import groupby


class SimHash(object):

    def __init__(self, bits=64, width=4, batch_size=200, large_weight_cutoff=50):
        self.bits = bits
        self.width = width
        self.batch_size = batch_size
        self.large_weight_cutoff = large_weight_cutoff
        self.f_bytes = bits // 8

    def simhash(self, s: str) -> int:
        bin_array = self.simhash_array(s)
        return self._bytes_to_int(np.packbits(bin_array).tobytes())

    def simhashasarray(self, s: str) -> np.ndarray:
        features = self._tokenize(s)
        features = {k: sum(1 for _ in g) for k, g in groupby(sorted(features))}

        sums = []
        batch = []
        count = 0
        w = 1
        if isinstance(features, dict):
            features = features.items()

        for f in features:
            skip_batch = False
            if not isinstance(f, str):
                f, w = f
                skip_batch = w > self.large_weight_cutoff or not isinstance(w, int)
            count += w

            h = self.md5(f)[-self.f_bytes:]

            if skip_batch:
                sums.append(self._bitarray_from_bytes(h) * w)
            else:
                batch.append(h * w)
                if len(batch) >= self.batch_size:
                    sums.append(self._sum_hashes(batch))
                    batch = []

            if len(sums) >= self.batch_size:
                sums = [np.sum(sums, 0)]

        if batch:
            sums.append(self._sum_hashes(batch))

        combined_sums = np.sum(sums, 0)
        return (combined_sums > count / 2) * 1

    def simhash_array(self, s: str) -> np.ndarray:
        features = self._tokenize(s)
        features = {k: sum(1 for _ in g) for k, g in groupby(sorted(features))}
        sums = []
        batch = []
        count = 0
        w = 1
        f_bytes = self.bits // 8
        for f in features:
            count += w
            h = self.md5(f)[-f_bytes:]

            batch.append(h * w)
            if len(batch) >= self.batch_size:
                sums.append(self._sum_hashes(batch))
                batch = []

            if len(sums) >= self.batch_size:
                sums = [np.sum(sums, 0)]

        if batch:
            sums.append(self._sum_hashes(batch))

        combined_sums = np.sum(sums, 0)
        return (combined_sums > count / 2) * 1

    def simhash_string(self, s: str) -> str:
        return np.array2string(self.simhash_array(s), separator="_", max_line_width=500)

    def _tokenize(self, s: str):
        ans = self._slide(s)
        return ans

    def _slide(self, content, width=4):
        return [content[i:i + width] for i in range(max(len(content) - width + 1, 1))]

    def _sum_hashes(self, digests):
        bitarray = self._bitarray_from_bytes(b''.join(digests))
        rows = np.reshape(bitarray, (-1, self.bits))
        return np.sum(rows, 0)

    def md5(self, s: str):
        return hashlib.md5(s.encode('utf-8')).digest()

    def md5string(self, s: str):
        return hashlib.md5(s.encode('utf-8')).hexdigest()

    @staticmethod
    def _bitarray_from_bytes(b):
        return np.unpackbits(np.frombuffer(b, dtype='>B'))

    @staticmethod
    def _bytes_to_int(b):
        return int.from_bytes(b, 'big')

    def hamming_distance(self, a: int, b: int) -> int:
        x = (a ^ b) & ((1 << self.bits) - 1)
        ans = 0
        while x:
            ans += 1
            x &= x - 1
        return ans


if __name__ == '__main__':
    sh = SimHash()
    a = sh.simhash_array(
        "3a 37 73 ef 66 e2 b3 12 24 78 44 02 7e c0 44 02 7e c0 44 02 7e c0 44 02 7e c0 44 02 7e c0 44 02 7e c0 44 02 7e c0 44 02 7e c0 f4 24 02 3d 7e a0 a0 24 31 ad 32 ae 54 02 7e d0 54 d0 54 02 7e 02 7e 02 7e 02 7e 02 7e 02 7e 02 7e 02 7e d0 a0 a0 8e b6".replace(
            " ", ''))
    print(a)
    b = sh.simhash_array(
        "3a 37 4a 73 ef 4a 4a 45 17 5e da 93 b3 12 24 24 24 24 24 6a 74 6c 3d e8 6c 24 02 7e 02 7e a0 e8 f0 e6 24 25 1e 02 54 d0 7e 9a 1e 02 54 d0 7e 9a 1e 02 54 d0 7e 9a 1e 02 54 d0 7e 9a 1e 02 54 d0 7e 9a 1e 02 54 d0 7e 9a 1e 02 54 d0 7e 9a 1e 02 54 d0 7e 9a a1 24 a0 a0 a0 24 6a 74 6c 24 24 63 df a0 a0 e8 6c 4f 55 55 55 28 a4 cb e8 f0 e6 a0 24 24 24 78 44 02 7e c0 44 02 7e c0 44 02 7e c0 44 02 7e c0 44 02 7e c0 44 02 7e c0 44 02 7e c0 44 02 7e c0 44 02 7e c0 44 02 7e c0 44 02 7e c0 44 02 7e c0 44 02 7e c0 44 02 7e c0 44 02 7e c0 f4 a0 24 24 63 df a0 24 54 54 d0 54 d0 54 02 7e d0 54 d0 54 d0 d0 a0 a0 a0 24 24 24 a0 24 54 54 3d d0 54 d0 54 d0 63 02 7e df d0 36 b2 a0 36 b2 a0 24 24 a0 24 24 78 44 02 7e c0 44 02 7e c0 44 02 7e c0 44 02 7e c0 44 02 7e c0 44 02 7e c0 f4 a0 a0 a0 24 24 a0 24 24 78 44 02 7e c0 44 02 7e c0 44 02 7e c0 44 02 7e c0 44 02 7e c0 44 02 7e c0 f4 a0 a0 a0 24 24 a0 24 24 78 44 02 7e c0 44 02 7e c0 44 02 7e c0 44 02 7e c0 44 02 7e c0 44 02 7e c0 f4 a0 a0 a0 24 24 a0 24 24 78 44 02 7e c0 44 02 7e c0 44 02 7e c0 44 02 7e c0 44 02 7e c0 44 02 7e c0 f4 a0 a0 a0 24 24 a0 24 24 78 44 02 7e c0 44 02 7e c0 44 02 7e c0 44 02 7e c0 44 02 7e c0 44 02 7e c0 f4 a0 a0 a0 24 24 a0 24 24 78 44 02 7e c0 44 02 7e c0 44 02 7e c0 44 02 7e c0 44 02 7e c0 44 02 7e c0 f4 a0 a0 a0 36 b2 a0 36 b2 a0 24 6a 74 6c 24 02 7e 02 7e 02 7e 02 7e 02 7e 02 7e 02 7e 02 7e 02 7e 02 7e 02 7e 02 7e 02 7e 02 7e 02 7e 02 7e 02 7e 02 7e 02 7e 02 7e 02 7e 02 7e 02 7e 02 7e 02 7e 02 7e 02 7e 02 7e 02 7e 02 7e 02 7e 02 7e 02 7e 02 7e 02 7e 02 7e 02 7e 02 7e 02 7e 02 7e 02 7e 02 7e 02 7e 02 7e 02 7e 02 7e 02 7e 02 7e 02 7e 02 7e 02 7e 02 7e 02 7e 02 7e 02 7e 02 7e 02 7e 02 7e 02 7e 02 7e 02 7e 02 7e 02 7e 02 7e 02 7e 02 7e 02 7e 02 7e 02 7e 02 7e 02 7e 02 7e a0 24 24 02 7e a0 5e da 5e da a0 e8 f0 e6 a0 a0 a0 a0 a0 8e b6".replace(
            " ", ''))

    print(b)
