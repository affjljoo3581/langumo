from langumo.utils import AuxiliaryFile, AuxiliaryFileManager
from typing import Union, Tuple


class Builder:
    def build(self,
              afm: AuxiliaryFileManager,
              *inputs: AuxiliaryFile
              ) -> Union[None, AuxiliaryFile, Tuple[AuxiliaryFile, ...]]:
        raise NotImplementedError('this method must be implemented by '
                                  'inheritor.')

    def run(self, parent: str):
        with AuxiliaryFileManager(parent) as afm:
            self.build(afm)

            # After running the build pipeline, delete all created dummy files
            # even though the remainders would be removed in `__exit__` of the
            # manager.
            afm.clear()
