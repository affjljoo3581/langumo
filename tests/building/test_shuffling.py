from langumo.building import ShuffleLines
from langumo.utils import AuxiliaryFileManager


def test_counting_lines_in_file():
    with AuxiliaryFileManager('tmp') as afm:
        builder = ShuffleLines()
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


def test_builder_collects_seeking_positions_correctly():
    with AuxiliaryFileManager('tmp') as afm:
        # Create an auxiliary file with 1000 dummy lines.
        corpus = afm.create()
        with corpus.open('w') as fp:
            fp.write('hello world!\n' * 1000)

        builder = ShuffleLines()
        for s in range(1, 200):
            assert len(builder._collect_seek_offsets(corpus, s)) == 1000 // s


def test_shuffling_preserves_contents():
    with AuxiliaryFileManager('tmp') as afm:
        corpus = afm.create()
        with corpus.open('w') as fp:
            fp.write('\n'.join([str(i) for i in range(1000)]) + '\n')

        # In this case, the size of each chunk is 1 and it implies `complete
        # random shuffling`.
        with (ShuffleLines(best_seek_cnt=1000, max_buckets=512)
              .build(afm, corpus)
              .open('r')) as fp:
            assert {int(i) for i in fp.read().split()} == set(range(1000))

        # If `best_seek_cnt` is less than the entire text lines, then the
        # shuffling would be approximated by using chunks and their buckets.
        with (ShuffleLines(best_seek_cnt=100, max_buckets=512)
              .build(afm, corpus)
              .open('r')) as fp:
            assert {int(i) for i in fp.read().split()} == set(range(1000))

        with (ShuffleLines(best_seek_cnt=10, max_buckets=512)
              .build(afm, corpus)
              .open('r')) as fp:
            assert {int(i) for i in fp.read().split()} == set(range(1000))

        # However, if `max_buckets` is less than the optimum bucket size (twice
        # of the optimum stride size), then only `max_buckets` of buckets would
        # be used. Note that this case leads reduction of randomness.
        with (ShuffleLines(best_seek_cnt=10, max_buckets=64)
              .build(afm, corpus)
              .open('r')) as fp:
            assert {int(i) for i in fp.read().split()} == set(range(1000))


def test_shuffling_without_break_line_in_last():
    with AuxiliaryFileManager('tmp') as afm:
        corpus = afm.create()
        with corpus.open('w') as fp:
            # Note that we would not add break-line character to the end of the
            # content.
            fp.write('\n'.join([str(i) for i in range(1000)]))

        with (ShuffleLines(best_seek_cnt=1000, max_buckets=512)
              .build(afm, corpus)
              .open('r')) as fp:
            assert {int(i) for i in fp.read().split()} == set(range(1000))

        with (ShuffleLines(best_seek_cnt=10, max_buckets=64)
              .build(afm, corpus)
              .open('r')) as fp:
            assert {int(i) for i in fp.read().split()} == set(range(1000))
