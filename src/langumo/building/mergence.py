from langumo.building import Builder
from langumo.utils import AuxiliaryFile, AuxiliaryFileManager, colorful


class MergeFiles(Builder):
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
