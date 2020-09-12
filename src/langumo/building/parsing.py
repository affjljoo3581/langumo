from multiprocessing import Process, Queue
from langumo.building import Builder
from langumo.utils import (AuxiliaryFile, AuxiliaryFileManager, colorful,
                           SentenceSplitter)
from typing import Iterable


class Parser:
    def prepare(self, raw: AuxiliaryFile):
        pass

    def extract(self, raw: AuxiliaryFile) -> Iterable[str]:
        raise NotImplementedError('this method must be implemented by '
                                  'inheritor.')

    def parse(self, text: str) -> str:
        raise NotImplementedError('this method must be implemented by '
                                  'inheritor.')


class ParseRawFile(Builder):
    def __init__(self,
                 parser: Parser,
                 lang: str,
                 min_len: int,
                 max_len: int,
                 newline: str = '[NEWLINE]',
                 num_workers: int = 1):
        self.parser = parser
        self.min_len = min_len
        self.max_len = max_len
        self.newline = newline
        self.num_workers = num_workers
        self.splitter = SentenceSplitter(lang)

    def _parse_worker(self, from_queue: Queue, to_queue: Queue):
        while True:
            # Get raw-formatted document from main process.
            document = from_queue.get()
            if document is None:
                to_queue.put(None)
                break

            # Parse the document to the plain text.
            parsed = self.parser.parse(document)

            # Divide the document into sequences with required length.
            group_sentences = []
            for paragraph in parsed.splitlines():
                for sentence in self.splitter.tokenize(paragraph):
                    group_sentences.append(sentence)

                    if sum(len(s) for s in group_sentences) > self.max_len:
                        to_queue.put(' '.join(group_sentences))
                        group_sentences.clear()

                # Use custom line-break token instead of `\n` which is used for
                # separating sequences.
                if group_sentences:
                    group_sentences.append(self.newline)

            # Use the remainder in dataset if its length is suitable.
            if group_sentences and group_sentences[-1] == self.newline:
                group_sentences = group_sentences[:-1]

            text = ' '.join(group_sentences)
            if len(text) > self.min_len and len(text) < self.max_len:
                to_queue.put(text)

    def _collect_worker(self, parsed: AuxiliaryFile, to_queue: Queue):
        terminated = 0
        with parsed.open('w') as fp:
            while terminated < self.num_workers:
                text = to_queue.get()
                if text is None:
                    terminated += 1
                    continue

                text += '\n' if not text.endswith('\n') else ''
                fp.write(text)

    def build(self, afm: AuxiliaryFileManager, raw: AuxiliaryFile
              ) -> AuxiliaryFile:
        parsed = afm.create()
        self.parser.prepare(raw)

        # Create processes for parsing texts in parallel and a process for
        # collecting the parsed texts and saving to the auxiliary file.
        from_queue, to_queue = Queue(), Queue()
        parsers = [Process(target=self._parse_worker,
                           args=(from_queue, to_queue),
                           daemon=True)
                   for _ in range(self.num_workers)]
        collector = Process(target=self._collect_worker,
                            args=(parsed, to_queue),
                            daemon=True)

        # Start the processes.
        print(colorful.render(f'<r>[*]</r> parse raw-formatted corpus file '
                              f'with <g>{self.parser.__class__.__name__}</g>'))

        for p in parsers:
            p.start()
        collector.start()

        # Feed the extracted raw-formatted document to each parser process.
        for document in self.parser.extract(raw):
            from_queue.put(document)
        for _ in range(self.num_workers):
            from_queue.put(None)

        # Wait for terminating the processes.
        for p in parsers:
            p.join()
        collector.join()

        return parsed
