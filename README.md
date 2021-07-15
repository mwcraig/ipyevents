# ipyevents

## Browsers events for your jupyter widgets

*ipyevents* provides a custom widget for returning mouse and keyboard events to
Python. Use it to:

 - add keyboard shortcuts to an existing widget;
 - react to the user clicking on an image;
 - add callbacks on arbitrary mouse and keyboard events.

See [this demo notebook](docs/events.ipynb) for documentation.

Special thanks to the [contributors to `ipyevents`](CONTRIBUTORS.md)!

## Try it on binder:

Dev version:
[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/mwcraig/ipyevents/HEAD?filepath=docs%2Fevents.ipynb)

## Documentation

[![Documentation Status](https://readthedocs.org/projects/ipyevents/badge/?version=latest)](https://ipyevents.readthedocs.io/en/latest/?badge=latest)


## Installation


To install using `conda`:

```bash
$ conda install -c conda-forge ipyevents
```

To install use `pip`:

    $ pip install ipyevents

Using with JupyterLab (whether you installed with `conda` or `pip`):

+ The stable releases of ipyevents (`2.0.0` and higher) are only built for JupyterLab 3 and up.
+ The last release that is built for JupyterLab 2 is 0.9.0. See the [README for that version](https://github.com/mwcraig/ipyevents/tree/0.9.0) for installation instructions.

```bash
$ jupyter labextension install @jupyter-widgets/jupyterlab-manager ipyevents
```

### For a development installation (requires npm),

```bash
$ git clone https://github.com/mwcraig/ipyevents.git
$ cd ipyevents
$ pip install -e .
$ jupyter nbextension install --py --symlink --sys-prefix ipyevents
$ jupyter nbextension enable --py --sys-prefix ipyevents
```

For Jupyter Lab also do this:

```bash
$ npm install
$ npm run build
$ jupyter labextension install
```
