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
    a = sh.simhash_array("3a374a4a73ef4a4a4a45455eda5eda66e25eda5edab3125eda6a746c6a746ce86c027e027e027ee8f0e6e8f0746c6a746c3de86c31ade86c3de8f0e6e8f0e6247844027ec044027ec044027ec044027ec044027ec044027ec044027ec044027ec0f4a0247844027ec044027ec044027ec044027ec044027ec0f4a024a06a746c6a746ce86c0000e86c242e243e3ea0aaa0e8f0e6e8f0e66a746c6a746c3de8f0746c247844027ec044027ec044027ec044027ec044027ec044027ec044027ec044027ec044027ec044027ec044027ec044027ec044027ec0f424a0a0e8f0e6e86c246a746c784424023d7e24027ea0a0c04424023d7e24027ea0a0c04424023d7e24027ea0a0c04424023d7e24027ea0a0c04424023d7e24027ea0a0c04424023d7e24027ea0a0c04424023d7e24027ea0a0c04424023d7e24027ea0a0c04424023d7e24027ea0a0c04424023d7e24027ea0a0c04424023d7e24027ea0a0c04424023d7e24027ea0a0c04424023d7e24027ea0a0c04424023d7e24027ea0a0c04424023d7e24027ea0a0c04424023d7e24027ea0a0c04424023d7e24027ea0a0c04424023d7e24027ea0a0c04424023d7e24027ea0a0c04424023d7e24027ea0a0c0f4e86ce8f0e6a05edae8f0e6246a746c6a746c24a024a0e8f0746c6a746c3de86c2454d054d054d054d054d0a024a0e8f0746c6a746c023d7ee86c023d7ee8f0e6e8f0e6e8f0e6e86c6a746c24a024a0e8f0746c3de8f0746c242424a0a024a024027ea024a0a0e8f0e6e8f0e6a0246a746c246a746c6a746c6a6b746c243d1324027ea0a0e86c24132413a0a0e86c242413a0a0e8f0e7e6e8f0e6e86ce8f0e6a05edae86c6a746c023d7ee8f0746c245eda6a4463df027ec04463df027ec04463df027ec04463df027ec04463df027ec04463df027ec04463df027ec04463df027ec04463df027ec04463df027ec04463df027ec04463df027ec0e65edaa0e8f0e6e8f0e6a0245eda2444c044c0a02424027e027e027e027e027e027e027e027e027e027e027e027e027e027e027e027e027e027e027e027e027ea024027e027e027e027e027e027e027e027e027e027e027e027e027e027e027e027e027e027e027ea0a0a06a746c2454027e63dfd0541363dfd0a0e8f0e65eda24247844c044c044027ec044133dc0f4a0a08eb6")
    print(a)
    b = sh.simhash_array("3a374a4a73ef4a4a4a45455eda5eda66e25eda5eda5edab3125eda6a746c6a746ce86c027e027e027ee8f0e6e8f0746c6a746c3de86c31ade86c3de8f0e6e8f0e6247844027ec044027ec044027ec044027ec044027ec044027ec044027ec044027ec0f4a0247844027ec044027ec044027ec044027ec044027ec0f4a024a06a746c6a746ce86c0000e86c242e243e3ea0aaa0e8f0e6e8f0e66a746c6a746c3de8f0746c247844027ec044027ec044027ec044027ec044027ec044027ec044027ec044027ec044027ec044027ec044027ec044027ec044027ec0f424a0a0e8f0e6e86c246a746c784424023d7e24027ea0a0c04424023d7e24027ea0a0c04424023d7e24027ea0a0c04424023d7e24027ea0a0c04424023d7e24027ea0a0c04424023d7e24027ea0a0c04424023d7e24027ea0a0c04424023d7e24027ea0a0c04424023d7e24027ea0a0c04424023d7e24027ea0a0c04424023d7e24027ea0a0c04424023d7e24027ea0a0c04424023d7e24027ea0a0c04424023d7e24027ea0a0c04424023d7e24027ea0a0c04424023d7e24027ea0a0c04424023d7e24027ea0a0c04424023d7e24027ea0a0c04424023d7e24027ea0a0c04424023d7e24027ea0a0c0f4e86ce8f0e6a05edae8f0e6246a746c6a746c24a024a0e8f0746c6a746c3de86c2454d054d054d054d054d0a024a0e8f0746c6a746c023d7ee86c023d7ee8f0e6e8f0e6e8f0e6e86c6a746c24a024a0e8f0746c3de8f0746c242424a0a024a024027ea024a0a0e8f0e6e8f0e6a0246a746c246a746c6a746c6a6b746c243d1324027ea0a0e86c24132413a0a0e86c242413a0a0e8f0e7e6e8f0e6e86ce8f0e6a05edae86c6a746c023d7ee8f0746c245eda6a4463df027ec04463df027ec04463df027ec04463df027ec04463df027ec04463df027ec04463df027ec04463df027ec04463df027ec04463df027ec04463df027ec04463df027ec0e65edaa0e8f0e6e8f0e6a0245eda2444c044c0a02424027e027e027e027e027e027e027e027e027e027e027e027e027e027e027e027e027e027e027e027e027ea024027e027e027e027e027e027e027e027e027e027e027e027e027e027e027e027e027e027e027ea0a0a06a746c2454027e63dfd0541363dfd0a0e8f0e65eda24247844c044c044027ec044133dc0f4a0a08eb6")

    print(b)
