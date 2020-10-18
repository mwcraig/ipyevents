import pytest
import traitlets

from ipyevents import Event


def test_invalid_event_name():
    # An unrecognized event name should generate a ValueError
    event_widget = Event()
    bad_name = 'this is not a valid event name'
    with pytest.raises(ValueError) as e:
        event_widget.watched_events = [bad_name]

    assert bad_name in str(e)
    assert 'not supported. The supported ' in str(e)


def test_valid_event_name():
    # A valid event name should result in that attribute being set.
    event_widget = Event()
    event_widget.watched_events = ['click']
    assert ['click'] == event_widget.watched_events


def test_setting_wait_with_no_throttle_or_debounce():
    # If wait is set to something non-zero AND neither throttle
    # nor debounce has been set then it should be set to
    # throttle.
    event_widget = Event()

    # Make sure throttle_or_debounce is not set...
    assert not event_widget.throttle_or_debounce

    # ...and that wait is currently zero
    assert event_widget.wait == 0

    # This implicitly sets throttle_or_debounce
    event_widget.wait = 20

    assert event_widget.throttle_or_debounce == 'throttle'


@pytest.mark.parametrize('slow_method', ['throttle', 'debounce'])
def test_setting_wait_with_debounce_set_preserves_debounce(slow_method):
    # If debounce is set but wait is zero and wait is then set to something
    # non-zero then throttle_or_debounce should still stay debounce.
    event_widget = Event()

    event_widget.throttle_or_debounce = slow_method

    # Make sure wait is currently zero...
    assert event_widget.wait == 0

    # This shouldn't change throttle or debounce
    event_widget.wait = 20

    assert event_widget.throttle_or_debounce == slow_method


def test_invalid_slow_method_raises_error():
    # Setting throttle_or_debounce to an invalid name should raise
    # a ValueError.
    event_widget = Event()

    bad_name = 'this is not a valid name'

    with pytest.raises(ValueError) as e:
        event_widget.throttle_or_debounce = bad_name

    assert bad_name in str(e)
    assert 'The event rate limiting method' in str(e)


def test_negative_wait_raises_error():
    # negative wait should raise an error.
    event_widget = Event()

    with pytest.raises(ValueError) as e:
        event_widget.wait = -20

    assert 'wait must be set to a non-negative integer. ' in str(e)


def test_floating_point_wait_raises_error():
    # A floating point value should reaise a TraitletError
    event_widget = Event()

    with pytest.raises(traitlets.traitlets.TraitError) as e:
        event_widget.wait = 15.0

    assert "'wait' trait of an Event instance" in str(e)


def test_setting_xy_coordinate_bad_value():
    # Setting xy_coordinate_system to a bad value should raise a ValueError
    event_widget = Event()

    bad_name = 'this is not a valid name'

    with pytest.raises(ValueError) as e:
        event_widget.xy_coordinate_system = bad_name

    assert "are not supported. The supported coordinates are" in str(e)
    assert bad_name in str(e)


def test_setting_xy_coordinates_good_value():
    # Setting to a value should just work
    event_widget = Event()
    good_name = 'data'
    event_widget.xy_coordinate_system = good_name

    assert event_widget.xy_coordinate_system == good_name


def test_properties_work():
    # These are a little silly, but will get this to 100% test coverage
    event_widget = Event()

    # Note the extra underscore on the right hand sides
    assert (event_widget.supported_key_events ==
            event_widget._supported_key_events)
    assert (event_widget.supported_mouse_events ==
            event_widget._supported_mouse_events)


def test_callbacks():
    # Test that the initial callbacks look right, that we can add one, and
    # that clearing removes them all.
    event_widget = Event()

    assert len(event_widget._dom_handlers.callbacks) == 0

    def noop(event):
        pass

    def noop2(event):
        pass

    event_widget.on_dom_event(noop)

    assert noop in event_widget._dom_handlers.callbacks
    assert len(event_widget._dom_handlers.callbacks) == 1

    # Add noop2....
    event_widget.on_dom_event(noop2)
    assert event_widget._dom_handlers.callbacks == [noop, noop2]

    # Try removing noop2
    event_widget.on_dom_event(noop2, remove=True)
    assert event_widget._dom_handlers.callbacks == [noop]

    # Finally, clear all callbacks
    event_widget.reset_callbacks()

    assert len(event_widget._dom_handlers.callbacks) == 0
