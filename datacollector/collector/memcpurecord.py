# © 2021 Nokia
#
# Licensed under the Apache license, version 2.0
# SPDX-License-Identifier: Apache-2.0

"""Class handles parsing and writing data into a json file."""
import json
import logging
import pathlib

from datacollector.collector.elastic_indexer import ElasticIndexer
from datacollector.collector.irecord import IRecord
from datacollector.collector.memcpu_parser import MemCpuParser


class MemCpuRecord(IRecord):
    """Class holds the functions to write the collected data into a file."""

    def __init__(self, filename, collector):
        """Initialize class."""
        super().__init__(filename, collector)
        self._filename = filename
        self._absp = pathlib.Path(__file__).parent.parent.absolute()
        self._abspath = self._absp.__str__()
        self._destination = self._abspath + '/data/'
        self._collector = collector
        self._json = {}
        self._parser = MemCpuParser()
        self._elastic = ElasticIndexer()

    def ingest_data(self, timestamp, cpu_data, mem_data, process_data):
        """Ingest data to the record class and write it into a file.
        Pass the data to ElasticWriter.
        """
        self._json = {"timestamp": timestamp, "run_id": self._collector.node_run_id}
        self._parse_cpu_data(cpu_data)
        self._json["memory"] = self._parse_mem_data(mem_data)
        parsed_memcpu = self._parser.handle_memcpu_data_row(self._json)
        self._elastic.upload_data(parsed_memcpu, index="memcpu_data")
        self._json = parsed_memcpu
        self._parse_process_data(process_data)
        self._write_to_file(self._json)

    def _parse_cpu_data(self, cpu_data):
        """Check data format from manual.

        http://man7.org/linux/man-pages/man5/proc.5.html.
        """
        for row in cpu_data:
            if 'cpu' in row:
                temp = row.split()
                self._json[temp[0]] = {"user": temp[1], "nice": temp[2],
                                      "system": temp[3], "idle": temp[4],
                                      "iowait": temp[5], "irq": temp[6],
                                      "softirq": temp[6], "steal": temp[7],
                                      "guest": temp[8], "guest_nice": temp[9]}

    def _parse_mem_data(self, data):
        """Check data format from manual.

        http://man7.org/linux/man-pages/man5/proc.5.html.
        """
        mem_data = {}
        for row in data:
            temp = row.split()
            mem_data[temp[0].strip(':')] = temp[1]
        return mem_data

    def _parse_process_data(self, data):
        """Parse process data."""
        meta = data[3].lower().split()
        process_number = 0
        for row in data[4:]:
            temp = row.split()
            if len(temp) < len(meta):
                continue
            process = {}
            for i in range(len(meta)):
                if meta[i] == "command":
                    process[meta[i]] = " ".join(temp[i:])
                else:
                    process[meta[i]] = temp[i]
            self._json["process_{}".format(process_number)] = process
            process_number = process_number + 1

    def _write_to_file(self, data):
        file = open(self._destination + self._collector.node_run_id
                    + '/' + self._filename + '.json', 'a+')
        file.write(json.dumps(data) + "\n")
