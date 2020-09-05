from langumo.utils import colorful
from typing import List


class SentenceSplitter:
    def __init__(self, lang: str):
        self.lang = lang
        self._splitter = None

        # Prepare prerequisite resources for sentence tokenizers.
        if lang == 'en':
            import nltk

            try:
                nltk.data.find('tokenizers/punkt')
            except LookupError:
                print(colorful.render('<r>[*]</r> prepare resources for '
                                      '<b>splitting sentences</b>'))

                nltk.download('punkt')

    def _initialize(self):
        if self.lang == 'en':
            import nltk

            # NLTK tokenizer needs pre-downloaded resources.
            nltk.data.find('tokenizers/punkt')
            self._splitter = nltk.tokenize.sent_tokenize
        elif self.lang == 'ko':
            import kss
            self._splitter = kss.split_sentences

    def tokenize(self, text: str) -> List[str]:
        if self._splitter is None:
            self._initialize()

        return list(self._splitter(text))
