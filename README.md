# langumo
**The unified corpus building environment for Language Models.**

![build](https://github.com/affjljoo3581/langumo/workflows/build/badge.svg)
![PyPI](https://img.shields.io/pypi/v/langumo)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/langumo)
![PyPI - Format](https://img.shields.io/pypi/format/langumo)<br/>
![GitHub](https://img.shields.io/github/license/affjljoo3581/langumo?color=blue)
[![FOSSA Status](https://app.fossa.com/api/projects/custom%2B20034%2Flangumo.svg?type=shield)](https://app.fossa.com/projects/custom%2B20034%2Flangumo?ref=badge_shield)
[![codecov](https://codecov.io/gh/affjljoo3581/langumo/branch/master/graph/badge.svg)](https://codecov.io/gh/affjljoo3581/langumo)
[![CodeFactor](https://www.codefactor.io/repository/github/affjljoo3581/langumo/badge)](https://www.codefactor.io/repository/github/affjljoo3581/langumo)
[![Codacy Badge](https://app.codacy.com/project/badge/Grade/9e9be907acaf473397cb1b25ab404c77)](https://www.codacy.com/manual/affjljoo3581/langumo?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=affjljoo3581/langumo&amp;utm_campaign=Badge_Grade)

## Table of contents
* [Introduction](#introduction)
* [Main features](#main-features)
* [Dependencies](#dependencies)
* [Installation](#installation)
    * [With pip](#with-pip)
    * [From source](#from-source)
* [Quick start guide](#quick-start-guide)
    * [Build your first dataset](#build-your-first-dataset)
    * [Write a custom `Parser`](#write-a-custom-parser)
* [Usage](#usage)
    * [Command-line usage](#command-line-usage)
    * [Details of build configuration](#details-of-build-configuration)
    * [Builtin `Parser`s](#builtin-parsers)
* [License](#license)

## Introduction
`langumo` is an **unified corpus building environment for Language Models**.
`langumo` provides pipelines for building text-based datasets. Constructing
datasets requires complicated pipelines (e.g. parsing, shuffling and
tokenization). Moreover, if corpora are collected from different sources, it
would be a problem to extract data from various formats simultaneously.
`langumo` helps to build a dataset with the diverse formats simply at once.

## Main features
* Easy to build, simple to add new corpus format.
* Fast building through performance optimizations (even written in Python).
* Supports multi-processing in parsing corpora.
* Extremely less memory usage.
* All-in-one environment. Never mind the detailed procedures!
* Does not need to write codes for new corpus. Instead, add to the build
  configuration simply.

## Dependencies
* nltk
* colorama
* pyyaml>=5.3.1
* tqdm>=4.46.0
* tokenizers>=0.8.0
* mwparserfromhell>=0.5.4
* kss==1.3.1

## Installation
### With pip
`langumo` can be installed using pip as follows:
```bash
$ pip install langumo
```

### From source
You can install `langumo` from source by cloning the repository and running:
```bash
$ git clone https://github.com/affjljoo3581/langumo.git
$ cd langumo
$ python setup.py install
```

## Quick start guide

### Build your first dataset
Let's build a [**Wikipedia**](https://en.wikipedia.org/wiki/Main_Page)
dataset. First, install `langumo` in your virtual
enviornment.
```bash
$ pip install langumo
```

After installing `langumo`, create a workspace directory to use in building.
```bash
$ mkdir workspace
$ cd workspace
```

Before creating the dataset, we need a Wikipedia dump file (which is a source of our dataset). You can get various
versions of Wikipedia dump files from [here](https://dumps.wikimedia.org/).
In this tutorial, we will use
[a part of Wikipedia dump file](https://dumps.wikimedia.org/enwiki/20200901/enwiki-20200901-pages-articles1.xml-p1p30303.bz2).
Download the file with your browser and move the downloaded file to
`workspace/src` directory. Or, use `wget` to get the file in terminal simply:
```bash
$ mkdir src
$ wget -P src https://dumps.wikimedia.org/enwiki/20200901/enwiki-20200901-pages-articles1.xml-p1p30303.bz2
```

To build the dataset, `langumo` needs a build configuration file which
contains the details of the dataset. Create `build.yml` file to the `workspace`
directory and write the belows to the file:
```yaml
langumo:
  inputs:
  - path: src/enwiki-20200901-pages-articles1.xml-p1p30303.bz2
    parser: langumo.parsers.WikipediaParser

  build:
    parsing:
      num-workers: 8 # The number of CPU cores you have.

    tokenization:
      vocab-size: 32000 # The vocabulary size.
```

Now we are ready to create our first dataset. Run `langumo`!
```bash
$ langumo
```

Then you can see the below outputs:
```
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
```

After building the dataset, the workspace directory would contain the below files:

    workspace
    ├── build
    │   ├── corpus.eval.txt
    │   ├── corpus.train.txt
    │   └── vocab.txt
    ├── src
    │   └── enwiki-20200901-pages-articles1.xml-p1p30303.bz2
    └── build.yml

### Write a custom `Parser`
`langumo` supports custom `Parser`s to use various formats of corpora in
building. In this tutorial, we are going to see how to build
[**Amazon Review Data (2018)**](https://nijianmo.github.io/amazon/index.html)
dataset in `langumo`.

The basic form of `Parser` class is as below:
```python
class AmazonReviewDataParser(langumo.building.Parser):
    def extract(self, raw: langumo.utils.AuxiliaryFile) -> Iterable[str]:
        pass

    def parse(self, text: str) -> str:
        pass
```

`extract` method yields articles or documents from raw-formatted file and `parse` method returns the parsed contents
from extracted raw articles from `extract`.

To implement the parser, let's analyse **Amazon Review Data
(2018)** dataset. The data format of **Amazon Review Data (2018)**
is one-review-per-line in json (or,
[JSON Lines](https://jsonlines.org/)). That is, each line is a
json-formatted review data as following:
```json
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
```

We only need the contents in `reviewText` of the reviews. So the parser
should only take `reviewText` from the json objects (extracted from
`extract` method).
```python
def parse(self, text: str) -> str:
    return json.loads(text)['reviewText']
```

Meanwhile, as mentioned above, reviews are separated by new-line
delimiter. So `extract` method should yield each line in the file. Note
that the raw files are deflated with `gunzip` format.
```python
def extract(self, raw: langumo.utils.AuxiliaryFile) -> Iterable[str]:
    with gzip.open(raw.name, 'r') as fp:
        yield from fp
```

That's all! You've just implemented a parser for **Amazon Review Data
(2018)**. Now you can use this parser in build configuration. Let the parser
class is in `myexample.parsers` package. Here is an example of build
configuration.
```yaml
langumo:
  inputs:
  - path: src/AMAZON_FASHION_5.json.gz
    parser: myexample.parsers.AmazonReviewDataParser
  
  # other configurations...
```

## Usage

### Command-line usage
```
usage: langumo [-h] [config]

The unified corpus building environment for Language Models.

positional arguments:
  config      langumo build configuration

optional arguments:
  -h, --help  show this help message and exit
```

### Details of build configuration
Every build configuration files contain `langumo` namespace in top.

#### `langumo.workspace`
The path of workspace directory where temporary files would be saved to. It
would be deleted automatically after building the dataset. *Default: tmp*

#### `langumo.inputs`
The list of input corpus files. Each item contains `path` and `parser` which
imply the input file path and full class name of its parser respectively.

#### `langumo.outputs`
`langumo` creates a trained vocabulary file which is for **WordPiece**
tokenizer and tokenized datasets for training and evaluation. You can configure
the detail output paths in this section.
* `vocabulary`: The output path of trained vocabulary file.
  *Default: build/vocab.txt*
* `train-corpus`: The output path of splitted dataset for training.
  *Default: build/corpus.train.txt*
* `eval-corpus`: The output path of splitted dataset for evaluation.
  *Default: build/corpus.eval.txt*

#### `langumo.build.parsing`
After each article is parsed to a plain text by `Parser`, `langumo`
automatically splits the article into groups to fit its length to the given
limitation. You can configure the details of parsing raw-formatted corpora.
* `num-workers`: The number of `Parser.parse` processes. We recommend to set
  to the number of CPU cores. *Default: 1*
* `language`: The language of your dataset. `langumo` will load corresponding
  sentence tokenizer to split articles into groups. *Default: en*
* `newline`: The delimiter of paragraphs. Precisely, all line-break characters
  in articles would be replaced to this token. That's because the contents are
  separated by line-break characters as well. *Default: [NEWLINE]*
* `min-length`: The minimum length of each content group. *Default: 0*
* `max-length`: The maximum length of each content group. *Default: 1024*

#### `langumo.build.splitting`
Language models are trained with **train dataset** and evaluated with
**evaluation dataset**. Usually the evaluation dataset are taken from the train
dataset — extremly large dataset — to preserve domain. You can configure the
scale of evaluation dataset.
* `validation-ratio`: The ratio of evaluation dataset to train dataset.
  *Default: 0.1*

#### `langumo.build.tokenization`
You can configure the details of both training tokenizer and tokenizing
sentences.
* `prebuilt-vocab`: The prebuild vocabulary file path. If you want to use
  prebuilt vocabulary rather than train new tokenizer, do specify the path to
  this option. Note that `subset-size`, `vocab-size` and `limit-alphabet` would
  be ignored.
* `subset-size`: The size of subset which is a portion of dataset. It is not
  efficient to train a tokenizer with whole dataset. Using a subset does not
  matter if it is well-shuffled. *Default: 1000000000*
* `vocab-size`: The vocabulary size. *Default: 32000*
* `limit-alphabet`: The maximum different characters to keep in the alphabet.
  *Default: 1000*
* `unk-token`: The token to replace unknown subwords. *Default: [UNK]*
* `special-tokens`: The list of special tokens. They would not be splitted into
  subwords. We recommend to add `langumo.build.parsing.newline` token.
  *Default: [START], [END], [PAD], [NEWLINE]*

### Builtin `Parser`s
`langumo` provides built-in `Parser`s to use popular datasets directly, without
creating new `Parser`s.

#### WikipediaParser (`langumo.parsers.WikipediaParser`)
Wikipedia articles are written in
[**MediaWiki**](https://en.wikipedia.org/wiki/MediaWiki) code. You can simply
use any version of Wikipedia dump file with this parser. It internally use
[`mwparserfromhell`](https://github.com/earwig/mwparserfromhell) library.

#### EscapedStringParser (`langumo.parsers.EscapedStringParser`)
In `json` package, there is `encode_basestring` method which escapes texts to
JSON-style string. For example,

    Harry Potter and the Sorcerer's Stone 

    CHAPTER ONE 

    THE BOY WHO LIVED 

    Mr. and Mrs. Dursley, of number four, Privet Drive, were proud to say that they were perfectly normal, thank you very much.

is escaped as below:

    "Harry Potter and the Sorcerer's Stone \n\nCHAPTER ONE \n\nTHE BOY WHO LIVED \n\nMr. and Mrs. Dursley, of number four, Privet Drive, were proud to say that they were perfectly normal, thank you very much."

As you can see, multi-line content is changed to the single line. This parser
handles the newline-separated contents escaped by
`json.encoder.encode_basestring`. If you want to use your custom dataset to
`langumo`, consider this format.

## License
`langumo` is [Apache-2.0 Licensed](./LICENSE).

[![FOSSA Status](https://app.fossa.com/api/projects/custom%2B20034%2Flangumo.svg?type=large)](https://app.fossa.com/projects/custom%2B20034%2Flangumo?ref=badge_large)