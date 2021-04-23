# © 2021 Nokia
#
# Licensed under the Apache license, version 2.0
# SPDX-License-Identifier: Apache-2.0

"""Abstract class for handling of reading and storing config information."""
import logging
import configparser
from abc import ABC, abstractmethod


class IConfig(ABC):
    """Abstract class for reading configuration files."""

    def __init__(self, config_name):
        """
        Initialize Configparser from configparser-library:
        self._config_parser = configparser.ConfigParser()

        Initialize reading from the config file.
        A section header name within device_config.ini-file is passed to the constructor.
        self._config_parser.read(config_name)

        Initialize needed variables for the config file contents. E.g.:
        self._config_name = config_name
        ...
        Read the config file.
        self._read_config()
        """

    """
    Implement properties (getters) for each variable. 
    E.g.:
    """
    @property
    @abstractmethod
    def port(self):
        """Getter for self._port."""
        # return self._port
        pass

    @abstractmethod
    def read_config(self):
        """Read the configuration from the file.
        Implement needed variables, e.g.:
        try:
            logging.info('Reading configuration from file.')
            self._hostname = self._config_parser[self._config_name]['hostname']
            ...
        except Exception as e:
            logging.error("Cannot parse configuration from file: " + str(e))
            return None
        """
        pass
