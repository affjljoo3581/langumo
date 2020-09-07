import json
from langumo.building import Parser
from langumo.utils import AuxiliaryFile
from typing import Iterable


class EscapedJSONStringParser(Parser):
    def extract(self, raw: AuxiliaryFile) -> Iterable[str]:
        with raw.open('r') as fp:
            for line in fp:
                if not line.strip():
                    continue

                yield line

    def parse(self, text: str) -> str:
        text, _ = json.decoder.scanstring(text, 1)
        return text
