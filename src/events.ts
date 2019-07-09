import {
    WidgetModel, unpack_models
} from '@jupyter-widgets/base';

import {
  EXTENSION_SPEC_VERSION
} from './version';

import * as _ from 'underscore';

// The names in the lists below are what will be sent as part of the
// event message to the backend.
// The actual list is constructed in _send_dom_event

let common_event_message_names = [
    'altKey',
    'ctrlKey',
    'metaKey',
    'shiftKey',
    'type',
    'timeStamp'
]

let mouse_standard_event_message_names = [
    'button',
    'buttons',
    'clientX',
    'clientY',
    'layerX',
    'layerY',
    'movementX',
    'movementY',
    'offsetX',
    'offsetY',
    'pageX',
    'pageY',
    'screenX',
    'screenY',
    'x',
    'y'
]

let mouse_added_event_message_names = [
    'dataX',
    'dataY',
    'relativeX',
    'relativeY',
    'boundingRectWidth',
    'boundingRectHeight',
    'boundingRectTop',
    'boundingRectLeft',
    'boundingRectBottom',
    'boundingRectRight',
    // Do NOT document the two below...they are deprecated.
    'arrayX',
    'arrayY'
]

let wheel_standard_event_names = [
    'deltaX',
    'deltaY',
    'deltaZ',
    'deltaMode'
]

let drag_standard_event_names = [
    'dataTransfer'
]

let key_standard_event_names = [
    'code',
    'key',
    'location',
    'repeat'
]

let listener_cache = {}

function _get_position(view, event) {
    // Return something like the position relative to the element to which
    // the listener is attached. This is essentially what layerX and layerY
    // are supposed to be (and are in chrome) but those event properties have
    // red box warnings in the MDN documentation that they are not part of any
    // standard and are not on any standards tracks, so get what we need here.
    var bounding_rect = view.el.getBoundingClientRect();
    var y_offset = bounding_rect.top;
    var x_offset = bounding_rect.left;
    return {
        'x': Math.round(event.clientX - x_offset),
        'y': Math.round(event.clientY - y_offset)
    }
}

export
class EventModel extends WidgetModel {
    static serializers = {
        ...WidgetModel.serializers,
        source: {deserialize: unpack_models}
    }

    defaults() {
        return _.extend(super.defaults(), {
            _model_name: 'EventModel',
            _model_module: 'ipyevents',
            _model_module_version: EXTENSION_SPEC_VERSION,
            source: null,
            watched_events: [],
            ignore_modifier_key_events: false,
            prevent_default_action: false,
            xy_coordinate_system: null,
            xy: [],
            _supported_mouse_events: [],
            _supported_key_events: [],
            _modifier_keys: ['Shift', 'Control', 'Alt', 'Meta']
        });
    }

    initialize(attributes, options: {model_id: string, comm?: any, widget_manager: any}) {
        super.initialize(attributes, options);
        this.on('change:source', this.prepare_source, this)
        this.on('change:watched_events', this.update_listeners, this)
        this.on('change:xy_coordinate_system', this.update_listeners, this)
        this.prepare_source()
    }

    key_or_mouse(event_type) {
        if (_.contains(this.get('_supported_mouse_events'), event_type)) {
            return 'mouse'
        }
        if (_.contains(this.get('_supported_key_events'), event_type)) {
            return 'keyboard'
        }
    }

    _cache_listeners(event_type, view, handler) {
        // Build up a cache of listeners so they can be removed if the
        // listener changes source or watched events.
        if (! listener_cache[this.model_id]) {
            listener_cache[this.model_id] = []
        }
        listener_cache[this.model_id].push({
            event: event_type,
            view: view,
            func: handler,
        })
    }

    prepare_source() {
        // Watch for changes in the models _view_count, and update
        // DOM listeners when views are created or destroyed.
        let previous_model = this.previous('source')
        this.stopListening(previous_model)

        let current_model = this.get('source')
        if (current_model.name ==  "DOMWidgetModel") {
            // We never actually listen to a bare DOMWidgetModel. However,
            // the InstanceDict trait type initializes to a basic version
            // of the required class...so effectively, we should treat
            // this model as undefined.
            return
        }

        // Check that the model has a view count
        if (! (typeof(current_model.get('_view_count')) === "number")) {
            // Sorry, but we need the view count...
            current_model.set('_view_count', 0)
        }

        this.listenTo(current_model, 'change:_view_count', this.update_listeners)
        this.update_listeners()
    }

    update_listeners() {
        // Remove all existing DOM event listeners
        this.remove_listeners()
        // Add watchers to any existing views of the model
        this.attach_listeners()
    }

