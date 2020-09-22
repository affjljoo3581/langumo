import os
import pytest
import tempfile
from langumo.building import (Builder, Sequential, ImportFrom, ExportTo,
                              Residual, StackOutputs)
from langumo.utils import AuxiliaryFile


class do_nothing(Builder):
    def build(self, afm, *inputs):
        return inputs


class return_none(Builder):
    def build(self, afm, *inputs):
        return None


class return_single_file(Builder):
    def build(self, afm, *inputs):
        return afm.create()


class return_multiple_files(Builder):
    def build(self, afm, *inputs):
        af1 = afm.create()
        af2 = afm.create()
        af3 = afm.create()

        return af1, af2, af3


class return_multiple_files_in_tuple(Builder):
    def build(self, afm, *inputs):
        return tuple(afm.create() for _ in range(10))


class return_integer(Builder):
    def build(self, afm, *inputs):
        return 0


class return_multiple_files_with_integer(Builder):
    def build(self, afm, *inputs):
        return tuple(afm.create() for _ in range(10)) + (0,)


class create_new_file(Builder):
    def __init__(self, *texts: str):
        self.texts = texts

    def build(self, afm, *inputs):
        files = [afm.create() for _ in self.texts]
        with AuxiliaryFile.opens(files, 'w') as fps:
            for i, fp in enumerate(fps):
                fp.write(self.texts[i])
        return tuple(files)


class assert_input_file_contents(Builder):
    def __init__(self, *texts: str):
        self.texts = texts

    def build(self, afm, *inputs):
        assert len(self.texts) == len(inputs)

        with AuxiliaryFile.opens(inputs, 'r') as fps:
            for text, fp in zip(self.texts, fps):
                assert fp.read() == text


class assert_input_files_count(Builder):
    def __init__(self, n: int):
        self.n = n

    def build(self, afm, *inputs):
        assert len(inputs) == self.n


class assert_file_existence(Builder):
    def __init__(self, *names: str):
        self.names = names

    def build(self, afm, *inputs):
        for name in self.names:
            assert os.path.exists(name)


def test_sequential_model_catches_wrong_types():
    with tempfile.TemporaryDirectory() as tdir:
        Sequential(return_none()).run(f'{tdir}/workspace')
        Sequential(return_single_file()).run(f'{tdir}/workspace')
        Sequential(return_multiple_files()).run(f'{tdir}/workspace')
        Sequential(return_multiple_files_in_tuple()).run(f'{tdir}/workspace')

        with pytest.raises(TypeError):
            Sequential(return_integer()).run(f'{tdir}/workspace')
        with pytest.raises(TypeError):
            Sequential(return_multiple_files_with_integer()
                       ).run(f'{tdir}/workspace')


def test_sequential_model_passes_output_files_correctly():
    with tempfile.TemporaryDirectory() as tdir:
        Sequential(
            return_single_file(),
            assert_input_files_count(1)
        ).run(f'{tdir}/workspace')

        Sequential(
            return_multiple_files(),
            assert_input_files_count(3)
        ).run(f'{tdir}/workspace')

        Sequential(
            return_multiple_files_in_tuple(),
            assert_input_files_count(10)
        ).run(f'{tdir}/workspace')


def test_importing_files_from_external():
    with tempfile.TemporaryDirectory() as tdir:
        for i in range(10):
            with open(f'{tdir}/{i}.txt', 'w') as fp:
                fp.write(str(i))

        Sequential(
            ImportFrom(f'{tdir}/0.txt'),
            assert_input_file_contents('0')
        ).run(f'{tdir}/workspace')

        Sequential(
            ImportFrom(f'{tdir}/0.txt', f'{tdir}/1.txt'),
            assert_input_file_contents('0', '1')
        ).run(f'{tdir}/workspace')

        Sequential(
            ImportFrom(*(f'{tdir}/{i}.txt' for i in range(10))),
            assert_input_file_contents(*(str(i) for i in range(10)))
        ).run(f'{tdir}/workspace')


def test_if_imported_files_are_not_removed():
    with tempfile.TemporaryDirectory() as tdir:
        for i in range(10):
            with open(f'{tdir}/{i}.txt', 'w') as fp:
                fp.write(f'{i}')

        Sequential(
            ImportFrom(f'{tdir}/0.txt'),
            # Note that returning nothing may require clearing unused files.
            # Precisely, auxiliary files which are registered to the manager
            # and not returned by the builder would be removed.
            return_none(),
            assert_file_existence(f'{tdir}/0.txt')
        ).run(f'{tdir}/workspace')

        Sequential(
            ImportFrom(*(f'{tdir}/{i}.txt' for i in range(10))),
            return_none(),
            assert_file_existence(*(f'{tdir}/{i}.txt' for i in range(10)))
        ).run(f'{tdir}/workspace')


