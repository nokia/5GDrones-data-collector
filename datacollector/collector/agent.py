# © 2021 Nokia
#
# Licensed under the Apache license, version 2.0
# SPDX-License-Identifier: Apache-2.0

"""This module contains the core logic of the agent.
It starts all maincollectors and routes messages to maincollectors. """
import logging
import time
from datetime import datetime, timedelta
from threading import Event, Thread

from datacollector.collector.maincollector import MainCollector


class Agent(Thread):
    """ Agent is used to communicate messages from and to the MainCollector-Nodecollector(s)-complexe(s)."""

    def __init__(self, start_time, stop_time, collect_interval, run_id):
        """Construct agent."""
        super().__init__()
        self._collect_interval = collect_interval
        self._collect_start_time = start_time
        self._collect_stop_time = stop_time
        self._collect_id = run_id
        self._reconnect_start_time = None
        self._adapter_restart_delay = 60
        self._adapter_restart_time = 10
        self.waiting = False
        self._shutdown = False
        self.adapter = None
        self._reconnect = False

    @property
    def collect_id(self):
        """Public access for collect id."""
        return self._collect_id

    @property
    def collect_interval(self):
        """Public access for collect interval."""
        return self._collect_interval

    @property
    def collect_start_time(self):
        """Public access for collect start time."""
        return self._collect_start_time

    @property
    def get_id(self):
        """Public access for collect_id"""
        return self._collect_id

    def shutdown(self):
        """Set shutdown-value to True."""
        self._shutdown = True

    def run(self):
        self.connect()

    def reconnect(self):
        """Call self.run() after an interval has passed."""
        if not self.adapter.is_alive() and (datetime.utcnow() <= self._reconnect_start_time +
                                            timedelta(minutes=self._adapter_restart_time)):
            logging.warning("Waiting 1min before restarting")
            time.sleep(self._adapter_restart_delay)
            logging.warning("Trying to restart Adapter process")
            self.run()
        else:
            self.shutdown()

    def is_adapter_process_alive(self, stop_event):
        """Check that all adapters processes are alive."""
        logging.getLogger('__collector__').info("Process check thread started")
        while not stop_event.is_set():
            time.sleep(1)
            if not self.adapter.is_alive():
                logging.warning("Adapter process is NOT alive. Restarting collector if shutdown not called.")
                if not self._shutdown or datetime.utcnow() <= self._collect_stop_time:
                    if self._reconnect_start_time is None:
                        self._reconnect_start_time = datetime.utcnow()
                    self._reconnect = True
                self.shutdown()
                stop_event.wait(5)

    def wait_for_start(self):
        """Wait until a set collection start time has been reached."""
        logging.info("Waiting for collection start time: %s", self._collect_start_time.isoformat())
        while datetime.now() < self._collect_start_time and not self._shutdown:
            time.sleep(1)

    def connect(self):
        """Starts a loop which waits for messages from any adapters."""
        self.adapter = MainCollector(self)
        logging.info("Agent started.")
        self.wait_for_start()
        logging.info("Start time reached")
        self.adapter.start()
        logging.info("Adapter started")
        stop_event = Event()
        process_check_thread = Thread(target=self.is_adapter_process_alive, args=[stop_event])
        process_check_thread.start()

        while True:
            time.sleep(1)
            if self._shutdown or datetime.utcnow() >= self._collect_stop_time:
                logging.warning("Shutdown of this adapter instance.")
                stop_event.set()
                self.adapter.signal_stop()
                self.adapter.join()
                process_check_thread.join()
                break

        if self._reconnect:
            self._shutdown = False
            self.reconnect()
