Building
========

Overview
--------
``langumo`` is an unified corpus building environment. Precisely, ``langumo``
is an integrated build-pipeline which consists of micro-building layers. The
layers are independent in building and only uses the given input auxiliary
files. ``langumo`` internally uses the builders for building corpus dataset by
constructing the integrated pipeline with them.

Base class
----------

.. autoclass:: langumo.building.base.Builder
    :members:

Implementations
---------------

.. automodule:: langumo.building.parsing
.. automodule:: langumo.building.mergence
.. automodule:: langumo.building.shuffling
.. automodule:: langumo.building.tokenization
.. automodule:: langumo.building.splitting
.. automodule:: langumo.building.miscellaneous
