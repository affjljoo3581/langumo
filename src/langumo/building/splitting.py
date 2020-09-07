import math
import shutil
from langumo.building import Builder
from langumo.utils import AuxiliaryFile, AuxiliaryFileManager, colorful
from typing import Tuple


class SplitValidation(Builder):
    def __init__(self, val_ratio: float = 0.1):
        self.val_ratio = val_ratio

    def _total_lines_in_file(self, af: AuxiliaryFile) -> int:
        total_lines = 0
        with af.open('rb') as fp:
            for _ in fp:
                total_lines += 1
        return total_lines

    def build(self, afm: AuxiliaryFileManager, corpus: AuxiliaryFile
              ) -> Tuple[AuxiliaryFile, AuxiliaryFile]:
        train_dataset = afm.create()
        val_dataset = afm.create()

        total_lines = self._total_lines_in_file(corpus)
        print(colorful.render(f'<r>[*]</r> split validation corpus - '
                              f'<m>{math.ceil(total_lines * self.val_ratio)} '
                              f'</m> of <m>{total_lines}</m> lines'))

        with corpus.open('rb') as src, train_dataset.open('wb') as tdst, \
                val_dataset.open('wb') as vdst:
            # Write the first `val_ratio` lines to the validation dataset file.
            for i, line in enumerate(src):
                vdst.write(line)
                if i + 1 >= total_lines * self.val_ratio:
                    break

            # After writing the validation dataset, copy the entire rest lines
            # to the train dataset.
            shutil.copyfileobj(src, tdst)

        return train_dataset, val_dataset
