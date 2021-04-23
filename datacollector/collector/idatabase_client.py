# © 2021 Nokia
#
# Licensed under the Apache license, version 2.0
# SPDX-License-Identifier: Apache-2.0

"""Abstraction of module for sending data to database."""
import logging

from abc import ABC, abstractmethod


class ReadConfigException(Exception):
    """Raised when reading a config file fails."""


class IDatabaseClient(ABC):
    """Class for handling data uploading from collectors to a database."""

    def __init__(self):
        """Set initializations for needed parameters."""
        # e.g.:
        # self._host = None
        # self._port = None
        # self._user = None
        # self._password = None

        # Set initializations of variables for database index name(s). Read from the config file.
        # self._index = None

        # For parsing client configuration, create a Config-object (where Config is an implementation of the
        # abstract class IConfig).
        # Pass the section header which is in the config file as an argument.
        # self._config = Config('header_name')
        # self.read_config_parameters()

        # Initialize a client as needed, e.g. for Elasticsearch using elasticsearch-package:
        # self._es_client = Elasticsearch([{'host': self._host, 'port': self._port}],
        #                                http_auth=(self._user, self._password))

    @abstractmethod
    def read_config_parameters(self):
        """Read the given configuration file into a dict.
        For example, for Elasticsearch:
        try:
            self._host = self._elastic_config.host
            self._port = self._elastic_config.port
            self._index = self._elastic_config._index
            self._user = self._elastic_config.user
            self._password = self._elastic_config.password
        except Exception as e:
            logging.exception("Failed to read Elastic configuration: ", str(e))
            raise
        return
        """
        pass

    @abstractmethod
    def _bulk(self):
        """Send data to given database."""
        pass

    @abstractmethod
    def upload_data(self, data, index):
        """Implement needed methods and calls for indexing the data.
        Call bulk-function to index data to Elasticsearch.
        """
        pass
