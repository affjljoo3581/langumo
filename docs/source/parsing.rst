Parsing
=======

Overview
--------

``langumo`` supports various corpus formats by using
:class:`Parser <langumo.building.Parser>`\s.

Base class
----------

.. autoclass:: langumo.building.parsing.Parser
    :members:

Built-in Parsers
----------------

``langumo`` provides a few built-in :class:`Parser <langumo.building.Parser>` s
to use popular datasets directly, without creating new parsers.

.. automodule:: langumo.parsers.wikipedia
.. automodule:: langumo.parsers.jsonstring
