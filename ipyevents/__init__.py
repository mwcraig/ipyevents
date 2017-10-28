from ._version import version_info, __version__

from .events import *

def _jupyter_nbextension_paths():
    return [{
        'section': 'notebook',
        'src': 'static',
        'dest': 'ipyevents',
        'require': 'ipyevents/extension'
    }]
