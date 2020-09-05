import os
import shutil
from langumo.building import (Builder, BuildPipeline, ImportFrom, ExportTo,
                              Residual, StackOutputs)
from langumo.utils import AuxiliaryFile


class do_nothing(Builder):
    def build(self, afm, *inputs):
        return inputs


class return_none(Builder):
    def build(self, afm, *inputs):
        return None


class create_new_file(Builder):
    def __init__(self, *texts: str):
        self.texts = texts

    def build(self, afm, *inputs):
        files = [afm.create() for _ in self.texts]
        with AuxiliaryFile.opens(files, 'w') as fps:
            for i, fp in enumerate(fps):
                fp.write(self.texts[i])
        return tuple(files)


class assert_input_files(Builder):
    def __init__(self, *texts: str):
        self.texts = texts

    def build(self, afm, *inputs):
        assert len(self.texts) == len(inputs)

        with AuxiliaryFile.opens(inputs, 'r') as fps:
            for text, fp in zip(self.texts, fps):
                assert fp.read() == text


class assert_file_existence(Builder):
    def __init__(self, *names: str):
        self.names = names

    def build(self, afm, *inputs):
        for name in self.names:
            assert os.path.exists(name)


def test_importing_files_from_external():
    for i in range(10):
        with open(f'{i}.txt', 'w') as fp:
            fp.write(str(i))

    BuildPipeline(ImportFrom('0.txt'),
                  assert_input_files('0')).run('tmp')
    BuildPipeline(ImportFrom('0.txt', '1.txt'),
                  assert_input_files('0', '1')).run('tmp')
    BuildPipeline(ImportFrom(*(f'{i}.txt' for i in range(10))),
                  assert_input_files(*(str(i) for i in range(10)))).run('tmp')

    # Remove the temporary files.
    for i in range(10):
        os.remove(f'{i}.txt')


def test_if_imported_files_are_not_removed():
    for i in range(10):
        with open(f'{i}.txt', 'w') as fp:
            fp.write(f'{i}')

    BuildPipeline(ImportFrom('0.txt'),
                  # Note that returning nothing may require clearing unused
                  # files. Precisely, auxiliary files which are registered to
                  # the manager and not returned by the builder would be
                  # removed.
                  return_none(),
                  assert_file_existence('0.txt')).run('tmp')

    BuildPipeline(ImportFrom(*(f'{i}.txt' for i in range(10))),
                  return_none(),
                  assert_file_existence(*(f'{i}.txt' for i in range(10)))) \
        .run('tmp')

    # Remove the temporary files.
    for i in range(10):
        os.remove(f'{i}.txt')


def test_exporting_files_to_external():
    # Test exporting a single file.
    BuildPipeline(create_new_file('hello world!'),
                  ExportTo('output.txt'),
                  assert_input_files('hello world!')).run('tmp')

    assert os.path.exists('output.txt')
    with open('output.txt', 'r') as fp:
        assert fp.read() == 'hello world!'

    # Test exporting multiple files.
    BuildPipeline(create_new_file(*(str(i) for i in range(10))),
                  ExportTo(*(f'{i}.txt' for i in range(10))),
                  assert_input_files(*(str(i) for i in range(10)))).run('tmp')

    for i in range(10):
        assert os.path.exists(f'{i}.txt')
        with open(f'{i}.txt', 'r') as fp:
            assert fp.read() == str(i)

    # Remove the exported files.
    os.remove('output.txt')
    for i in range(10):
        os.remove(f'{i}.txt')


def test_builder_creates_subdirectories_in_exporting():
    BuildPipeline(create_new_file('hello world!', '!dlrow olleh'),
                  ExportTo('build/out1/tmp.txt', 'build/out2/tmp.txt')) \
        .run('tmp')

    assert os.path.exists('build/out1/tmp.txt')
    assert os.path.exists('build/out2/tmp.txt')

    with open('build/out1/tmp.txt', 'r') as fp:
        assert fp.read() == 'hello world!'
    with open('build/out2/tmp.txt', 'r') as fp:
        assert fp.read() == '!dlrow olleh'

    shutil.rmtree('build')


def test_residual_builder_concatenates_inputs_and_outputs():
    # Test for simple pipeline.
    BuildPipeline(
        create_new_file('hello', 'world!'),
        Residual(
            create_new_file('hello world!')
        ),
        assert_input_files('hello', 'world!', 'hello world!')
    ).run('tmp')

    # Test for complex pipelines.
    BuildPipeline(
        create_new_file('hello', 'world!'),
        Residual(
            do_nothing(),
            create_new_file('hello world!', '!dlrow olleh'),
            do_nothing(),
        ),
        assert_input_files('hello', 'world!', 'hello world!', '!dlrow olleh')
    ).run('tmp')

    BuildPipeline(
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
        assert_input_files('hello', 'world!', 'hello world!', '!dlrow olleh',
                           'world! hello')
    ).run('tmp')


def test_stacking_builder_stacks_outputs_correctly():
    BuildPipeline(
        do_nothing(),
        StackOutputs(create_new_file(str(i)) for i in range(10)),
        do_nothing(),
        assert_input_files(*(str(i) for i in range(10)))
    ).run('tmp')

    BuildPipeline(
        do_nothing(),
        StackOutputs((create_new_file(str(i)),) for i in range(10)),
        do_nothing(),
        assert_input_files(*(str(i) for i in range(10)))
    ).run('tmp')

    BuildPipeline(
        do_nothing(),
        StackOutputs((
            create_new_file(str(i)),
            do_nothing(),
        ) for i in range(10)),
        do_nothing(),
        assert_input_files(*(str(i) for i in range(10)))
    ).run('tmp')

    BuildPipeline(
        do_nothing(),
        StackOutputs((
            do_nothing(),
            create_new_file(str(i)),
            Residual(create_new_file(str(i) + str(i))),
            do_nothing(),
        ) for i in range(10)),
        do_nothing(),
        assert_input_files(*(str(i) * j
                             for i in range(10) for j in range(1, 3)))
    ).run('tmp')
