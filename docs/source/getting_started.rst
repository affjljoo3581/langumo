Getting Started
===============

Introduction
------------
``langumo`` is an **unified corpus building environment for Language Models**.
``langumo`` provides pipelines for building text-based datasets. Constructing
datasets requires complicated pipelines (e.g.
:mod:`parsing <langumo.building.parsing>`,
:mod:`shuffling <langumo.building.shuffling>` and
:mod:`tokenization <langumo.building.tokenization>`). Moreover, if corpora are
collected from different sources, it would be a problem to extract data from
various formats. `langumo` helps to build a dataset with the diverse formats
simply at once.

Main features
-------------
* Easy to build, simple to add new corpus format.
* Fast building through performance optimizations (even written in Python).
* Supports multi-processing in parsing corpora.
* Extremely less memory usage.
* All-in-one environment. Never mind the internal procedures!
* Does not need to write codes for new corpus. Instead, add to the build
  configuration simply.

Dependencies
------------
* nltk
* colorama
* pyyaml>=5.3.1
* tqdm>=4.46.0
* tokenizers==0.8.1
* mwparserfromhell>=0.5.4
* kss==1.3.1

Installation
------------

With pip
^^^^^^^^
``langumo`` can be installed using `pip`_ as follows:

.. code-block:: bash

  $ pip install langumo

From source
^^^^^^^^^^^
You can install ``langumo`` from source by cloning the repository and running:

.. code-block:: bash

  $ git clone https://github.com/affjljoo3581/langumo.git
  $ cd langumo
  $ python setup.py install

.. _`pip`: https://pypi.org/

Command-line usage
^^^^^^^^^^^^^^^^^^

.. code-block:: bash

  usage: langumo [-h] [config]

  The unified corpus building environment for Language Models.

  positional arguments:
    config      langumo build configuration

  optional arguments:
    -h, --help  show this help message and exit
