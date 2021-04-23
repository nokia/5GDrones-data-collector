# © 2021 Nokia
#
# Licensed under the Apache license, version 2.0
# SPDX-License-Identifier: Apache-2.0

"""Module for handling indexing of data to Elasticsearch via an Elasticsearch client."""
import logging
from elasticsearch import Elasticsearch
from elasticsearch import helpers

from datacollector.collector.elastic_config_parser import ElasticConfig
from datacollector.collector.idatabase_client import IDatabaseClient


class ElasticException(Exception):
    """Raised when writing to Elasticsearch fails."""


class ReadConfigException(Exception):
    """Raised when reading a config file fails."""


class ElasticIndexer(IDatabaseClient):
    """Class for handling data uploading from collectors to elasticsearch."""

    def __init__(self):
        """Initialize connection parameters. Create and read using ElasticConfig.
        Initialize an Elasticsearch-client from elasticsearch-package."""
        super().__init__()
        self._host = None
        self._port = None
        self._user = None
        self._password = None
        self._memcpu_index = None

        self._elastic_config = ElasticConfig('elastic')
        self.read_config_parameters()

        self._es_client = Elasticsearch([{'host': self._host, 'port': self._port}],
                                        http_auth=(self._user, self._password))

    def read_config_parameters(self):
        """Read the config variables from the ElasticConfig-object."""
        try:
            self._host = self._elastic_config.host
            self._port = self._elastic_config.port
            self._memcpu_index = self._elastic_config.memcpu_index
            self._user = self._elastic_config.user
            self._password = self._elastic_config.password
        except Exception as e:
            logging.exception("Failed to read Elastic configuration: ", str(e))
            raise

    def _bulk(self, index, docs, timeout, max_retries):
        """Bulk index given data to given Elasticsearch index."""
        try:
            logging.getLogger('__collector__').info("Indexing to Elasticsearch.")
            _success, _errors = helpers.bulk(
                self._es_client,
                docs,
                index=index,
                request_timeout=timeout,
                max_retries=max_retries,
            )
        except Exception as e:
            logging.getLogger('__collector__').exception("Failed to index data in _bulk(): %s", str(e))

    def upload_data(self, data, index):
        """Choose an appropriate method depending on the passed data and index.
        Call bulk-function to index data to Elasticsearch.
        """
        if index == "memcpu_data":
            data_list = [data]
            self._bulk(self._memcpu_index, data_list, timeout=60, max_retries=5)
