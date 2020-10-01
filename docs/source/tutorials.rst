Tutorials
=========

Build your first datset
-----------------------

Let's build a `Wikipedia`_ dataset. First, install ``langumo`` in your virtual
enviornment.

.. code-block:: bash

    $ pip install langumo


After installing ``langumo``, create a workspace to use in build.

.. code-block:: bash

    $ mkdir workspace
    $ cd workspace


Before creating the dataset, we need a **Wikipedia dump file** (which is a
source of the dataset). You can get various versions of Wikipedia dump files
from `here`_. In this tutorial, we will use `a part of Wikipedia dump file`_.
Download the file with your browser and move to ``workspace/src``. Or, use
``wget`` to get the file in terminal simply:

.. code-block:: bash

    $ wget -P src https://dumps.wikimedia.org/enwiki/20200901/enwiki-20200901-pages-articles1.xml-p1p30303.bz2


``langumo`` needs a build configuration file which contains the details of
dataset. Create ``build.yml`` file to ``workspace`` and write belows:

.. code-block:: yaml

    langumo:
      inputs:
      - path: src/enwiki-20200901-pages-articles1.xml-p1p30303.bz2
        parser: langumo.parsers.WikipediaParser

      build:
        parsing:
          num-workers: 8 # The number of CPU cores you have.

        tokenization:
          vocab-size: 32000 # The vocabulary size.


Now we are ready to create our first dataset. Run ``langumo``!

.. code-block:: bash

    $ langumo


Then you can see the below outputs:

.. code-block::

    [*] import file from src/enwiki-20200901-pages-articles1.xml-p1p30303.bz2
    [*] parse raw-formatted corpus file with WikipediaParser
    [*] merge 1 files into one
    [*] shuffle raw corpus file: 100%|██████████████████████████████| 118042/118042 [00:01<00:00, 96965.15it/s]
    [00:00:10] Reading files (256 Mo)                   ███████████████████████████████████                 100
    [00:00:00] Tokenize words                           ███████████████████████████████████ 418863   /   418863
    [00:00:01] Count pairs                              ███████████████████████████████████ 418863   /   418863
    [00:00:02] Compute merges                           ███████████████████████████████████ 28942    /    28942
    [*] export the processed file to build/vocab.txt
    [*] tokenize sentences with WordPiece model: 100%|███████████████| 236084/236084 [00:23<00:00, 9846.67it/s]
    [*] split validation corpus - 23609  of 236084 lines
    [*] export the processed file to build/corpus.train.txt
    [*] export the processed file to build/corpus.eval.txt


After building the dataset, ``workspace`` would contain the below files:

.. code-block::

    workspace
    ├── build
    │   ├── corpus.eval.txt
    │   ├── corpus.train.txt
    │   └── vocab.txt
    ├── src
    │   └── enwiki-20200901-pages-articles1.xml-p1p30303.bz2
    └── build.yml

.. _`Wikipedia`: https://en.wikipedia.org/wiki/Main_Page
.. _`here`: https://dumps.wikimedia.org/
.. _`a part of Wikipedia dump file`: https://dumps.wikimedia.org/enwiki/20200901/enwiki-20200901-pages-articles1.xml-p1p30303.bz2

Write a custom Parser
---------------------

``langumo`` supports custom :class:`Parser <langumo.building.parsing.Parser>` s
to use various formats in building. In this tutorial, we are going to see how
to build `Amazon Review Data (2018)`_ dataset in ``langumo``.

The basic form of ``Parser`` class is as below:

.. code-block:: python

    class AmazonReviewDataParser(langumo.building.Parser):
        def extract(self, raw: langumo.utils.AuxiliaryFile) -> Iterable[str]:
            pass

        def parse(self, text: str) -> str:
            pass


:meth:`extract <langumo.building.parsing.Parser.extract>` method yields
articles or documents from raw-formatted file and
:meth:`parse <langumo.building.parsing.Parser.parse>` method returns the parsed
contents from extracted raw articles.

To implement the parser, let's analyse **Amazon Review Data (2018)** dataset.
The data format of **Amazon Review Data (2018)** is one-review-per-line in json
(or, `JSON Lines`_). That is, each line is a json-formatted review data. Here
is an example:

.. code-block:: json

    {
        "image": ["https://images-na.ssl-images-amazon.com/images/I/71eG75FTJJL._SY88.jpg"], 
        "overall": 5.0, 
        "vote": "2", 
        "verified": true, 
        "reviewTime": "01 1, 2018", 
        "reviewerID": "AUI6WTTT0QZYS", 
        "asin": "5120053084", 
        "style": {
            "Size:": "Large", 
            "Color:": "Charcoal"
        }, 
        "reviewerName": "Abbey", 
        "reviewText": "I now have 4 of the 5 available colors of this shirt... ", 
        "summary": "Comfy, flattering, discreet--highly recommended!", 
        "unixReviewTime": 1514764800
    }


We only need the contents in ``reviewText`` of the reviews. So the parser
should only take ``reviewText`` from the json objects (extracted from
:meth:`extract <langumo.building.parsing.Parser.extract>` method).

.. code-block:: python

    def parse(self, text: str) -> str:
        return json.loads(text)['reviewText']


Meanwhile, as mentioned above, reviews are separated by new-line delimiter. So
:meth:`extract <langumo.building.parsing.Parser.extract>` method should yield
each line in the file. Note that the raw files are deflated with ``gunzip``
format.

.. code-block:: python

    def extract(self, raw: langumo.utils.AuxiliaryFile) -> Iterable[str]:
        with gzip.open(raw.name, 'r') as fp:
            yield from fp


That's all! You've just implemented a parser for **Amazon Review Data (2018)**.
Now you can use the parser in build configuration. Let the parser class is in
``myexample.parsers`` package. Here is an example of build configuration.

.. code-block:: yaml

    langumo:
      inputs:
      - path: src/AMAZON_FASHION_5.json.gz
        parser: myexample.parsers.AmazonReviewDataParser
  
      # other configurations...

.. _`Amazon Review Data (2018)`: https://nijianmo.github.io/amazon/index.html
.. _`JSON Lines`: https://jsonlines.org/
