# © 2021 Nokia
#
# Licensed under the Apache license, version 2.0
# SPDX-License-Identifier: Apache-2.0

"""Class for handling collector threads."""
import logging
import time
from datetime import datetime
from threading import Event, Thread

from datacollector.collector.connection_config_parser import ConnectionConfig
from datacollector.collector.memcpunodecollector import MemCpuNodeCollector
from datacollector.collector.sshconnection import SshConnection


class UnhandledException(Exception):
    """Raised when unable to collect properly."""


class NoNodesException(Exception):
    """Raised when no nodes are discovered."""


class MainCollector(Thread):
    """Maincollector class."""

    def __init__(self, agent):
        """Initialize main collector."""
        super().__init__(daemon=True)
        self.agent = agent
        self.stop = False
        self.name = "{addition}-{default}".format(addition=type(self).__name__, default=self.name)
        self._config = None
        self._reconnect_lock = False
        self._stop_event = Event()
        self._collect_interval = agent.collect_interval
        self._start_time = agent.collect_start_time
        self._collect_start_time = datetime.min
        self._node_collectors = []

    @property
    def collect_interval(self):
        """Public access for collect_interval."""
        return self._collect_interval

    @property
    def start_time(self):
        """Public access for start_time."""
        return self._start_time

    @property
    def lock_status(self):
        """Public access for lock_status"""
        return self._reconnect_lock

    @property
    def config(self):
        """Public access for config."""
        return self._config

    def lock_connections(self):
        """Set reconnect_lock to True."""
        self._reconnect_lock = True

    def unlock_connections(self):
        """Set reconnect_lock to False."""
        self._reconnect_lock = False

    def node_finished(self):
        """Interface for NodeCollector threads to report when they have finished.

        Last thread that finishes informs adapter that data has been collected.
        """
        if self._all_nodes_finished():
            elapsed_time = datetime.utcnow() - self._collect_start_time
            logging.info("Time elapsed during collection: %ss", elapsed_time)

    def run(self):
        """Check when we can stop. See _run method."""
        logging.info("%s started.", self.name)
        while not self.stop:
            self._run()
        logging.info("%s finished.", self.name)

    def signal_stop(self):
        """Call after StopCollector message."""
        logging.debug("%s Received stop signal", self.name)
        self.stop = True
        self._stop_event.set()

    def _read_config(self):
        self._config.read_config()

    def _all_nodes_finished(self):
        return all(not collector.collecting for
                   collector in self._node_collectors)

    def _run(self):
        """Start collector threads and triggers first collection immediately.
        Then triggers collection between every collect interval.
        """
        try:
            self._main_logic()
        except Exception as e:
            logging.error(self.name + " unhandled exception" + str(e))
        self.stop = True

    def _main_logic(self):
        """Run main logic."""
        try:
            logging.info("Running MainCollector _main_logic...")
            self._create_node_collectors()
            self._start_node_collectors()
            self.agent._reconnect_start_time = None
            self.agent._reconnect = False
            self._collect()  # Trigger first collection immediately.
            while not self._stop_event.wait(timeout=self._collect_interval) and self._node_collectors != []:
                self._collect()
            self._collect()  # Collect last time after stop event has been set.
            time.sleep(self._collect_interval)
            self._stop_node_collectors()
        except Exception as e:
            logging.warning("Collector ran into an issue. Shutting down...")
            self.stop = True

    def _create_node_collectors(self):
        logging.info("Creating NodeCollectors...")
        """Create NodeCollectors with implemented ConnectionConfig- and IConnection-objects."""
        self._config = ConnectionConfig('device')
        self._node_collectors.append(MemCpuNodeCollector(self, SshConnection(self._config.hostname, self._config.port,
                                                                             self._config.username,
                                                                             self._config.password)))

    def _start_node_collectors(self):
        logging.info("Starting NodeCollectors...")
        if not self._node_collectors:
            raise NoNodesException

        for collector in self._node_collectors:
            collector.start()

    def _collect(self):
        """Distribute collect command to all NodeCollector threads.

        If last collection is still ongoing, skips the new
        incoming request.
        There is some delay between starting collectors,
        so that ssh connections get time to authenticate themselves.
        """
        if not self._check_alive_collectors():
            self.signal_stop()

        if not self._all_nodes_finished():
            logging.warning(
                "New collect ordered before last one was finished, skipping.")
            return

        logging.info("Triggering new collection for all nodes.")
        self._collect_start_time = datetime.utcnow()
        for collector in self._node_collectors:
            collector.collect()

    def _stop_node_collectors(self):
        """Set stop flag for each NodeCollector thread and then waits for them to join."""
        logging.info("%s stopping node collector threads.", self.name)
        for collector in self._node_collectors:
            collector.connection.close_session()
            collector.stop()
        for collector in self._node_collectors:
            collector.join()
        logging.info("%s all node collectors stopped.", self.name)

    def _check_alive_collectors(self):
        for collector in self._node_collectors:
            if not collector.isAlive():
                return False
        return True
