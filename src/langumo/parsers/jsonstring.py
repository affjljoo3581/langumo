"""
Escaped JSON-Style String
^^^^^^^^^^^^^^^^^^^^^^^^^

In `json`_ package, :func:`json.encoder.encode_basestring` encodes a Python
string to a JSON-style representation. Especially line-break characters are
escaped to ``\\n``. It helps to separate documents which consists of multi-line
paragraphs by line-break delimiter.

.. _json: https://docs.python.org/3/library/json.html

.. autoclass:: EscapedStringParser
    :show-inheritance:
"""

import re
import json
from langumo.building import Parser
from langumo.utils import AuxiliaryFile
from typing import Iterable


class EscapedStringParser(Parser):
    """Escaped JSON-Style String Parser.

    This parser normalizes the contents by removing duplicated spaces, empty
    lines and replacing irregular quotes to normal ones ('' and "").
    """

    single_quotes_pattern = re.compile('[\x60\xb4\u2018\u2019]')
    double_quotes_pattern = re.compile('[\u201c\u201d]')

    def extract(self, raw: AuxiliaryFile) -> Iterable[str]:
        with raw.open('r') as fp:
            for line in fp:
                if not line.strip():
                    continue

                yield line

    def parse(self, text: str) -> str:
        text, _ = json.decoder.scanstring(text, 1)

        filtered = []
        for line in text.strip().splitlines():
            if not line:
                continue

            # Remove duplicated spaces.
            line = line.replace('\n', ' ').replace('\t', ' ')
            while '  ' in line:
                line = line.replace('  ', ' ')

            # Normalize the quotes by replacing unusual ones to the standard
            # ones.
            line = EscapedStringParser.single_quotes_pattern.sub('\'', line)
            line = EscapedStringParser.double_quotes_pattern.sub('"', line)

            filtered.append(line)

        return '\n'.join(filtered)
