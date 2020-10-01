from langumo.utils import AuxiliaryFile, AuxiliaryFileManager
from typing import Union, Tuple


class Builder:
    """Abstract base class of build layer."""

    def build(self,
              afm: AuxiliaryFileManager,
              *inputs: AuxiliaryFile
              ) -> Union[None, AuxiliaryFile, Tuple[AuxiliaryFile, ...]]:
        """Build something with input files.

        Note:
            This method must be implemented.

        Args:
            afm: auxiliary file manager in current context and layer.
            inputs: input auxiliary files for building.

        Returns:
            build output auxiliary files.
        """
        raise NotImplementedError('this method must be implemented by '
                                  'inheritor.')

    def run(self, parent: str):
        """Execute the builder.

        All builders can be executed directly and independently, without any
        input auxiliary files. We recommend to execute builders with
        miscellaneous ones (e.g.
        :class:`ImportFrom <langumo.building.miscellaneous.ImportFrom>` and
        :class:`ExportTo <langumo.building.miscellaneous.ExportTo>`) to pass
        build inputs correctly.

        Args:
            parent: parent workspace directory which will be used for
                containing all auxiliary files.
        """
        with AuxiliaryFileManager(parent) as afm:
            self.build(afm)

            # After running the build pipeline, delete all created dummy files
            # even though the remainders would be removed in `__exit__` of the
            # manager.
            afm.clear()
