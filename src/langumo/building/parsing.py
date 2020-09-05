from multiprocessing import Process, Queue
from langumo.building import Builder
from langumo.utils import AuxiliaryFile, AuxiliaryFileManager, colorful
from typing import Union, Iterable


class Parser:
    def prepare(self, raw: AuxiliaryFile):
        pass

    def extract(self, raw: AuxiliaryFile) -> Iterable[str]:
        raise NotImplementedError('this method must be implemented by '
                                  'inheritor.')

    def parse(self, text: str) -> Union[str, Iterable[str]]:
        raise NotImplementedError('this method must be implemented by '
                                  'inheritor.')


class ParseRawFile(Builder):
    def __init__(self,
                 parser: Parser,
                 num_workers: int = 1):
        self.parser = parser
        self.num_workers = num_workers

    def _parse_worker(self, from_queue: Queue, to_queue: Queue):
        while True:
            # Get raw-formatted document text from main process.
            document = from_queue.get()
            if document is None:
                to_queue.put(None)
                break

            # Parse and clean the raw-formatted document text to plain text.
            parsed = self.parser.parse(document)
            if isinstance(parsed, str):
                parsed = [parsed]

            # Return the parsed text to main process.
            for p in parsed:
                to_queue.put(p)

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
        print(colorful.render('<r>[*]</r> parse raw-formatted corpus file'))

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
