# © 2021 Nokia
#
# Licensed under the Apache license, version 2.0
# SPDX-License-Identifier: Apache-2.0

"""Implementation from INodeCollector-class for handling collection from a node."""
import logging
from datetime import datetime
from paramiko import SSHException

from datacollector.collector.inodecollector import INodeCollector
from datacollector.collector.memcpurecord import MemCpuRecord


class CollectionFailedException(Exception):
    """Raised when unable to collect properly."""


class NoConnectionException(Exception):
    """This exception is raised when there is error with pinging the host."""


class UnhandledException(Exception):
    """Raised when unable to collect properly."""


class MemCpuNodeCollector(INodeCollector):
    """Holds the needed functionality and information for each node.
    Extends INodeCollector.
    """

    def __init__(self, main_collector, connection):
        """Initialize node collector."""
        super().__init__(main_collector, connection)
        self._connection = connection
        self._record = MemCpuRecord(connection.hostname, self)

    def _try_collect(self):
        """Call data collection and ingestion methods."""
        try:
            cpu_data = self._collect_cpu()
            mem_data = self._collect_mem()
            process_data = self._collect_process_mem()
            timestamp = datetime.utcnow().isoformat()
            self._record.ingest_data(timestamp, cpu_data, mem_data, process_data)
            self.success = True
        except ConnectionResetError or AttributeError:
            logging.error("%s collecting Failed", self._connection.hostname)
            self._connect_to_node()

        except SSHException:
            logging.error("%s collecting Failed", self._connection.hostname)
            self._connect_to_node()

        except Exception as e:
            logging.error("%s collecting Failed: %s", self._connection.hostname, str(e))
            raise UnhandledException()

    def _collect_cpu(self):
        """Collect current cpu data."""
        try:
            data = self._connection.execute('cat /proc/stat')
            if data is not None:
                return data
        except Exception as e:
            raise e

    def _collect_mem(self):
        """Collect current memory data."""
        try:
            data = self._connection.execute('cat /proc/meminfo')
            if data is not None:
                return data
        except Exception as e:
            raise e

    def _collect_process_mem(self):
        """Collect current process data."""
        try:
            data = self._connection.execute('top -b -n 1')
            if data is not None:
                return data
        except Exception as e:
            raise e
