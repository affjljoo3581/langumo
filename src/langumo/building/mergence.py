"""
Mergence
^^^^^^^^

All parsed plain text files should be merged into a single file to handle them
as an unified large corpus data.

.. autoclass:: MergeFiles
"""

from langumo.building import Builder
from langumo.utils import AuxiliaryFile, AuxiliaryFileManager, colorful


class MergeFiles(Builder):
    """Merge files into a single one.

    Note:
        All documents are separated by new-line character(``\\n``) and this
        builder automatically appends the new-line character to avoid mixing
        the last document of a file and the first document of another one.
    """

    def build(self, afm: AuxiliaryFileManager, *inputs: AuxiliaryFile
              ) -> AuxiliaryFile:
        merged = afm.create()

        print(colorful.render(f'<r>[*]</r> merge <m>{len(inputs)}</m> files '
                              f'into one'))
        with merged.open('wb') as dst, \
                AuxiliaryFile.opens(inputs, 'rb') as srcs:
            for src in srcs:
                for line in src:
                    # Add break-line character to the end of text to avoid
                    # being merged with other line.
                    line += b'\n' if not line.endswith(b'\n') else b''

                    dst.write(line)

        return merged
