# © 2021 Nokia
#
# Licensed under the Apache license, version 2.0
# SPDX-License-Identifier: Apache-2.0

"""Abstract class for handling collection from a node."""
import logging
import os
import pathlib
import time
import uuid
from abc import ABC, abstractmethod
from threading import Event, Thread

from datacollector.collector.any_event import AnyEvent
from datacollector.collector.sshconnection import TooManyRetriesException


class CollectionFailedException(Exception):
    """Raised when unable to collect properly."""


class NoConnectionException(Exception):
    """This exception is raised when there is error with pinging the host."""


class UnhandledException(Exception):
    """Raised when unable to collect properly."""


class INodeCollector(ABC, Thread):
    """Holds the needed functionality and information for each node.
    Abstract methods to be implemented.
    """

    def __init__(self, main_collector, connection):
        """Initialize node collector."""
        super().__init__()
        self._main_collector = main_collector
        self._connection = connection
        self.events = self._create_events()
        self.collecting = False
        self.success = False
        self._node_run_id = self._create_node_run_id()
        self._create_dirs()

        # Add initializations of objects from implementations of IRecord and IConnection
        # self._connection = connection
        # self._record = Record( ... )

    @staticmethod
    def _create_events():
        stop_event = Event()
        collect_event = Event()
        any_event = AnyEvent(stop_event, collect_event)
        return {"stop": stop_event, "collect": collect_event, "any": any_event}

    @property
    def _stop_event(self):
        """Getter for self.events["stop"]."""
        return self.events["stop"]

    @property
    def _collect_event(self):
        """Getter for self.events["collect"]."""
        return self.events["collect"]

    @property
    def _any_event(self):
        """Getter for self.events["any"]."""
        return self.events["any"]

    @property
    def connection(self):
        """Getter for self._connection."""
        return self._connection

    @property
    def node_run_id(self):
        """Getter for self._node_run_id."""
        return self._node_run_id

    def _create_node_run_id(self):
        """Create a node specific test id."""
        uid = str(uuid.uuid4())[:8]
        run_id = self._main_collector.agent.collect_id + '_' + uid
        return run_id

    def stop(self):
        """Interface for other threads to set stop event."""
        self._stop_event.set()

    def collect(self):
        """Interface for other threads to set collect event."""
        self._collect_event.set()

    def _connect_to_node(self):
        """Create a separate connection for the collector."""
        try:

            if self._main_collector.lock_status:
                while self._main_collector.lock_status:
                    time.sleep(0.5)
            self._main_collector.lock_connections()
            self._connection.connect(via=None)
            self._main_collector.unlock_connections()

        except TooManyRetriesException:
            self._main_collector.unlock_connections()
            self.stop()
        except Exception:
            self._main_collector.unlock_connections()
            self.stop()

    def run(self):
        """Handle waiting and collect cycle.

        Thread stays idle until any event happens. Then it checks event type
        (collect or stop) and acts accordingly. Collect event first
        executes collection and then reports to main collector.
        """
        logging.getLogger('__collector__').info("Started thread for: %s", self._connection.hostname)

        try:
            self._connect_to_node()
            if self._connection.test_connection():
                self._wait_and_handle_events()
            else:
                raise NoConnectionException
        except NoConnectionException:
            logging.getLogger('__collector__').exception("%s NoConnection exception:",
                                                         self._connection.hostname)
        logging.getLogger('__collector__').info("%s finished.", self._connection.hostname)
        self.stop()

    def _wait_and_handle_events(self):
        """Wait until an event is set."""
        try:
            while self._any_event.wait():
                if self._stop_event.is_set():
                    break
                if self._collect_event.is_set():
                    self._collect_event.clear()
                    self._handle_collect_event()
        except Exception:
            raise UnhandledException()

    def _handle_collect_event(self):
        """Handle collecting event wraps the collecting function."""
        self.collecting = True
        logging.getLogger('__collector__').info("%s started collecting.", self._connection.hostname)
        self._try_collect()
        self.collecting = False
        logging.getLogger('__collector__').info("%s finished collecting, success: %s.",
                                                self._connection.hostname, self.success)
        self._main_collector.node_finished()

    def _create_dirs(self):
        try:
            logging.getLogger('__collector__').info("Creating folders for data...")
            absp = pathlib.Path(__file__).parent.parent.absolute()
            abspath = absp.__str__()
            os.makedirs(abspath + '/data/' + self._node_run_id)
        except FileExistsError:
            logging.getLogger('__collector__').debug("Folder already exists, skipping...")

    @abstractmethod
    def _try_collect(self):
        """Collect the data. Log if errors occur.

        Implement actual collection method calls in class extensions.
        For example:
        try:
            # *Collection methods here*
            self.success = True

        except Exception as e:
            logging.getLogger('__collector__').error("%s collecting Failed: %s",
                                                     self._connection.hostname, str(e))
            raise UnhandledException()
        """
        pass
