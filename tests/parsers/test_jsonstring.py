import os
from langumo.parsers import EscapedJSONStringParser
from langumo.utils import AuxiliaryFile


def _get_resource_path(name: str) -> str:
    return os.path.join(os.path.dirname(__file__), 'resources', name)


def test_json_string_parser_extraction():
    parser = EscapedJSONStringParser()

    # Load a dummy escaped json-string file.
    raw = AuxiliaryFile(_get_resource_path('dummy.jsonstring.txt'))
    parser.prepare(raw)

    # Extract documents from the parser.
    documents = list(parser.extract(raw))

    # The dummy dump file contains 3 full articles and others are empty.
    assert len(documents) == 3


def test_if_parser_parses_escaped_json_string_well():
    parser = EscapedJSONStringParser()

    # Load a dummy escaped json-string file.
    raw = AuxiliaryFile(_get_resource_path('dummy.jsonstring.txt'))
    parser.prepare(raw)

    # Extract documents and parse the json-encoded strings.
    articles = []
    for document in parser.extract(raw):
        article = parser.parse(document)
        if article:
            articles.append(article)

    assert (articles == ['Wikipedia is a multilingual online encyclopedia '
                         'created and maintained as an op en collaboration '
                         'project by a community of volunteer editors using a '
                         'wiki-based editing system. It is the largest and '
                         'most popular general reference work on the World '
                         'Wide Web. It is also one of the 15 most popular '
                         'websites as ranked by Alexa, as of August 2020. It '
                         'features exclusively free content and has no '
                         'advertising. It is hosted by the Wikimedia '
                         'Foundation, an American non-profit organization '
                         'funded primarily through donations.\nWikipedia was '
                         'launched on January 15, 2001, and was created by '
                         'Jimmy Wales and Larry Sanger. Sanger coined its '
                         'name as a portmanteau of the terms "wiki" and '
                         '"encyclopedia". Initially an English-language '
                         'encyclopedia, versions of Wikipedia in other '
                         'languages were quickly developed. With 6.2 million '
                         'articles, the English Wikipedia is the largest of '
                         'the more than 300 Wikipedia encyclopedias. Overall, '
                         'Wikipedia comprises more than 54 million articles '
                         'attracting 1.5 billion unique visitors per month.',
                         'In 2005, Nature published a peer review comparing '
                         '42 hard science articles from Encyclopædia '
                         'Britannica and Wikipedia and found that '
                         'Wikipedia\'s level of accuracy approached that of '
                         'Britannica, although critics suggested that it '
                         'might not have fared so well in a similar study of '
                         'a random sampling of all articles or one focused on '
                         'social science or contentious social issues. The '
                         'following year, Time stated that the open-door '
                         'policy of allowing anyone to edit had made '
                         'Wikipedia the biggest and possibly the best '
                         'encyclopedia in the world, and was a testament to '
                         'the vision of Jimmy Wales.\nWikipedia has been '
                         'criticized for exhibiting systemic bias and for '
                         'being subject to manipulation and spin in '
                         'controversial topics; Edwin Black has criticized '
                         'Wikipedia for presenting a mixture of "truth, half '
                         'truth, and some falsehoods". Wikipedia has also '
                         'been criticized for gender bias, particularly on '
                         'its English-language version, where the dominant '
                         'majority of editors are male. However, edit-a-thons '
                         'have been held to encourage female editors and '
                         'increase the coverage of women\'s topics. Facebook '
                         'announced that by 2017 it would help readers detect '
                         'fake news by suggesting links to related Wikipedia '
                         'articles. YouTube announced a similar plan in 2018.',
                         'Other collaborative online encyclopedias were '
                         'attempted before Wikipedia, but none were as '
                         'successful. Wikipedia began as a complementary '
                         'project for Nupedia, a free online English-language '
                         'encyclopedia project whose articles were written by '
                         'experts and reviewed under a formal process. It was '
                         'founded on March 9, 2000, under the ownership of '
                         'Bomis, a web portal company. Its main figures were '
                         'Bomis CEO Jimmy Wales and Larry Sanger, '
                         'editor-in-chief for Nupedia and later Wikipedia. '
                         'Nupedia was initially licensed under its own '
                         'Nupedia Open Content License, but even before '
                         'Wikipedia was founded, Nupedia switched to the GNU '
                         'Free Documentation License at the urging of Richard '
                         'Stallman. Wales is credited with defining the goal '
                         'of making a publicly editable encyclopedia, while '
                         'Sanger is credited with the strategy of using a '
                         'wiki to reach that goal. On January 10, 2001, '
                         'Sanger proposed on the Nupedia mailing list to '
                         'create a wiki as a "feeder" project for Nupedia.\n'
                         'The domains wikipedia.com and wikipedia.org were '
                         'registered on January 12, 2001 and January 13, 2001 '
                         'respectively, and Wikipedia was launched on January '
                         '15, 2001, as a single English-language edition at '
                         'www.wikipedia.com, and announced by Sanger on the '
                         'Nupedia mailing list. Wikipedia\'s policy of '
                         '"neutral point-of-view" was codified in its first '
                         'few months. Otherwise, there were relatively few '
                         'rules initially and Wikipedia operated '
                         'independently of Nupedia. Originally, Bomis '
                         'intended to make Wikipedia a business for profit.'])
