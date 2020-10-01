"""
Miscellaneous Builders
^^^^^^^^^^^^^^^^^^^^^^

``langumo`` provides a few miscellaneous builders to help constructing the
build pipeline simply. They are not the main implementation of corpus building,
but necessary to compose the pipeline.

.. autoclass:: Sequential
.. autoclass:: ImportFrom
.. autoclass:: ExportTo
.. autoclass:: Residual
.. autoclass:: StackOutputs
"""

import os
import shutil
from langumo.building import Builder
from langumo.utils import AuxiliaryFile, AuxiliaryFileManager, colorful
from typing import Union, Tuple, Iterable


class Sequential(Builder):
    """A sequential container of builders.

    The builders in this container have same auxiliary level. The build outputs
    from each builder will be passed to the next build layer.
    """
    def __init__(self, *builders: Builder):
        self.builders = builders

    def build(self,
              afm: AuxiliaryFileManager,
              *inputs: AuxiliaryFile
              ) -> Union[None, AuxiliaryFile, Tuple[AuxiliaryFile, ...]]:
        with afm.auxiliary_scope():
            outputs = inputs
            for builder in self.builders:
                outputs = builder.build(afm, *outputs)

                # Lock output auxiliary files to protect from deleting for
                # passing to next builder.
                if isinstance(outputs, AuxiliaryFile):
                    outputs.lock()
                    outputs = (outputs,)
                elif isinstance(outputs, tuple):
                    for af in outputs:
                        if not isinstance(af, AuxiliaryFile):
                            raise TypeError(f'element {type(af)} is not an '
                                            f'auxiliary file.')
                        af.lock()
                elif outputs is None:
                    outputs = tuple()
                else:
                    # If the output of builder is not one of the allowed types
                    # (auxiliary file, tuple of auxiliary files, and None) then
                    # throw exception.
                    raise TypeError(f'output type {type(outputs)} from '
                                    f'builder is not allowed.')

                # Delete all unnecessary files except inputs and locked files.
                afm.clear()
        return outputs


class ImportFrom(Builder):
    """Import external files to auxiliary environment.

    This builder imports external files to the auxiliary environment to use in
    other builders. It builds nothing but simply wraps the external files with
    :class:`AuxiliaryFile <langumo.utils.auxiliary.AuxiliaryFile>` and returns
    them for passing to next layers.

    Note:
        The imported auxiliary files are not managed by
        :class:`AuxiliaryFileManager
        <langumo.utils.auxiliary.AuxiliaryFileManager>` to prevent from being
        removed by automatically clean-up.

    Args:
        paths: import file paths.
    """
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
    """Export auxiliary files to external workspace.

    After building somethings, the output auxiliary files would be removed by
    :class:`AuxiliaryFileManager
    <langumo.utils.auxiliary.AuxiliaryFileManager>` 's clean-up. This builder
    exports the output files to the given external paths and returns the given
    auxiliary files identically.

    Note:
        The auxiliary files will be copied to the given export file paths.

    Args:
        paths: export file paths.
    """
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
    """Concatenate the inputs with outputs from sequential layers.

    The given sequential layers are wrapped with :class:`Sequential`
    internally. Due to the reason, the auxiliary level in the builders may be
    increased. This builder returns the given inputs and the outputs from the
    sequential layers.
    """
    def __init__(self, *builders: Builder):
        self.builder = (Sequential(*builders) if len(builders) > 1
                        else builders[0])

    def build(self, afm: AuxiliaryFileManager, *inputs: AuxiliaryFile
              ) -> Tuple[AuxiliaryFile, ...]:
        outputs = self.builder.build(afm, *inputs) or tuple()
        return inputs + outputs


class StackOutputs(Builder):
    """Stack the outputs from the build layers.

    While :class:`Sequential` runs builders by chaining the inputs and their
    outputs, this builder runs them in parallel -- each builder would take the
    same input files which is given to this builder -- and returns the stack of
    the outputs.

    Args:
        builder_group: an iterator of builders or builder sequences.
    """
    def __init__(self,
                 builder_group: Iterable[Union[Builder, Tuple[Builder, ...]]]):
        self.builders = []
        for builders in builder_group:
            if isinstance(builders, tuple):
                if len(builders) == 1:
                    self.builders.append(builders[0])
                else:
                    self.builders.append(Sequential(*builders))
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
