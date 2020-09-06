import os
from langumo.parsers import WikipediaParser
from langumo.utils import AuxiliaryFile


def _get_resource_path(name: str) -> str:
    return os.path.join(os.path.dirname(__file__), 'resources', name)


def test_wikipedia_parser_preparation():
    parser = WikipediaParser()

    # Load a dummy wikipedia dump file.
    raw = AuxiliaryFile(_get_resource_path('dummy.wiki.xml.bz2'))
    parser.prepare(raw)

    # Check if the parser extracts the namespaces in wikipedia correctly.
    assert (parser.namespaces
            == ['Media', 'Special', 'Talk', 'User', 'User talk', 'Wikipedia',
                'Wikipedia talk', 'File', 'File talk', 'MediaWiki',
                'MediaWiki talk', 'Template', 'Template talk', 'Help',
                'Help talk', 'Category', 'Category talk', 'Portal',
                'Portal talk', 'Book', 'Book talk', 'Draft', 'Draft talk',
                'Education Program', 'Education Program talk', 'TimedText',
                'TimedText talk', 'Module', 'Module talk', 'Gadget',
                'Gadget talk', 'Gadget definition', 'Gadget definition talk'])


def test_wikipedia_parser_extraction():
    parser = WikipediaParser()

    # Load a dummy wikipedia dump file.
    raw = AuxiliaryFile(_get_resource_path('dummy.wiki.xml.bz2'))
    parser.prepare(raw)

    # Extract documents from the parser.
    documents = list(parser.extract(raw))

    # The dummy dump file contains 3 full articles and other redirection pages.
    assert len(documents) == 3


def test_if_parser_parses_mediawiki_codes_well():
    parser = WikipediaParser()

    # Load a dummy wikipedia dump file.
    raw = AuxiliaryFile(_get_resource_path('dummy.wiki.xml.bz2'))
    parser.prepare(raw)

    # Extract documents and parse the mediawiki codes.
    articles = []
    for document in parser.extract(raw):
        article = parser.parse(document)
        if article:
            articles.append(article)

    assert (articles == ['Archer is a slab serif typeface designed in 2001 by '
                         'Tobias Frere-Jones and Jonathan Hoefler for use in '
                         'Martha Stewart Living magazine. It was later '
                         'released by Hoefler & Frere-Jones for commercial '
                         'licensing.\n'
                         'The typeface is a geometric slab serif, one with a '
                         'geometric design similar to sans-serif fonts. It '
                         'takes inspiration from mid-twentieth century '
                         'designs such as Rockwell.\n'
                         'The face is unique for combining the geometric '
                         'structure of twentieth-century European slab-serifs '
                         'but imbuing the face with a domestic, less strident '
                         'tone of voice. Balls were added to the upper '
                         'terminals on letters such as C and G to increase '
                         'its charm. Italics are true italic designs, with '
                         'flourishes influenced by calligraphy, an unusual '
                         'feature for geometric slab serif designs. As with '
                         'many Hoefler & Frere-Jones designs, it was released '
                         'in a wide range of weights from hairline to bold, '
                         'reflecting its design goal as a typeface for '
                         'complex magazines.\n'
                         'The typeface has been used for, among other things, '
                         'branding for Wells Fargo and is a main font for the '
                         'San Francisco Chronicle and Wes Anderson\'s film '
                         'The Grand Budapest Hotel.'])
