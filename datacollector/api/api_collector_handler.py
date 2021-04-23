# © 2021 Nokia
#
# Licensed under the Apache license, version 2.0
# SPDX-License-Identifier: Apache-2.0

"""Functionalities for handling collector via API."""
import json
import logging
import os
import pathlib
import time
import uuid

from datetime import datetime, timedelta
from threading import Thread

from datacollector.collector.agent import Agent


class CollectorHandler:
    """Class for handling collector start, stop, and data retrieval via API."""

    def __init__(self):
        self._agent_list = []

    @staticmethod
    def create_run_id():
        """Create a run id for the collector."""
        date = datetime.utcnow()
        run_id = "Datacollector_" + str(uuid.uuid4())[:3] + '_' + datetime.strftime(date, "%Y-%m-%dT%H-%M-%S")
        return run_id

    @staticmethod
    def set_logging(run_id):
        """Initialize logging."""
        formatter = logging.Formatter('%(asctime)s - %(module)s - %(levelname)s - %(message)s',
                                      datefmt="%Y-%m-%dT%H:%M:%S%z")

        # Create logging handler for logging to file
        absp = pathlib.Path(__file__).parent.parent.absolute()
        abspath = absp.__str__()
        file_handler = logging.FileHandler(abspath + '/log/' + run_id + '.log')
        file_handler.setFormatter(formatter)
        file_handler.setLevel(logging.WARNING)

        # Create logging handler for logging to console
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)

        logging.basicConfig(
            level=logging.DEBUG,
            format=formatter,
            handlers=[
                file_handler,
                console_handler
            ]
        )

    @staticmethod
    def run_agent(agent):
        """Run agent thread."""
        agent.start()

    def start_agent(self, start_delta, stop_delta, interval, run_id):
        """Start collector agent."""
        self.set_logging(run_id)
        if not isinstance(start_delta, (int, float)) or not isinstance(stop_delta, (float, int)) or not \
                isinstance(interval, (float, int)) or not isinstance(run_id, str):
            raise TypeError('Invalid parameter type')
        if start_delta < 0 or stop_delta < 0 or interval <= 0:
            raise ValueError('Invalid parameter value')

        collect_start_time = datetime.utcnow() + timedelta(seconds=start_delta)
        collect_stop_time = collect_start_time + timedelta(seconds=stop_delta)
        agent = Agent(collect_start_time, collect_stop_time, interval, run_id)
        self._agent_list.append(agent)
        agent_thread = Thread(target=self.run_agent, args=[agent])
        agent_thread.start()
        while agent.is_alive():
            time.sleep(1)

    def stop_agent(self, run_id):
        """Stop agent thread."""
        for instance in self._agent_list:
            if instance.get_id == run_id:
                instance.shutdown()
                self._agent_list.remove(instance)
                return "Collector has been stopped."
        return "Instance of agent does not exist for current ID"

    def get_collection_names(self):
        """Get names of performed collection runs."""
        try:
            path = os.path.join(os.getcwd(), 'data')
            collections = [x for x in os.listdir(path)]
        except Exception:
            raise Exception("Failed to retrieve collection names.")
        return collections

    def get_collection_results(self, folder_name, file_name):
        """Get results of a collection."""
        lines = []
        try:
            path = os.path.join(os.getcwd(), 'data')
            for folder in os.listdir(path):
                if folder == folder_name:
                    file = path + "/" + folder_name + "/" +file_name + ".json"
                    with open(file) as json_data:
                        for line in json_data:
                            lines.append(json.loads(line))

        except Exception:
            raise Exception("Failed to retrieve results for the run ID.")
        return lines
