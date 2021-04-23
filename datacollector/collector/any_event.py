# © 2021 Nokia
#
# Licensed under the Apache license, version 2.0
# SPDX-License-Identifier: Apache-2.0

"""
This module provides AnyEvent class to create a combination event from multiple events.

Example usage:
foo_event = Event()
bar_event = Event()
any_event = AnyEvent(foo_event, bar_event)
while any_event.wait():  # Blocking wait call.
    if foo_event.is_set():
        # handle my event
    if bar_event.is_set():
        # handle other event
"""

from threading import Event


class AnyEvent(Event):
    """Creates combination event from multiple input events.

    Returned event will be triggered if any input event is triggered.
    """

    def __init__(self, *events):
        """AnyEvent initialization"""
        super().__init__()

        def changed():
            booleans = [_event.is_set() for _event in events]
            if any(booleans):
                self.set()
            else:
                self.clear()

        for event in events:
            AnyEvent.anify(event, changed)

        changed()

    @staticmethod
    def any_set(event):
        """Event internal setter override."""
        # noinspection PyProtectedMember
        event._set()  # pylint: disable=W0212
        event.changed()

    @staticmethod
    def any_clear(event):
        """Event internal clear override."""
        # noinspection PyProtectedMember
        event._clear()  # pylint: disable=W0212
        event.changed()

    @staticmethod
    def anify(event, changed_callback):
        """Modifies events so that they are linked to any event."""
        event._set = event.set  # pylint: disable=W0212
        event._clear = event.clear  # pylint: disable=W0212
        event.changed = changed_callback
        event.set = lambda: AnyEvent.any_set(event)
        event.clear = lambda: AnyEvent.any_clear(event)
