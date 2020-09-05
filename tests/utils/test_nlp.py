from multiprocessing import Process, Queue
from langumo.utils import SentenceSplitter


def test_english_sentence_splitting():
    _dummy_sentence_corpus = (
        'Wikipedia is a multilingual online encyclopedia created and '
        'maintained as an open collaboration project by a community of '
        'volunteer editors using a wiki-based editing system. It is the '
        'largest and most popular general reference work on the World Wide '
        'Web. It is also one of the 15 most popular websites ranked by Alexa, '
        'as of August 2020. It features exclusively free content and no '
        'commercial ads. It is hosted by the Wikimedia Foundation, a '
        'non-profit organization funded primarily through donations.'
    )

    assert (SentenceSplitter('en').tokenize(_dummy_sentence_corpus)
            == ['Wikipedia is a multilingual online encyclopedia created and '
                'maintained as an open collaboration project by a community '
                'of volunteer editors using a wiki-based editing system.',
                'It is the largest and most popular general reference work on '
                'the World Wide Web.',
                'It is also one of the 15 most popular websites ranked by '
                'Alexa, as of August 2020.',
                'It features exclusively free content and no commercial ads.',
                'It is hosted by the Wikimedia Foundation, a non-profit '
                'organization funded primarily through donations.'])


def test_english_sentence_splitting_in_multiprocessing():
    _dummy_sentence_corpus = (
        'Wikipedia is a multilingual online encyclopedia created and '
        'maintained as an open collaboration project by a community of '
        'volunteer editors using a wiki-based editing system. It is the '
        'largest and most popular general reference work on the World Wide '
        'Web. It is also one of the 15 most popular websites ranked by Alexa, '
        'as of August 2020. It features exclusively free content and no '
        'commercial ads. It is hosted by the Wikimedia Foundation, a '
        'non-profit organization funded primarily through donations.'
    )

    # Create worker process function to split sentences in multi-processing.
    def _process(text: str, splitter: SentenceSplitter, queue: Queue):
        queue.put(splitter.tokenize(text))

    # Prepare processes and queue to communicate with them.
    queue = Queue()
    splitter = SentenceSplitter('en')
    workers = [Process(target=_process,
                       args=(_dummy_sentence_corpus, splitter, queue),
                       daemon=True)
               for _ in range(10)]

    # Start the processes.
    for w in workers:
        w.start()

    # Check if all processes split sentences correctly.
    for _ in range(10):
        assert (queue.get() == [
                'Wikipedia is a multilingual online encyclopedia created and '
                'maintained as an open collaboration project by a community '
                'of volunteer editors using a wiki-based editing system.',
                'It is the largest and most popular general reference work on '
                'the World Wide Web.',
                'It is also one of the 15 most popular websites ranked by '
                'Alexa, as of August 2020.',
                'It features exclusively free content and no commercial ads.',
                'It is hosted by the Wikimedia Foundation, a non-profit '
                'organization funded primarily through donations.'])


def test_korean_sentence_splitting():
    _dummy_sentence_corpus = (
        '위키백과 또는 위키피디아는 누구나 자유롭게 쓸 수 있는 다언어판 인터넷 '
        '백과사전이다. 2001년 1월 15일 지미 웨일스와 래리 생어가 시작하였으며, '
        '대표적인 집단 지성의 사례로 평가받고 있다. 위키백과는 자유 저작물을 '
        '보유하고 상업적인 광고가 없으며 주로 기부금을 통해 지원을 받는 비영리 '
        '단체인 위키미디어 재단에 의해 소유되고 지원을 받고 있다. 2020년 기준으로 '
        '영어판 600만여 개, 한국어판 517,949개를 비롯하여 300여 언어판을 합하면 '
        '4천만 개 이상의 글이 수록되어 꾸준히 성장하고 있으며 앞으로 더 성장할 '
        '예정이다. 위키백과의 저작권은 크리에이티브 커먼즈 라이선스(CCL)와 GNU '
        '자유 문서(GFDL)의 2중 라이선스를 따른다. 두 라이선스 모두 자유 콘텐츠를 '
        '위한 것으로 일정한 요건을 갖추면 사용에 제약을 받지 않는다.'
    )

    assert (SentenceSplitter('ko').tokenize(_dummy_sentence_corpus)
            == ['위키백과 또는 위키피디아는 누구나 자유롭게 쓸 수 있는 다언어판 '
                '인터넷 백과사전이다.',
                '2001년 1월 15일 지미 웨일스와 래리 생어가 시작하였으며, 대표적인 '
                '집단 지성의 사례로 평가받고 있다.',
                '위키백과는 자유 저작물을 보유하고 상업적인 광고가 없으며 주로 '
                '기부금을 통해 지원을 받는 비영리 단체인 위키미디어 재단에 의해 '
                '소유되고 지원을 받고 있다.',
                '2020년 기준으로 영어판 600만여 개, 한국어판 517,949개를 비롯하여 '
                '300여 언어판을 합하면 4천만 개 이상의 글이 수록되어 꾸준히 '
                '성장하고 있으며 앞으로 더 성장할 예정이다.',
                '위키백과의 저작권은 크리에이티브 커먼즈 라이선스(CCL)와 GNU 자유 '
                '문서(GFDL)의 2중 라이선스를 따른다.',
                '두 라이선스 모두 자유 콘텐츠를 위한 것으로 일정한 요건을 갖추면 '
                '사용에 제약을 받지 않는다.'])