def test_exporting_files_to_external():
    with tempfile.TemporaryDirectory() as tdir:
        # Test exporting a single file.
        Sequential(
            create_new_file('hello world!'),
            ExportTo(f'{tdir}/output.txt'),
            assert_input_file_contents('hello world!')
        ).run(f'{tdir}/workspace')

        assert os.path.exists(f'{tdir}/output.txt')
        with open(f'{tdir}/output.txt', 'r') as fp:
            assert fp.read() == 'hello world!'

        # Test exporting multiple files.
        Sequential(
            create_new_file(*(str(i) for i in range(10))),
            ExportTo(*(f'{tdir}/{i}.txt' for i in range(10))),
            assert_input_file_contents(*(str(i) for i in range(10)))
        ).run(f'{tdir}/workspace')

        for i in range(10):
            assert os.path.exists(f'{tdir}/{i}.txt')
            with open(f'{tdir}/{i}.txt', 'r') as fp:
                assert fp.read() == str(i)


def test_builder_creates_subdirectories_in_exporting():
    with tempfile.TemporaryDirectory() as tdir:
        Sequential(
            create_new_file('hello world!', '!dlrow olleh'),
            ExportTo(f'{tdir}/build/out1/tmp.txt',
                     f'{tdir}/build/out2/tmp.txt')
        ).run(f'{tdir}/workspace')

        assert os.path.exists(f'{tdir}/build/out1/tmp.txt')
        assert os.path.exists(f'{tdir}/build/out2/tmp.txt')

        with open(f'{tdir}/build/out1/tmp.txt', 'r') as fp:
            assert fp.read() == 'hello world!'
        with open(f'{tdir}/build/out2/tmp.txt', 'r') as fp:
            assert fp.read() == '!dlrow olleh'


def test_residual_builder_concatenates_inputs_and_outputs():
    with tempfile.TemporaryDirectory() as tdir:
        # Test for simple pipeline.
        Sequential(
            create_new_file('hello', 'world!'),
            Residual(
                create_new_file('hello world!')
            ),
            assert_input_file_contents('hello', 'world!', 'hello world!')
        ).run(f'{tdir}/workspace')

        # Test for complex pipelines.
        Sequential(
            create_new_file('hello', 'world!'),
            Residual(
                do_nothing(),
                create_new_file('hello world!', '!dlrow olleh'),
                do_nothing(),
            ),
            assert_input_file_contents('hello', 'world!', 'hello world!',
                                       '!dlrow olleh')
        ).run(f'{tdir}/workspace')

        Sequential(
            create_new_file('hello', 'world!'),
            Residual(
                do_nothing(),
                create_new_file('hello world!', '!dlrow olleh'),
                do_nothing(),
                Residual(
                    do_nothing(),
                    create_new_file('world! hello'),
                    do_nothing(),
                )
            ),
            assert_input_file_contents('hello', 'world!', 'hello world!',
                                       '!dlrow olleh', 'world! hello')
        ).run(f'{tdir}/workspace')


def test_stacking_builder_stacks_outputs_correctly():
    with tempfile.TemporaryDirectory() as tdir:
        Sequential(
            do_nothing(),
            StackOutputs(create_new_file(str(i)) for i in range(10)),
            do_nothing(),
            assert_input_file_contents(*(str(i) for i in range(10)))
        ).run(f'{tdir}/workspace')

        Sequential(
            do_nothing(),
            StackOutputs((create_new_file(str(i)),) for i in range(10)),
            do_nothing(),
            assert_input_file_contents(*(str(i) for i in range(10)))
        ).run(f'{tdir}/workspace')

        Sequential(
            do_nothing(),
            StackOutputs((
                create_new_file(str(i)),
                do_nothing(),
            ) for i in range(10)),
            do_nothing(),
            assert_input_file_contents(*(str(i) for i in range(10)))
        ).run(f'{tdir}/workspace')

        Sequential(
            do_nothing(),
            StackOutputs((
                do_nothing(),
                create_new_file(str(i)),
                Residual(create_new_file(str(i) + str(i))),
                do_nothing(),
            ) for i in range(10)),
            do_nothing(),
            assert_input_file_contents(*(str(i) * j
                                         for i in range(10)
                                         for j in range(1, 3)))
        ).run(f'{tdir}/workspace')
