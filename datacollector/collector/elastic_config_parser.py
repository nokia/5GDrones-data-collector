# © 2021 Nokia
#
# Licensed under the Apache license, version 2.0
# SPDX-License-Identifier: Apache-2.0
"""Module for implementation of IConfig for Elasticsearch client."""

import configparser
import logging
import pathlib

from datacollector.collector.iconfig_parser import IConfig


class ElasticConfig(IConfig):
    """Implementation of IConfig for reading and saving connection configuration for Elasticsearch client."""
    def __init__(self, config_name):
        super().__init__(config_name)
        self._config_parser = configparser.ConfigParser()

        absp = pathlib.Path(__file__).parent.parent.absolute()
        abspath = absp.__str__()
        self._config_parser.read(abspath + '/config/' + 'elastic_config.ini')

        self._config_name = config_name
        self._host = None
        self._port = None
        self._user = None
        self._password = None
        self._memcpu_index = None
        self._read_config()

    @property
    def port(self):
        """Getter for self._port."""
        return self._port

    @property
    def host(self):
        """Getter for self._hostname."""
        return self._hostname

    @property
    def user(self):
        """Getter for self._username."""
        return self._username

    @property
    def password(self):
        """Getter for self._password."""
        return self._password

    @property
    def memcpu_index(self):
        """Getter for self._memcpu_index."""
        return self._memcpu_index

    def _read_config(self):
        """Read the configuration from the file."""
        try:
            logging.info('Reading configuration from file.')
            self._hostname = self._config_parser[self._config_name]['host']
            self._port = self._config_parser[self._config_name]['port']
            self._username = self._config_parser[self._config_name]['user']
            self._password = self._config_parser[self._config_name]['password']
            self._memcpu_index = self._config_parser[self._config_name]['memcpu_index']
        except Exception as e:
            logging.error("Cannot parse configuration from file: %s", str(e))
