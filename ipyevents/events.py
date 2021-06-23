from ipywidgets import CoreWidget
from ipywidgets import DOMWidget
from ipywidgets.widgets.trait_types import InstanceDict
from ipywidgets import register, widget_serialization, CallbackDispatcher
from traitlets import Unicode, List, Bool, validate, Tuple, Integer
from ._version import EXTENSION_SPEC_VERSION


@register
class Event(CoreWidget):
    """
    Add browser event handling to a jupyter widget.

    Parameters
    ----------

    source : ipywidgets-compatible widget
        The widget to be watched for events.

    watched_events : list
        List of the browser events to observe on the source.

    ignore_modifier_key_events : bool
        If ``True``, ignore key presses of modifier keys
        ('Shift', 'Control', 'Alt', 'Meta'). Useful when keys mouse events
        with modifiers are watched but you want ot ignore the modifiers by
        themselves. Default is ``False``.

    prevent_default_actions : bool
        If ``True``, do not carry out default action associated with browser
        event. One use is to prevent the browser's display of a context menu
        when right-clicking. Default is ``False``.

    xy_coordinate_system : str or ``None``
        If not ``None``, set the ``xy`` attribute to the current mouse
        position. Use `data` to get the coordinates in whatever is most
        "natural" for the widget (e.g. pixel location in an image). The
        full list of allowed coordinate systems is available through
        the ``supported_xy_coordinates`` attribute of the
        `~ipyevents.Event` widget.

    throttle_or_debounce : {``None``, 'throttle', 'debounce'}
        Method to use, if any, for limiting event rate. 'throttle is primarily
        useful for 'mousemove' and 'wheel' events. 'debounce' can be useful
        for limiting repeated key strokes or clicks. In a nutshell, throtttling
        sets a limit on the rate at which events will be passed while
        debouncing imposes a minimum time between events before a new event is
        passed. Default is ``None``.

    wait : int
        The wait time, in milliseconds, for throttling or debouncing.

    Properties
    ----------

    xy : tuple of int or float
        Location of mouse, only set if `~ipyevents.Event.xy_coordinate_system`
        is not ``None``.

    supported_key_events
        List of keyboard events that can be watched.

    supported_mouse_events
        List of mouse events that can be watched.

    supported_touch_events
        List of touch events that can be watched.

    supported_xy_coordinates
        List of supported xy coordinate systems that can be returned
        in `~ipyevents.Event.xy`.
    """
    _model_name = Unicode('EventModel').tag(sync=True)
    _model_module = Unicode('ipyevents').tag(sync=True)
    _model_module_version = Unicode(EXTENSION_SPEC_VERSION).tag(sync=True)
    source = InstanceDict(DOMWidget).tag(sync=True, **widget_serialization)
    watched_events = List().tag(sync=True)
    ignore_modifier_key_events = Bool(False).tag(sync=True)
    prevent_default_action = Bool(False).tag(sync=True)
    xy_coordinate_system = Unicode(allow_none=True).tag(sync=True, default=None)
    xy = List().tag(sync=True)
    wait = Integer().tag(sync=True, default=0)
    throttle_or_debounce = Unicode(allow_none=True).tag(sync=True, default=None)
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

    _supported_touch_events = List([
        'touchstart',
        'touchend',
        'touchmove',
        'touchcancel',
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

    _throttle_debounce_allowed = [
        None,       # No throttling or debounce
        'throttle', # Throttle the rate at which events are
                    # passed from front end to back.
        'debounce'  # Debounce events, i.e. impose minimum delay before
                    # triggering events from the front end to the back.
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

    @property
    def supported_touch_events(self):
        return self._supported_touch_events

    @property
    def supported_xy_coordinates(self):
        return self._xy_coordinate_system_allowed

    @validate('watched_events')
    def _validate_watched_events(self, proposal):
        value = proposal['value']
        supported_events = (self._supported_mouse_events +
                            self._supported_key_events +
                            self._supported_touch_events)
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

    @validate('wait')
    def _validate_wait(self, proposal):
        value = proposal['value']
        if value < 0:
            message = ('wait must be set to a non-negative integer. ')
            raise ValueError(message)
        elif not self.throttle_or_debounce:
            self.throttle_or_debounce = 'throttle'

        return value

    @validate('throttle_or_debounce')
    def _validate_throttle_debounce(self, proposal):
        value = proposal['value']
        if value not in self._throttle_debounce_allowed:
            message = ('The event rate limiting method {bad} is not supported. '
                       'The supported methods are:'
                       '\n {good}'.format(bad=value,
                                          good=self._throttle_debounce_allowed))
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

    def reset_callbacks(self):
        """Remove any previously defined callback."""
        self._dom_handlers.callbacks.clear()

    def _handle_mouse_msg(self, _, content, buffers):
        self._dom_handlers(content)
