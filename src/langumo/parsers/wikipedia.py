import re
import bz2
import mwparserfromhell as mw
import xml.etree.cElementTree as etree
from langumo.building import Parser
from langumo.utils import AuxiliaryFile, SentenceSplitter
from typing import Iterable, Union, List


class WikipediaParser(Parser):
    brackets_pattern = re.compile(r'\([^(]*?\)')
    single_quotes_pattern = re.compile('[\x60\xb4\u2018\u2019]')
    double_quotes_pattern = re.compile('[\u201c\u201d]')

    def __init__(self, min_len: int, max_len: int):
        self.splitter = None
        self.namespaces = []
        self.min_len = min_len
        self.max_len = max_len

    def prepare(self, raw: AuxiliaryFile):
        with bz2.open(raw.name, 'r') as fp:
            context = etree.iterparse(fp, events=('start', 'end'))

            # Find a language code of wikipedia dump file.
            _, root = next(context)
            for name, value in root.items():
                if name.endswith('lang'):
                    self.splitter = SentenceSplitter(value)
                    break

            # Collect namespaces from the dump file.
            for event, elem in context:
                if event != 'end':
                    continue

                if elem.tag.endswith('namespace'):
                    if elem.text is not None:
                        self.namespaces.append(elem.text)

                # Exit the loop if the parser meets the end of `<namespaces>`
                # tag.
                if elem.tag.endswith('namespaces'):
                    break

    def extract(self, raw: AuxiliaryFile) -> Iterable[str]:
        with bz2.open(raw.name, 'r') as fp:
            context = etree.iterparse(fp, events=('start', 'end'))
            _, root = next(context)

            # Parse articles from the dump file and yield them.
            prefix_pattern = re.compile(r'({.*?})')
            for event, elem in context:
                if event != 'end' or not elem.tag.endswith('page'):
                    continue

                # Skip the article which does not have namespace of 0.
                prefix = prefix_pattern.match(elem.tag).group(0)
                if elem.find(f'./{prefix}ns').text != '0':
                    root.clear()
                    continue

                # Get a mediawiki code of the article content.
                article = elem.find(f'./{prefix}revision/{prefix}text').text
                root.clear()

                if article is None or article.lower().startswith('#redirect'):
                    continue

                yield article

    def _clean_mediawiki_text(self, text: str) -> List[str]:
        # Parse mediawiki code by using `mwparserfromhell` and create
        # namespace-based wiki-link pattern.
        wiki = mw.parse(text)
        mw_nslinks_pattern = re.compile(
            '^(?:{}):'.format('|'.join(self.namespaces)), re.IGNORECASE)

        # Simple remove wrapper function.
        def remove_element(section, obj):
            try:
                section.remove(obj)
            except ValueError:
                pass

        # Filter functions to remove from mediawiki code.
        def filter_wikilinks(obj):
            return bool(mw_nslinks_pattern.match(str(obj.title)))

        def filter_templates(obj):
            return obj.name.lower() in {'reflist', 'notelist', 'notelist-ua',
                                        'notelist-lr', 'notelist-ur',
                                        'notelist-lg'}

        def filter_tags(obj):
            return str(obj.tag) in {'ref', 'table'}

        section_text = []
        for section in wiki.get_sections(flat=True, include_lead=True):
            # Remove elements filtered by above functions.
            for obj in section.ifilter_wikilinks(matches=filter_wikilinks,
                                                 recursive=True):
                remove_element(section, obj)
            for obj in section.ifilter_templates(matches=filter_templates,
                                                 recursive=True):
                remove_element(section, obj)
            for obj in section.ifilter_tags(matches=filter_tags,
                                            recursive=True):
                remove_element(section, obj)

            # Add cleaned mediawiki-based contents.
            section_text.append(section.strip_code().strip())

        return section_text

    def parse(self, text: str) -> Union[str, Iterable[str]]:
        section_text = self._clean_mediawiki_text(text)

        # Post-process parsed wikipedia article contents.
        filtered = []
        for text in section_text:
            for line in text.strip().splitlines():
                # Check if the text has normal punctuation.
                if not line or line[-1] not in '!?.':
                    continue

                # Remove nested brackets and unnecessary spaces.
                while WikipediaParser.brackets_pattern.search(line):
                    line = WikipediaParser.brackets_pattern.sub('', line)

                line = line.replace('\n', ' ').replace('\t', ' ')
                while '  ' in line:
                    line = line.replace('  ', ' ')

                # Normalize the quotes by replacing unusual ones to the
                # standard ones.
                line = WikipediaParser.single_quotes_pattern.sub('\'', line)
                line = WikipediaParser.double_quotes_pattern.sub('"', line)

                filtered += self.splitter.tokenize(line)

        # Merge the splitted sentences to have normalized lengths.
        groups = [[]]
        for text in filtered:
            text = text.strip()
            if sum(len(s) for s in groups[-1]) + len(text) > self.max_len:
                groups.append([])
            groups[-1].append(text)

        groups = [' '.join(sentences) for sentences in groups]
        groups = [sentences for sentences in groups
                  if len(sentences) > self.min_len]

        return groups
