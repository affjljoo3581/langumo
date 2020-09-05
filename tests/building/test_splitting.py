from langumo.building import SplitValidation
from langumo.utils import AuxiliaryFileManager


def test_counting_lines_in_file():
    with AuxiliaryFileManager('tmp') as afm:
        builder = SplitValidation()
        corpus = afm.create()

        # Test for the case of 10 lines.
        with corpus.open('w') as fp:
            fp.write('hello world!\n' * 10)
        assert builder._total_lines_in_file(corpus) == 10

        # Test for the case of 100 lines.
        with corpus.open('w') as fp:
            fp.write('hello world!\n' * 100)
        assert builder._total_lines_in_file(corpus) == 100

        # Test for the case of 1548 lines.
        with corpus.open('w') as fp:
            fp.write('hello world!\n' * 1548)
        assert builder._total_lines_in_file(corpus) == 1548


def test_builder_splits_corpus_without_loss_of_contents():
    with AuxiliaryFileManager('tmp') as afm:
        corpus = afm.create()
        with corpus.open('w') as fp:
            fp.write('\n'.join(str(i) for i in range(1000)))

        # Test the splitting builder with various ratios.
        tfile, vfile = SplitValidation(val_ratio=0.1).build(afm, corpus)
        with tfile.open('r') as tfp, vfile.open('r') as vfp:
            assert ([int(s.strip()) for s in vfp.readlines()]
                    == list(range(100)))
            assert ([int(s.strip()) for s in tfp.readlines()]
                    == list(range(100, 1000)))

        tfile, vfile = SplitValidation(val_ratio=0.27).build(afm, corpus)
        with tfile.open('r') as tfp, vfile.open('r') as vfp:
            assert ([int(s.strip()) for s in vfp.readlines()]
                    == list(range(270)))
            assert ([int(s.strip()) for s in tfp.readlines()]
                    == list(range(270, 1000)))

        tfile, vfile = SplitValidation(val_ratio=0.1387).build(afm, corpus)
        with tfile.open('r') as tfp, vfile.open('r') as vfp:
            assert ([int(s.strip()) for s in vfp.readlines()]
                    == list(range(139)))
            assert ([int(s.strip()) for s in tfp.readlines()]
                    == list(range(139, 1000)))
