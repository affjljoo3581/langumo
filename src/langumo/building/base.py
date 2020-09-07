from langumo.utils import AuxiliaryFile, AuxiliaryFileManager
from typing import Union, Tuple


class Builder:
    def build(self,
              afm: AuxiliaryFileManager,
              *inputs: AuxiliaryFile
              ) -> Union[None, AuxiliaryFile, Tuple[AuxiliaryFile, ...]]:
        raise NotImplementedError('this method must be implemented by '
                                  'inheritor.')


class BuildPipeline(Builder):
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

    def run(self, parent: str):
        with AuxiliaryFileManager(parent) as afm:
            self.build(afm)

            # After running the build pipeline, delete all created dummy files
            # even though the remainders would be removed in `__exit__` of the
            # manager.
            afm.clear()
