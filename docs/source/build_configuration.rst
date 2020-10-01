Build Configuration
===================

Overview
--------

Before building a corpus dataset, you need to configure the detail parameters.
``langumo`` reads the build configuration file and uses the parameters in
:ref:`building`.

Build configuration files use ``YAML`` syntax. Default configuration file name
is ``build.yml``. See also :ref:`Command-line usage`.

YAML syntax for building
------------------------

Every build configuration files must contain ``langumo`` namespace in top.

``langumo.workspace``
^^^^^^^^^^^^^^^^^^^^^
The path of workspace directory where temporary files would be saved. It will
be deleted automatically after building the dataset. *Default: tmp*

``langumo.inputs``
^^^^^^^^^^^^^^^^^^
The list of input corpus files. Each item contains ``path`` and
:class:`parser <langumo.building.parsing.Parser>` which imply the input file
path and full class name of its parser respectively.

``langumo.outputs``
^^^^^^^^^^^^^^^^^^^
``langumo`` creates a trained vocabulary file which is used in **WordPiece**
tokenizer and tokenized datasets for training and evaluation. You can configure
the output paths in this section.

* ``vocabulary``: The output path of trained vocabulary file.
  *Default: build/vocab.txt*
* ``train-corpus``: The output path of tokenized corpus dataset for training.
  *Default: build/corpus.train.txt*
* ``eval-corpus``: The output path of tokenized corpus dataset for evaluation.
  *Default: build/corpus.eval.txt*

``langumo.build.parsing``
^^^^^^^^^^^^^^^^^^^^^^^^^
After each article is parsed to a plain text by
:class:`Parser <langumo.building.parsing.Parser>`, ``langumo`` automatically
splits the article into the sentence groups to fit its length to the
limitation. You can configure the details in this section.

* ``num-workers``: The number of worker processes which execute
  :meth:`parse <langumo.building.parsing.Parser.parse>`. We recommend to set to
  the number of CPU cores. *Default: 1*
* ``language``: The language of your dataset. ``langumo`` will load
  corresponding sentence tokenizer to split articles into the sentence groups.
  *Default: en*
* ``newline``: The delimiter of paragraphs. Precisely, all line-break
  characters in every articles would be replaced to this token.
  *Default: [NEWLINE]*
* ``min-length``: The minimum length of each sentence group. *Default: 0*
* ``max-length``: The maximum length of each sentence group. *Default: 1024*

``langumo.build.splitting``
^^^^^^^^^^^^^^^^^^^^^^^^^^^
Language models are trained with **train dataset** and evaluated with
**evaluation dataset**. Usually they should be different for evaluating correct
generalization performance. So ``langumo`` splits the tokenized raw texts into
**training** and **evaluation**.

* ``validation-ratio``: The ratio of evaluation dataset to train dataset.
  *Default: 0.1*

``langumo.build.tokenization``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
You can configure the details of both training a tokenizer and tokenizing
the sentences.

* ``prebuilt-vocab``: The prebuild vocabulary file path. If you want to use
  prebuilt vocabulary instead of training new tokenizer, do specify the path at
  this option. Note that if you use the prebuilt vocabulary then
  ``subset-size``, ``vocab-size`` and ``limit-alphabet`` options would be
  ignored.
* ``subset-size``: The size of subset which is a part of dataset for training a
  tokenizer. It is not efficient to train the tokenizer with whole dataset.
  The subset of dataset does not harm the performance awfully. We recommend to
  use the subset in training tokenizer. *Default: 1000000000*
* ``vocab-size``: The vocabulary size. *Default: 32000*
* ``limit-alphabet``: The maximum different characters to keep in the alphabet.
  *Default: 1000*
* ``unk-token``: The token to replace unknown subwords. *Default: [UNK]*
* ``special-tokens``: The list of special tokens. They would not be splitted
  into subwords. We recommend to add `langumo.build.parsing.newline` token in
  this option. *Default: [START], [END], [PAD], [NEWLINE]*


Example
-------
Here is an example of build configuration:

.. code-block:: YAML

    langumo:
      workspace: tmp # temporary directory

      inputs:
      - path: src/corpus1.txt
        parser: myexample.parsers.Corpus1Parser
      # add input corpus files...

      outputs:
        vocabulary: build/vocab.txt

        train-corpus: build/train.txt
        eval-corpus: build/eval.txt

      build:
        parsing:
          num-workers: 16 # number of cpu cores...

          language: en
          newline: [NEWLINE]

          min-length: 512
          max-length: 2048

        splitting:
          # only 1% of the total data is used for evaluation
          validation-ratio: 0.01

        tokenization:
          # 5GB of the total data is used for training tokenizer
          subset-size: 5000000000

          vocab-size: 50000
          limit-alphabet: 1000

          unk-token: [UNK]
          special-tokens:
          - [START]
          - [END]
          - [PAD]
          - [NEWLINE]

``build/vocab.txt``, ``build/train.txt`` and ``build/corpus`` will be created
as build outputs. Sequences whose lengths are less than **512** would be
ignored and ones whose lenghts are more than **2048** would be splitted into
subsequences. Thus, the lengths of documents in the corpus dataset are less
than **2048**. **WordPiece** tokenizer will create **50k** subwords including
special tokens.