    remove_listeners() {
        // Remove all of the event listeners stored in the cache.
        if (listener_cache[this.model_id]) {
            for (let listener of listener_cache[this.model_id]) {
                listener.view.el.removeEventListener(listener.event, listener.func)
            }
         }
        // Reset the list of listeners.
        listener_cache[this.model_id] = null
        // Reset the mouse position trait, if necessary...
        if (this.get('xy').length > 0) {
            this.set('xy', [])
            this.save_changes()
        }
    }

    _add_listeners_to_view(view) {
        // Add listeners for each of the watched events
        for (let event of this.get('watched_events')) {
            switch (this.key_or_mouse(event)) {
                case "keyboard":
                    this._add_key_listener(event, view)
                    break
                case "mouse":
                    let handler = this._dom_click.bind(this, view)
                    view.el.addEventListener(event, handler)
                    // Keep track of the listeners we are attaching so that we can
                    // remove them if needed.
                    this._cache_listeners(event, view, handler)
                    break
                default:
                    console.error('Not familiar with that message source')
                    break
            }
        }
        // Also add listeners to support populating the x/y traits
        if (this.get('xy_coordinate_system')) {
            let handler = this._set_xy.bind(this, view)
            let event = 'mousemove'
            view.el.addEventListener(event, handler)
            this._cache_listeners(event, view, handler)
        }
    }

    attach_listeners() {
        let current_source = this.get('source')
        _.each(current_source.views, (view_promise) => {
            Promise.resolve(view_promise).then((view) => {
                this._add_listeners_to_view(view)
            })
        })
    }

    _add_key_listener(event_type, view) {
        // Key listeners should:
        //     + Only fire when the mouse is over the element.
        //     + Not propagate up to the notebook (because imagine you
        //       press 'x' on your widget and cut the cell...not what
        //       you probably want the user to experience)
        //
        // The approach here is to add a key listener on mouseenter and remove
        // it on mouseleave.
        //
        // For JupyterLab we also need to grab the focus. Since this does not affect
        // keypress handling in the notebook in any way, don't try to check whether
        // we are in lab, just grab the focus.

        // The actual handler is here.
        let key_handler = (event) => {
            // console.log('Key presses FTW!', event)
            if (this.get('ignore_modifier_key_events') &&
               _.contains(this.get('_modifier_keys'), event.key)) {
                // If the key event is supposed to be ignored, then skip it.
                return
            }
            this._send_dom_event(event)
            // Need this (and useCapture in the listener) to prevent the keypress
            // from propagating to the notebook or browser.
            event.stopPropagation()
            event.preventDefault()
        }

        // The remainder of this attaches the handler on mouseenter and
        // removes it on mouseleave, ensuring that the element is focusable,
        // that it grabs the focus, and adding a special class to focused
        // elements to make it easier for users to override the style if
        // they so desire.
        //
        // At the end everything is restored to the state it was in before the
        // mouseenter.

        // Last argument useCapture needs to be true to prevent the event from
        // passing through to the notebook; also need to stopPropagation in key_handler.
        // useCapture ensures the event handling occurs during the capture (first)
        // phase of event handling.
        let capture_event = true

        // Add a class to this element so that the user can easily change the
        // styling when the element grabs the focus.
        let ipyevents_style_name = 'ipyevents-watched'

        // Use this to see if we added the tabindex, and if so, remove it when
        // we are done.
        let tab_index_ipyevents = "-4242"


        let enable_key_listen = () => {
            document.addEventListener(event_type, key_handler, capture_event)

            // Try to focus....
            view.el.focus()

            if (view.el != document.activeElement) {
                // We didn't actually focus, so make sure the element can be focused...
                view.el.setAttribute("tabindex", tab_index_ipyevents)
                view.el.focus()
            }
            // Add a class to make styling easy
            view.el.classList.add(ipyevents_style_name)
        }
        let disable_key_listen = () => {
            document.removeEventListener(event_type, key_handler, capture_event)

            // Remove the tabindex if we added it...
            if (view.el.getAttribute("tabindex") == tab_index_ipyevents) {
                view.el.removeAttribute("tabindex")
            }

            // No need for the styling class now that we don't have focus
            view.el.classList.remove(ipyevents_style_name)

            // Remove focus from this element. An earlier version returned
            // the focus to the element that previously had it, but that
            // resulted in a bad user experience. The browser scrolled to
            // whatever element had the focus previously, resulting in
            // completely unexpected scrolls for the user. AFAICT the
            // notebook remembers the focus independent of what is done
            // here.
            view.el.blur()
        }


        view.el.addEventListener('mouseenter', enable_key_listen)
        view.el.addEventListener('mouseleave', disable_key_listen)
        this._cache_listeners('mouseenter', view, enable_key_listen)
        this._cache_listeners('mouseleave', view, disable_key_listen)
    }

