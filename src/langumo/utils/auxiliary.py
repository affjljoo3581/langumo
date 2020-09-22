import os
import shutil
import random
import string
import contextlib
from typing import IO, List, Container, ContextManager


class AuxiliaryFile:
    def __init__(self, name: str):
        self.name = name
        self.locked = False

    def lock(self):
        self.locked = True
        return self

    def open(self, mode: str = 'r') -> IO:
        return open(self.name, mode)

    @staticmethod
    @contextlib.contextmanager
    def opens(files: List['AuxiliaryFile'], mode: str = 'r'
              ) -> ContextManager[List[IO]]:
        files = [f.open(mode) for f in files]
        try:
            yield files
        finally:
            for f in files:
                f.close()


class AuxiliaryFileManager:
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
        file = AuxiliaryFile(self._create_random_filename())
        self.files.append((file, self.auxiliary_level))

        # Create an empty file.
        with open(file.name, 'w') as fp:
            fp.close()

        return file

    def synchronize(self, files: Container[AuxiliaryFile]):
        for i, (af, level) in enumerate(self.files):
            if af in files:
                self.files[i] = (af, self.auxiliary_level)

    @contextlib.contextmanager
    def auxiliary_scope(self):
        self.auxiliary_level += 1
        try:
            yield
        finally:
            self.auxiliary_level -= 1

    def clear(self):
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
        # Remove the parent workspace directory and its sub-files.
        shutil.rmtree(self.parent)
