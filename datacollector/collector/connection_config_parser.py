# © 2021 Nokia
#
# Licensed under the Apache license, version 2.0
# SPDX-License-Identifier: Apache-2.0
"""Module for IConfig implementation for a NodeCollector."""

import configparser
import logging
import pathlib

from datacollector.collector.iconfig_parser import IConfig


class ConnectionConfig(IConfig):
    """Implementation of IConfig for a NodeCollector connection configuration."""
    def __init__(self, config_name):
        super().__init__(config_name)
        self._config_parser = configparser.ConfigParser()

        absp = pathlib.Path(__file__).parent.parent.absolute()
        abspath = absp.__str__()
        self._config_parser.read(abspath + '/config/' + 'device_config.ini')

        self._config_name = config_name
        self._hostname = ""
        self._port = ""
        self._username = ""
        self._password = ""
        self.read_config()

    @property
    def port(self):
        """Getter for self._port."""
        return self._port

    @property
    def hostname(self):
        """Getter for self._hostname."""
        return self._hostname

    @property
    def username(self):
        """Getter for self._username."""
        return self._username

    @property
    def password(self):
        """Getter for self._password."""
        return self._password

    def read_config(self):
        """Read the configuration from the file."""
        try:
            logging.info('Reading configuration from file.')
            self._hostname = self._config_parser[self._config_name]['hostname']
            self._port = self._config_parser[self._config_name]['port']
            self._username = self._config_parser[self._config_name]['username']
            self._password = self._config_parser[self._config_name]['password']
        except Exception as e:
            logging.error("Cannot parse configuration from file: %s", str(e))
