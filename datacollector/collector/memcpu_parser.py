# © 2021 Nokia
#
# Licensed under the Apache license, version 2.0
# SPDX-License-Identifier: Apache-2.0

"""Functionality for modifying data to be indexed to Elasticsearch.
Calculates CPU utilization based on collected data.
"""


class CpuUtilisationCalculationException(Exception):
    """Raised when CPU utilisation calculation fails."""


class MemCpuParser:
    """Provides functionalities for parsing MEMCPU data."""

    def __init__(self):
        self.run_id = None
        self._prevcpus = None
        self._no_of_cpus = None

    def get_number_of_cpus(self, row):
        """Calculate number of cpu-objects in given dict.

        Number is utilised in calculation of CPU utilisation.
        """
        self._no_of_cpus = 0
        for obj in row:
            if obj.startswith("cpu"):
                self._no_of_cpus += 1

    def create_prevcpus_dict(self):
        """Create a dict of cpu-objects. Set parameter values to zero.

        The dict is utilised to keep track of previous cpu-objects
        used in CPU utilisation calculation.

        Return the dict.
        """
        self._prevcpus = {}
        prevcpu = {"name": "cpu", "user": 0, "nice": 0, "system": 0, "idle": 0,
                   "iowait": 0, "irq": 0, "softirq": 0, "steal": 0, "guest": 0}
        self._prevcpus["cpu"] = prevcpu
        for n in range(self._no_of_cpus - 1):
            name = "cpu" + str(n)
            tempprev = prevcpu.copy()
            tempprev["name"] = name
            self._prevcpus[name] = tempprev

    def cpu_utilisation(self, cpu, prevcpu):
        """Calculate CPU utilisation.

        Utilisation is calculated based on given values:
        user, nice, system, idle, iowait, irq, softirq, steal, guest, guest_nice.

        Current CPU (cpu) and previous CPU (prevcpu) information is used.

        Calculation is based on the following algorithm:
            PrevIdle = previdle + previowait
            Idle = idle + iowait

            PrevNonIdle = prevuser + prevnice + prevsystem + previrq + prevsoftirq + prevsteal
            NonIdle = user + nice + system + irq + softirq + steal

            PrevTotal = PrevIdle + PrevNonIdle
            Total = Idle + NonIdle

            totald = Total - PrevTotal
            idled = Idle - PrevIdle

            CPU_Percentage = (totald - idled)/totald
        """
        try:
            previdle = int(prevcpu["idle"]) + int(prevcpu["iowait"])
            idle = int(cpu["idle"]) + int(cpu["iowait"])
            prevnonidle = int(prevcpu["user"]) + int(prevcpu["nice"]) + int(prevcpu["system"]) + int(
                prevcpu["irq"]) + int(
                prevcpu["softirq"]) + int(prevcpu["steal"])
            nonidle = int(cpu["user"]) + int(cpu["nice"]) + int(cpu["system"]) + int(cpu["irq"]) + int(
                cpu["softirq"]) + int(cpu["steal"])

            prevtotal = previdle + prevnonidle
            total = idle + nonidle

            totald = total - prevtotal
            idled = idle - previdle

            utilisation = ((totald - idled) / totald) * 100
        except Exception:
            raise CpuUtilisationCalculationException
        else:
            return utilisation

    def modify_memcpu_data_row(self, json_row):
        """Parse MEM/CPU information from json_row-dict.

        Call cpu_utilisation() for CPU utilisation calculation.
        prevcpus-dict includes previous CPU dicts for calculating utilisation.
        Save parsed variables and CPU utilisation to a dict.

        Return resulting dict.
        """
        final = {"timestamp": json_row["timestamp"],
                 "run_id": json_row["run_id"],
                 "memory": json_row["memory"]}

        # Parse CPU dicts from json_row
        for obj in json_row:
            if obj.startswith("cpu"):
                final[obj] = json_row[obj]

        # Handle current and previous CPU dicts
        # Call cpu_utilisation() for utilisation values calculation
        nprevcpus = {}
        for cpu in self._prevcpus:
            nprevcpus[cpu] = self._prevcpus[cpu]
            utilisation = self.cpu_utilisation(final[cpu], nprevcpus[cpu])
            nprevcpus[cpu] = final[cpu]
            final[cpu]["utilisation"] = utilisation

        self._prevcpus = nprevcpus
        return final

    def handle_memcpu_data_row(self, data_row):
        """Call correct methods for handling MEM/CPU data row (dict).

        Calculate number of cpus in row if None.
        Based on no of cpus, create previous cpus dicts for utilisation calculation if None.

        Return parsed MEM/CPU data row.
        """
        # Get number of cpu-objects
        if self._no_of_cpus is None:
            self.get_number_of_cpus(data_row)

        # Create dict of cpu-objects for tracking
        # previous cpu-objects used in CPU utilisation calculation
        if self._prevcpus is None:
            self.create_prevcpus_dict()

        # Parse MEM/CPU data row
        parsed_row = self.modify_memcpu_data_row(data_row)

        return parsed_row
