from ipywidgets import CoreWidget
from ipywidgets import DOMWidget
from ipywidgets.widgets.trait_types import InstanceDict
from ipywidgets import register, widget_serialization, CallbackDispatcher
from traitlets import Unicode, List, Bool, validate, Tuple
from ._version import EXTENSION_SPEC_VERSION


@register
class Event(CoreWidget):
    _model_name = Unicode('EventModel').tag(sync=True)
    _model_module = Unicode('ipyevents').tag(sync=True)
    _model_module_version = Unicode(EXTENSION_SPEC_VERSION).tag(sync=True)
    source = InstanceDict(DOMWidget).tag(sync=True, **widget_serialization)
    watched_events = List().tag(sync=True)
    ignore_modifier_key_events = Bool(False).tag(sync=True)
    prevent_default_action = Bool(False).tag(sync=True)
    xy_coordinate_system = Unicode(allow_none=True, default=None).tag(sync=True)
    xy = List().tag(sync=True)
    _supported_mouse_events = List([
        'click',
        'auxclick',
        'dblclick',
        'mouseenter',
        'mouseleave',
        'mousedown',
        'mouseup',
        'mousemove',
        'wheel',
        'contextmenu',
        'dragstart',
        'drag',
        'dragend',
        'dragenter',
        'dragover',
        'dragleave',
        'drop'
    ]).tag(sync=True)
    _supported_key_events = List([
        'keydown',
        'keyup'
    ]).tag(sync=True)

    _xy_coordinate_system_allowed = [
        None,       # Not tracking mouse x/y
        'data',     # "natural" coordinates for the widget (e.g. image)
        'client',   # Relative to the visible part of the web page
        'offset',   # Relative to the padding edge of widget
        'page',     # Relative to the whole document
        'relative', # Relative to the widget
        'screen'    # Relative to the screen
    ]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._dom_handlers = CallbackDispatcher()
        self.on_msg(self._handle_mouse_msg)

    @property
    def supported_key_events(self):
        return self._supported_key_events

    @property
    def supported_mouse_events(self):
        return self._supported_mouse_events

    @validate('watched_events')
    def _validate_watched_events(self, proposal):
        value = proposal['value']
        supported_events = (self._supported_mouse_events +
                            self._supported_key_events)
        bad_events = [v for v in value if v not in
                      supported_events]
        if bad_events:
            message = ('The event(s) {bad} are not supported. The supported '
                       'events are:\n {good}'.format(bad=bad_events,
                                                     good=supported_events))
            raise ValueError(message)
        return value

    @validate('xy_coordinate_system')
    def _xy_coordinate_system(self, proposal):
        value = proposal['value']
        if value not in self._xy_coordinate_system_allowed:
            message = ('The coordinates {bad} are not supported. The '
                       'supported coordinates are:'
                       '\n {good}'.format(bad=value,
                                          good=self._xy_coordinate_system_allowed))
            raise ValueError(message)
        return value

    def on_dom_event(self, callback, remove=False):
        """Register a callback to execute when a DOM event occurs.

        The callback will be called with one argument, an dict whose keys
        depend on the type of event.

        Parameters
        ----------
        remove: bool (optional)
            Set to true to remove the callback from the list of callbacks.
        """
        self._dom_handlers.register_callback(callback, remove=remove)

    def _handle_mouse_msg(self, _, content, buffers):
        self._dom_handlers(content)