    _supplement_mouse_positions(generating_view, event) {

        // Get coordinates relative to the container
        let relative_xy = _get_position(generating_view, event)
        event['relativeX'] = relative_xy.x
        event['relativeY'] = relative_xy.y
        if ('_data_xy' in generating_view) {
            let data_coords = generating_view['_data_xy'](event)
            event['dataX'] = data_coords.x
            event['dataY'] = data_coords.y
        }
        else if (generating_view.model.get('_view_name') == 'ImageView') {
            // NO OTHER WIDGETS WILL BE SPECIAL CASED in this package.
            // Image widget from the core ipywidgets package gets special
            // treatment to ensure this works with all versions of
            // ipywidgets >= 7.0.0.
            //
            // If your custom widget has some special way of converting
            // to an _data_xy then please add that method to the widget's
            // view.
            let data_coords = _click_location_original_image(generating_view,
                                                              event);
            event['dataX'] = data_coords.x
            event['dataY'] = data_coords.y
        }
        // Also return the properties of the bounding rectangle
        var bounding_rect = generating_view.el.getBoundingClientRect()
        event['boundingRectWidth'] = bounding_rect.width
        event['boundingRectHeight'] = bounding_rect.height
        event['boundingRectTop'] = bounding_rect.top
        event['boundingRectLeft'] = bounding_rect.left
        event['boundingRectBottom'] = bounding_rect.bottom
        event['boundingRectRight'] = bounding_rect.right

        // The following is for backwards compatibility. It is deliberately
        // no longer in the documentation.
        if ('dataX' in event) {
            event['arrayX'] = event['dataX']
            event['arrayY'] = event['dataY']
        }
    }

    _dom_click(generating_view, event) {
        // Get coordinates relative to the container, and
        // data (i.e. "natural") coordinates.
        this._supplement_mouse_positions(generating_view, event)

        if ((event.type == 'wheel') || this.get('prevent_default_action')) {
            // Really want both of these, one to stop any default action
            // and the other to ensure no other listeners pick it up.
            event.preventDefault()
            event.stopPropagation()
        }
        this._send_dom_event(event)
    }

    _set_xy(generating_view, event) {
                // Get coordinates relative to the container, and
        // data (i.e. "natural") coordinates.
        this._supplement_mouse_positions(generating_view, event)
        let coord_type = this.get('xy_coordinate_system')
        let coords = [event[coord_type + 'X'], event[coord_type + 'Y']]
        if (coords[0] === undefined) {
            // The user likely asked for data/natural coordinates but
            // they are not defined for this object. Let the user know...
            console.error('No coordinates of this type found: ' + coord_type)
            return;
        }
        this.set('xy', coords)
        this.save_changes()
    }

    _send_dom_event(event) {
        // Construct the event message. The message is a dictionary, with keys
        // determined by the type of event from the list of event names above.
        //
        // Values are drawn from the DOM event object.
        let event_message = {}
        let message_names = []
        switch (this.key_or_mouse(event.type)) {
            case "mouse":
                message_names = common_event_message_names.concat(mouse_standard_event_message_names)
                message_names = message_names.concat(mouse_added_event_message_names)
                if (event.type == 'wheel') {
                    message_names = message_names.concat(wheel_standard_event_names)
                } else if (event.type == 'drop' || event.type.startsWith('drag')) {
                    message_names = message_names.concat(drag_standard_event_names)
                }
                break;
            case "keyboard":
                message_names = common_event_message_names.concat(key_standard_event_names)
                break;
            default:
                console.error('Not familiar with that message source')
                break;
        }

        for (let i of message_names) {
            event_message[i] = event[i]
        }
        event_message['event'] = event['type']
        this.send(event_message, {})
    }
}

function _click_location_original_image(view, event) {
    // Calculate the location in image units.
    // Works for ipywidgets.Image
    var pad_left = parseInt(view.el.style.paddingLeft) || 0;
    var border_left = parseInt(view.el.style.borderLeft) || 0;
    var pad_top = parseInt(view.el.style.paddingTop) || 0;
    var border_top = parseInt(view.el.style.borderTop) || 0;

    var relative_click_x = parseInt(event.relativeX) - border_left - pad_left;
    var relative_click_y = parseInt(event.relativeY) - border_top - pad_top;
    var image_x = Math.round(relative_click_x / view.el.width * view.el.naturalWidth);
    var image_y = Math.round(relative_click_y / view.el.height * view.el.naturalHeight);
    return {x: image_x, y: image_y}
}
