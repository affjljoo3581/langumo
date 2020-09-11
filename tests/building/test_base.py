import pytest
import tempfile
from langumo.building import Builder, BuildPipeline


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


class assert_input_files(Builder):
    def __init__(self, n: int):
        self.n = n

    def build(self, afm, *inputs):
        assert len(inputs) == self.n


def test_build_pipeline_catches_wrong_types():
    with tempfile.TemporaryDirectory() as tdir:
        BuildPipeline(return_none()).run(f'{tdir}/workspace')
        BuildPipeline(return_single_file()).run(f'{tdir}/workspace')
        BuildPipeline(return_multiple_files()).run(f'{tdir}/workspace')
        BuildPipeline(return_multiple_files_in_tuple()
                      ).run(f'{tdir}/workspace')

        with pytest.raises(TypeError):
            BuildPipeline(return_integer()).run(f'{tdir}/workspace')
        with pytest.raises(TypeError):
            BuildPipeline(return_multiple_files_with_integer()
                          ).run(f'{tdir}/workspace')


def test_build_pipeline_passes_output_files_correctly():
    with tempfile.TemporaryDirectory() as tdir:
        BuildPipeline(
            return_single_file(),
            assert_input_files(1)
        ).run(f'{tdir}/workspace')

        BuildPipeline(
            return_multiple_files(),
            assert_input_files(3)
        ).run(f'{tdir}/workspace')

        BuildPipeline(
            return_multiple_files_in_tuple(),
            assert_input_files(10)
        ).run(f'{tdir}/workspace')