def test_korean_sentence_splitting_in_multiprocessing():
    _dummy_sentence_corpus = (
        '위키백과 또는 위키피디아는 누구나 자유롭게 쓸 수 있는 다언어판 인터넷 '
        '백과사전이다. 2001년 1월 15일 지미 웨일스와 래리 생어가 시작하였으며, '
        '대표적인 집단 지성의 사례로 평가받고 있다. 위키백과는 자유 저작물을 '
        '보유하고 상업적인 광고가 없으며 주로 기부금을 통해 지원을 받는 비영리 '
        '단체인 위키미디어 재단에 의해 소유되고 지원을 받고 있다. 2020년 기준으로 '
        '영어판 600만여 개, 한국어판 517,949개를 비롯하여 300여 언어판을 합하면 '
        '4천만 개 이상의 글이 수록되어 꾸준히 성장하고 있으며 앞으로 더 성장할 '
        '예정이다. 위키백과의 저작권은 크리에이티브 커먼즈 라이선스(CCL)와 GNU '
        '자유 문서(GFDL)의 2중 라이선스를 따른다. 두 라이선스 모두 자유 콘텐츠를 '
        '위한 것으로 일정한 요건을 갖추면 사용에 제약을 받지 않는다.'
    )

    # Create worker process function to split sentences in multi-processing.
    def _process(text: str, splitter: SentenceSplitter, queue: Queue):
        queue.put(splitter.tokenize(text))

    # Prepare processes and queue to communicate with them.
    queue = Queue()
    splitter = SentenceSplitter('ko')
    workers = [Process(target=_process,
                       args=(_dummy_sentence_corpus, splitter, queue),
                       daemon=True)
               for _ in range(10)]

    # Start the processes.
    for w in workers:
        w.start()

    # Check if all processes split sentences correctly.
    for _ in range(10):
        assert (queue.get() == [
                '위키백과 또는 위키피디아는 누구나 자유롭게 쓸 수 있는 다언어판 '
                '인터넷 백과사전이다.',
                '2001년 1월 15일 지미 웨일스와 래리 생어가 시작하였으며, 대표적인 '
                '집단 지성의 사례로 평가받고 있다.',
                '위키백과는 자유 저작물을 보유하고 상업적인 광고가 없으며 주로 '
                '기부금을 통해 지원을 받는 비영리 단체인 위키미디어 재단에 의해 '
                '소유되고 지원을 받고 있다.',
                '2020년 기준으로 영어판 600만여 개, 한국어판 517,949개를 비롯하여 '
                '300여 언어판을 합하면 4천만 개 이상의 글이 수록되어 꾸준히 '
                '성장하고 있으며 앞으로 더 성장할 예정이다.',
                '위키백과의 저작권은 크리에이티브 커먼즈 라이선스(CCL)와 GNU 자유 '
                '문서(GFDL)의 2중 라이선스를 따른다.',
                '두 라이선스 모두 자유 콘텐츠를 위한 것으로 일정한 요건을 갖추면 '
                '사용에 제약을 받지 않는다.'])
