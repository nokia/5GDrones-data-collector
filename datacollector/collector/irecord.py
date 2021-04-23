# © 2021 Nokia
#
# Licensed under the Apache license, version 2.0
# SPDX-License-Identifier: Apache-2.0

"""Abstract class handles parsing and writing data to file or other destination."""
from abc import ABC, abstractmethod


class IRecord(ABC):
    """Abstract class for data ingestion functionalities."""

    def __init__(self, filename, collector):
        """Initialize class. Initialize needed parameters."""

    @abstractmethod
    def ingest_data(self):
        """Interface method for data ingestion. Implement necessary functionalities."""
        pass
