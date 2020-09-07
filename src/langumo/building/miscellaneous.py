import os
import shutil
from langumo.building import Builder, BuildPipeline
from langumo.utils import AuxiliaryFile, AuxiliaryFileManager, colorful
from typing import Union, Tuple, Iterable


class ImportFrom(Builder):
    def __init__(self, *paths: str):
        self.paths = paths

    def build(self, afm: AuxiliaryFileManager, *inputs: AuxiliaryFile
              ) -> AuxiliaryFile:
        # Note that an imported files would be wrapped with `AuxiliaryFile`
        # directly. Because the files are not created by `AuxiliaryFileManager`
        # but brought simply from existing external files, they do not need to
        # be removed. Namely, the manager does not have the ownership of them.
        files = []
        for path in self.paths:
            print(colorful.render(f'<r>[*]</r> import file from '
                                  f'<b>{path}</b>'))
            files.append(AuxiliaryFile(path))
        return tuple(files)


class ExportTo(Builder):
    def __init__(self, *paths: str):
        self.paths = paths

    def build(self, afm: AuxiliaryFileManager, *inputs: AuxiliaryFile
              ) -> Union[None, AuxiliaryFile, Tuple[AuxiliaryFile, ...]]:
        if len(inputs) != len(self.paths):
            raise ValueError('number of predifined exporting files are not '
                             'matched to the given auxiliary files.')

        # Save the auxiliary files to the exporting paths.
        for af, path in zip(inputs, self.paths):
            # Create an exporting directory if not exist.
            parent = os.path.dirname(path)
            if parent != '' and not os.path.exists(parent):
                os.makedirs(parent, exist_ok=True)

            print(colorful.render(f'<r>[*]</r> export the processed file to '
                                  f'<b>{path}</b>'))
            shutil.copyfile(af.name, path)

        return inputs


class Residual(Builder):
    def __init__(self, *builders: Builder):
        self.builder = (BuildPipeline(*builders) if len(builders) > 1
                        else builders[0])

    def build(self, afm: AuxiliaryFileManager, *inputs: AuxiliaryFile
              ) -> Tuple[AuxiliaryFile, ...]:
        outputs = self.builder.build(afm, *inputs) or tuple()
        return inputs + outputs


class StackOutputs(Builder):
    def __init__(self,
                 builder_group: Iterable[Union[Builder, Tuple[Builder, ...]]]):
        self.builders = []
        for builders in builder_group:
            if isinstance(builders, tuple):
                if len(builders) == 1:
                    self.builders.append(builders[0])
                else:
                    self.builders.append(BuildPipeline(*builders))
            else:
                self.builders.append(builders)

    def build(self, afm: AuxiliaryFileManager, *inputs: AuxiliaryFile
              ) -> Tuple[AuxiliaryFile, ...]:
        outputs = tuple()
        for builder in self.builders:
            outputs += builder.build(afm, *inputs)
            afm.synchronize(outputs)

            # Lock input and stacked output auxiliary files.
            for af in inputs + outputs:
                af.lock()
            afm.clear()
        return outputs
