ipyevents
===============================

A custom widget fo r returning mouse and keyboard events to Python

Installation
------------

To install use pip:

    $ pip install ipyevents
    $ jupyter nbextension enable --py --sys-prefix ipyevents


For a development installation (requires npm),

    $ git clone https://github.com/mwcraig/ipyevents.git
    $ cd ipyevents
    $ pip install -e .
    $ jupyter nbextension install --py --symlink --sys-prefix ipyevents
    $ jupyter nbextension enable --py --sys-prefix ipyevents
