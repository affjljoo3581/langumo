import tempfile
from langumo.building import TrainTokenizer, TokenizeSentences
from langumo.utils import AuxiliaryFileManager


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
    'visitors per month.\n'
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


def test_subset_file_creation():
    with tempfile.TemporaryDirectory() as tdir, \
            AuxiliaryFileManager(f'{tdir}/tmp') as afm:
        corpus = afm.create()
        with corpus.open('w') as fp:
            fp.write('hello world!\n' * 100)

        with (TrainTokenizer(subset_size=1024)
              ._create_subset_file(afm, corpus)
              .open('r')) as fp:
            assert len(fp.readlines()) == 79

        with (TrainTokenizer(subset_size=128)
              ._create_subset_file(afm, corpus)
              .open('r')) as fp:
            assert len(fp.readlines()) == 10

        with (TrainTokenizer(subset_size=2000)
              ._create_subset_file(afm, corpus)
              .open('r')) as fp:
            assert len(fp.readlines()) == 100


def test_training_wordpiece_tokenizer():
    with tempfile.TemporaryDirectory() as tdir, \
            AuxiliaryFileManager(f'{tdir}/tmp') as afm:
        corpus = afm.create()
        with corpus.open('w') as fp:
            fp.write(_dummy_corpus_content)

        # Train WordPiece tokenizer and get vocabulary file.
        vocab = (TrainTokenizer(vocab_size=128,
                                limit_alphabet=64,
                                unk_token='[UNK]')
                 .build(afm, corpus))

        # Read subwords from the vocabulary file.
        with vocab.open('r') as fp:
            words = fp.readlines()

        # Check if the number of total words equals to vocabulary size and the
        # vocabulary contains unknown token.
        assert len(words) == 128
        assert words[0].strip() == '[UNK]'


def test_subword_tokenization():
    with tempfile.TemporaryDirectory() as tdir, \
            AuxiliaryFileManager(f'{tdir}/tmp') as afm:
        corpus = afm.create()
        with corpus.open('w') as fp:
            fp.write(_dummy_corpus_content)

        # Train WordPiece vocabulary and tokenize sentences.
        vocab = (TrainTokenizer(vocab_size=128, limit_alphabet=64)
                 .build(afm, corpus))
        tokenized = (TokenizeSentences(unk_token='[UNK]')
                     .build(afm, corpus, vocab))

        # Test if the tokenization is correctly applied to the corpus. Note
        # that the tokenizer model will normalize the sentences.
        with tokenized.open('r') as fp:
            assert (fp.read().strip().replace('##', '').replace(' ', '')
                    == _dummy_corpus_content.lower().replace(' ', ''))
