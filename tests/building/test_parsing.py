from langumo.building import Parser, ParseRawFile
from langumo.utils import AuxiliaryFile, AuxiliaryFileManager, SentenceSplitter
from typing import Union, Iterable


_dummy_corpus_content = (
    'Wikipedia is a multilingual online encyclopedia created and maintained '
    'as an open collaboration project by a community of volunteer editors '
    'using a wiki-based editing system. It is the largest and most popular '
    'general reference work on the World Wide Web. It is also one of the 15 '
    'most popular websites ranked by Alexa, as of August 2020. It features '
    'exclusively free content and no commercial ads. It is hosted by the '
    'Wikimedia Foundation, a non-profit organization funded primarily through '
    'donations.\n'
    'Wikipedia was launched on January 15, 2001, and was created by Jimmy '
    'Wales and Larry Sanger. Sanger coined its name as a portmanteau of the '
    'terms "wiki" and "encyclopedia". Initially an English-language '
    'encyclopedia, versions of Wikipedia in other languages were quickly '
    'developed. With 6.1 million articles, the English Wikipedia is the '
    'largest of the more than 300 Wikipedia encyclopedias. Overall, Wikipedia '
    'comprises more than 54 million articles attracting 1.5 billion unique '
    'visitors per month.\n\n'
    'In 2005, Nature published a peer review comparing 42 hard science '
    'articles from Encyclopædia Britannica and Wikipedia and found that '
    'Wikipedia\'s level of accuracy approached that of Britannica, although '
    'critics suggested that it might not have fared so well in a similar '
    'study of a random sampling of all articles or one focused on social '
    'science or contentious social issues. The following year, Time stated '
    'that the open-door policy of allowing anyone to edit had made Wikipedia '
    'the biggest and possibly the best encyclopedia in the world, and was a '
    'testament to the vision of Jimmy Wales.\n'
    'Wikipedia has been criticized for exhibiting systemic bias and for being '
    'subject to manipulation and spin in controversial topics; Edwin Black '
    'has criticized Wikipedia for presenting a mixture of "truth, half truth, '
    'and some falsehoods". Wikipedia has also been criticized for gender '
    'bias, particularly on its English-language version, where the dominant '
    'majority of editors are male. However, edit-a-thons have been held to '
    'encourage female editors and increase the coverage of women\'s topics. '
    'Facebook announced that by 2017 it would help readers detect fake news '
    'by suggesting links to related Wikipedia articles. YouTube announced a '
    'similar plan in 2018.'
)


class simple_parser(Parser):
    def extract(self, raw: AuxiliaryFile) -> Iterable[str]:
        with raw.open('r') as fp:
            articles = fp.read().split('\n\n')
            yield from articles

    def parse(self, text: str) -> str:
        return text


def test_formatted_file_parsing():
    with AuxiliaryFileManager('tmp') as afm:
        corpus = afm.create()
        with corpus.open('w') as fp:
            fp.write(_dummy_corpus_content)

        with (ParseRawFile(simple_parser(), lang='en', min_len=16, max_len=512,
                           newline='[NEWLINE]', num_workers=2)
              .build(afm, corpus)
              .open('r')) as fp:
            assert ({s.strip() for s in fp} == {
                     'Wikipedia is a multilingual online encyclopedia created '
                     'and maintained as an open collaboration project by a '
                     'community of volunteer editors using a wiki-based '
                     'editing system. It is the largest and most popular '
                     'general reference work on the World Wide Web. It is '
                     'also one of the 15 most popular websites ranked by '
                     'Alexa, as of August 2020. It features exclusively free '
                     'content and no commercial ads. It is hosted by the '
                     'Wikimedia Foundation, a non-profit organization funded '
                     'primarily through donations. [NEWLINE] Wikipedia was '
                     'launched on January 15, 2001, and was created by Jimmy '
                     'Wales and Larry Sanger.',
                     'Sanger coined its name as a portmanteau of the terms '
                     '"wiki" and "encyclopedia". Initially an '
                     'English-language encyclopedia, versions of Wikipedia in '
                     'other languages were quickly developed. With 6.1 '
                     'million articles, the English Wikipedia is the largest '
                     'of the more than 300 Wikipedia encyclopedias. Overall, '
                     'Wikipedia comprises more than 54 million articles '
                     'attracting 1.5 billion unique visitors per month.',
                     'In 2005, Nature published a peer review comparing 42 '
                     'hard science articles from Encyclopædia Britannica and '
                     'Wikipedia and found that Wikipedia\'s level of accuracy '
                     'approached that of Britannica, although critics '
                     'suggested that it might not have fared so well in a '
                     'similar study of a random sampling of all articles or '
                     'one focused on social science or contentious social '
                     'issues. The following year, Time stated that the '
                     'open-door policy of allowing anyone to edit had made '
                     'Wikipedia the biggest and possibly the best '
                     'encyclopedia in the world, and was a testament to the '
                     'vision of Jimmy Wales.',
                     'Wikipedia has been criticized for exhibiting systemic '
                     'bias and for being subject to manipulation and spin in '
                     'controversial topics; Edwin Black has criticized '
                     'Wikipedia for presenting a mixture of "truth, half '
                     'truth, and some falsehoods". Wikipedia has also been '
                     'criticized for gender bias, particularly on its '
                     'English-language version, where the dominant majority '
                     'of editors are male. However, edit-a-thons have been '
                     'held to encourage female editors and increase the '
                     'coverage of women\'s topics. Facebook announced that by '
                     '2017 it would help readers detect fake news by '
                     'suggesting links to related Wikipedia articles.',
                     'YouTube announced a similar plan in 2018.'})
