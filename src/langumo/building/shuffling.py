import tqdm
import random
import shutil
from langumo.building import Builder
from langumo.utils import AuxiliaryFile, AuxiliaryFileManager, colorful
from typing import List


class ShuffleLines(Builder):
    def __init__(self, best_seek_cnt: int = 100000, max_buckets: int = 512):
        self.best_seek_cnt = best_seek_cnt
        self.max_buckets = max_buckets

    def _total_lines_in_file(self, af: AuxiliaryFile) -> int:
        total_lines = 0
        with af.open('rb') as fp:
            for _ in fp:
                total_lines += 1
        return total_lines

    def _collect_seek_offsets(self, af: AuxiliaryFile, stride: int
                              ) -> List[int]:
        offsets = []
        with af.open('rb') as fp:
            while True:
                current = fp.tell()

                # Read `stride` lines and move to the end of the chunk. If the
                # last line in the chunk is empty, then it means current is the
                # last of entire chunks.
                lines = [fp.readline() for _ in range(stride)]
                if not lines[-1]:
                    break

                # Gather the current position to the collection.
                offsets.append(current)
        return offsets

    def build(self, afm: AuxiliaryFileManager, corpus: AuxiliaryFile
              ) -> AuxiliaryFile:
        # Calculate the optimum stride and bucket size.
        stride = max(
            1, self._total_lines_in_file(corpus) // self.best_seek_cnt)
        buckets = [afm.create()
                   for _ in range(min(stride * 2, self.max_buckets))]

        # Collect the corresponding seeking positions and shuffle them.
        offsets = self._collect_seek_offsets(corpus, stride)
        random.shuffle(offsets)

        with corpus.open('rb') as src, \
                AuxiliaryFile.opens(buckets, 'wb') as dsts:
            # Create tqdm progress bar with colorful description.
            tqdm_iter = tqdm.tqdm(
                offsets,
                desc=colorful.render('<r>[*]</r> shuffle raw corpus file'))

            for offset in tqdm_iter:
                src.seek(offset)

                for _ in range(stride):
                    line = src.readline()
                    if not line:
                        break

                    # Add break-line character to the end of text to avoid
                    # being merged with other line.
                    line += b'\n' if not line.endswith(b'\n') else b''

                    # Write the decorated text line to the random bucket for
                    # ensuring randomness.
                    dsts[random.randint(0, len(dsts) - 1)].write(line)

        # After splitting to the buckets, merge them into a single file.
        merged = afm.create()
        with merged.open('wb') as dst, \
                AuxiliaryFile.opens(buckets, 'rb') as srcs:
            for src in srcs:
                shutil.copyfileobj(src, dst)

        return merged
