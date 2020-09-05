import os
from langumo.utils import AuxiliaryFile, AuxiliaryFileManager


def _number_of_files_in_directory(path: str) -> int:
    return len([f for f in os.listdir(path)
                if os.path.isfile(os.path.join(path, f))])


def test_afm_context_manager():
    with AuxiliaryFileManager('tmp'):
        assert os.path.exists('tmp')
    assert not os.path.exists('tmp')


def test_afm_creates_files_correctly():
    with AuxiliaryFileManager('tmp') as afm:
        tfile = afm.create()

        with tfile.open('w') as fp:
            fp.write('hello world!')
        with tfile.open('r') as fp:
            assert fp.read() == 'hello world!'

        assert os.path.exists(tfile.name)
        assert _number_of_files_in_directory('tmp') == 1
    assert not os.path.exists('tmp')


def test_afm_ignores_locked_files_in_clearing():
    with AuxiliaryFileManager('tmp') as afm:
        for _ in range(10):
            afm.create()
        assert _number_of_files_in_directory('tmp') == 10

        for _ in range(5):
            afm.create().lock()
        assert _number_of_files_in_directory('tmp') == 15

        # All auxiliary files except locked ones would be removed. Note that
        # the remainders are unlocked at this point.
        afm.clear()
        assert _number_of_files_in_directory('tmp') == 5

        # As mentioned above, all unlocked files would be remove at this point.
        afm.clear()
        assert _number_of_files_in_directory('tmp') == 0
    assert not os.path.exists('tmp')


def test_afm_handles_files_separately_by_level():
    with AuxiliaryFileManager('tmp') as afm:
        # Create auxiliary files in level 0.
        for _ in range(10):
            afm.create()
        assert _number_of_files_in_directory('tmp') == 10

        with afm.auxiliary_scope():
            # Create auxiliary files in level 1.
            for _ in range(5):
                afm.create()
            assert _number_of_files_in_directory('tmp') == 15

            # Remove the auxiliary files with level 1.
            afm.clear()
            assert _number_of_files_in_directory('tmp') == 10

            # Create auxiliary files and lock some of them.
            for _ in range(2):
                afm.create()
            for _ in range(3):
                afm.create().lock()
            assert _number_of_files_in_directory('tmp') == 15

            with afm.auxiliary_scope():
                # Create auxiliary files in level 2.
                for _ in range(5):
                    afm.create()
                assert _number_of_files_in_directory('tmp') == 20

            # Not only non-locked files but also sub-level auxiliary files
            # would be removed.
            afm.clear()
            assert _number_of_files_in_directory('tmp') == 13

        afm.clear()
        assert _number_of_files_in_directory('tmp') == 0


def test_opening_multiple_auxiliary_files_at_once():
    with AuxiliaryFileManager('tmp') as afm:
        files = [afm.create() for _ in range(10)]

        with AuxiliaryFile.opens(files, 'w') as fps:
            for i, fp in enumerate(fps):
                fp.write(f'{i}th file')

        with AuxiliaryFile.opens(files, 'r') as fps:
            for i, fp in enumerate(fps):
                assert fp.read() == f'{i}th file'
