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
* [Usage](#usage)
* [License](#license)

## Introduction
`langumo` is an **unified corpus building environment for Language Models**.
`langumo` provides pipelines for building text-based datasets. Constructing
datasets requires complicated pipelines (e.g. parsing, shuffling and
tokenization). Moreover, if corpora are collected from different sources, it
would be a problem to extract data from various formats. `langumo` helps to
build a dataset with the diverse formats simply at once.

## Main features
* Easy to build, simple to add new corpus format.
* Fast building through performance optimizations (even written in Python).
* Supports multi-processing in parsing corpora.
* Extremely less memory usage.
* All-in-one environment. Never mind the internal procedures!
* Does not need to write codes for new corpus. Instead, add to the build
  configuration simply.

## Dependencies
* nltk
* colorama
* pyyaml>=5.3.1
* tqdm>=4.46.0
* tokenizers==0.8.1
* mwparserfromhell>=0.5.4
* kss==1.3.1

## Installation
### With pip
`langumo` can be installed using `pip` as follows:
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

Let's build a [**Wikipedia**](https://en.wikipedia.org/wiki/Main_Page)
dataset. First, install `langumo` in your virtual
enviornment.
```bash
$ pip install langumo
```

After installing `langumo`, create a workspace to use in build.
```bash
$ mkdir workspace
$ cd workspace
```

Before creating the dataset, we need a **Wikipedia dump file** (which is a source of the dataset). You can get various
versions of Wikipedia dump files from [here](https://dumps.wikimedia.org/).
In this tutorial, we will use
[a part of Wikipedia dump file](https://dumps.wikimedia.org/enwiki/20200901/enwiki-20200901-pages-articles1.xml-p1p30303.bz2).
Download the file with your browser and move to `workspace/src`. Or, use `wget` to get the file in terminal simply:
```bash
$ wget -P src https://dumps.wikimedia.org/enwiki/20200901/enwiki-20200901-pages-articles1.xml-p1p30303.bz2
```

`langumo` needs a build configuration file which contains the details of
dataset. Create `build.yml` file to `workspace` and write belows:
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

After building the dataset, `workspace` would contain the below files:

    workspace
    ├── build
    │   ├── corpus.eval.txt
    │   ├── corpus.train.txt
    │   └── vocab.txt
    ├── src
    │   └── enwiki-20200901-pages-articles1.xml-p1p30303.bz2
    └── build.yml

## Usage

```
usage: langumo [-h] [config]

The unified corpus building environment for Language Models.

positional arguments:
  config      langumo build configuration

optional arguments:
  -h, --help  show this help message and exit
```

## License
`langumo` is [Apache-2.0 Licensed](./LICENSE).

[![FOSSA Status](https://app.fossa.com/api/projects/custom%2B20034%2Flangumo.svg?type=large)](https://app.fossa.com/projects/custom%2B20034%2Flangumo?ref=badge_large)