import tempfile
from langumo.building import MergeFiles
from langumo.utils import AuxiliaryFile, AuxiliaryFileManager


def test_merging_files_without_loss_of_contents():
    with tempfile.TemporaryDirectory() as tdir, \
            AuxiliaryFileManager(f'{tdir}/tmp') as afm:
        files = [afm.create() for _ in range(10)]
        with AuxiliaryFile.opens(files, 'w') as fps:
            for i, fp in enumerate(fps):
                fp.write(f'{i}\n' * 100)

        with MergeFiles().build(afm, *files).open('r') as fp:
            assert (fp.read().split()
                    == [str(i) for i in range(10) for _ in range(100)])


def test_if_builder_adds_break_lines_automatically():
    with tempfile.TemporaryDirectory() as tdir, \
            AuxiliaryFileManager(f'{tdir}/tmp') as afm:
        files = [afm.create() for _ in range(10)]
        with AuxiliaryFile.opens(files, 'w') as fps:
            for i, fp in enumerate(fps):
                fp.write('\n'.join([str(i) for _ in range(100)]))

        with MergeFiles().build(afm, *files).open('r') as fp:
            assert (fp.read().split()
                    == [str(i) for i in range(10) for _ in range(100)])
