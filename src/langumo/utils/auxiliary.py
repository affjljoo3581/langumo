r"""
Auxiliary File System
=====================

Overview
--------

To build corpus dataset, each procedure requires temporary files to store data
in disk, not memory. While the scale of each corpus is increased, we faced to
handle enormously large files. There is no problem to save all temporary files
and remove after the build with small corpora. However, if we store them with
extremely large ones thoughtlessly, **low disk space error** may be occurred.

Hence, we designed **Auxiliary File System** which manages temporary (or
literally, auxiliary) files simply and automatically. It manages whole
auxiliary files created from their manager. The manager records their
auxiliary-scope level to determine which one is currently in unused state and
removes the files that are in unused state for cleaning-up. Every
:class:`Builder <langumo.building.base.Builder>`\s use :class:`AuxiliaryFile`\s
in build.

Reference
---------

.. autoclass:: AuxiliaryFile
    :members:

.. autoclass:: AuxiliaryFileManager
    :members:
"""

import os
import shutil
import random
import string
import contextlib
from typing import IO, List, Container, ContextManager


class AuxiliaryFile:
    """An auxiliary file object.

    Note:
        It is not recommended to create this class directly without
        :class:`AuxiliaryFileManager`.

    Args:
        name: auxiliary file name.
    """
    def __init__(self, name: str):
        self.name = name
        self.locked = False

    def lock(self):
        """Lock the file to prevent from deleting."""
        self.locked = True
        return self

    def open(self, mode: str = 'r') -> IO:
        """Open the auxiliary file."""
        return open(self.name, mode)

    @staticmethod
    @contextlib.contextmanager
    def opens(files: List['AuxiliaryFile'], mode: str = 'r'
              ) -> ContextManager[List[IO]]:
        """Open multiple auxiliary files at once."""
        files = [f.open(mode) for f in files]
        try:
            yield files
        finally:
            for f in files:
                f.close()


class AuxiliaryFileManager:
    """Auxiliary file manager.

    Args:
        parent: parent workspace directory which will be used for
            containing auxiliary files.
    """
    def __init__(self, parent: str):
        self.files = []
        self.parent = parent
        self.auxiliary_level = 0

        # Create parent workspace directory.
        os.makedirs(parent)

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    def _create_random_filename(self) -> str:
        while True:
            # Create random filename which is a combination of digits and lower
            # case letters.
            name = os.path.join(self.parent, ''.join(
                random.choices(string.digits + string.ascii_lowercase, k=16)))

            if all(name != af.name for af, _ in self.files):
                return name

    def create(self) -> AuxiliaryFile:
        """Create new auxiliary file.

        The auxiliary file is usually used as a temporary file. It will be
        created in ``parent`` directory and have current **auxiliary level**. 

        Returns:
            new auxiliary file object.
        """
        file = AuxiliaryFile(self._create_random_filename())
        self.files.append((file, self.auxiliary_level))

        # Create an empty file.
        with open(file.name, 'w') as fp:
            fp.close()

        return file

    def synchronize(self, files: Container[AuxiliaryFile]):
        """Synchronize auxiliary levels to current.

        Some files created in lower :meth:`auxiliary_scope <auxiliary_scope>`
        need to be handled as higher-scope ones. It synchronizes the auxiliary
        levels of the given files to current scope level.
        """
        for i, (af, level) in enumerate(self.files):
            if af in files:
                self.files[i] = (af, self.auxiliary_level)

    @contextlib.contextmanager
    def auxiliary_scope(self):
        """Returns a context manager which increases the auxiliary level."""
        self.auxiliary_level += 1
        try:
            yield
        finally:
            self.auxiliary_level -= 1

    def clear(self):
        """Remove unused auxiliary files.

        AuxiliaryFileManager automatically traces unused auxiliary files and
        remove them to manage the disk space. The manager determines that
        auxiliary files which are non-locked and have lower auxiliary-scope
        level -- not created in current scope -- are in unused state and
        unnecessary ones. If some files should be preserved, use
        :meth:`lock <AuxiliaryFile.lock>` and
        :meth:`synchronize <synchronize>`.
        """
        for af, level in self.files.copy():
            # Skip clearing high-level files.
            if level < self.auxiliary_level:
                continue

            if af.locked:
                # If the auxiliary file is locked, then skip deleting and
                # unlock it.
                af.locked = False
            else:
                self.files.remove((af, level))
                os.remove(af.name)

    def close(self):
        """Close the auxiliary manager and cleanup the workspace directory."""
        # Remove the parent workspace directory and its sub-files.
        shutil.rmtree(self.parent)
