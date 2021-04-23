# Overview

The reference implementation of Datacollector collects memory, CPU and process data over SSH from a remote Linux OS
based machine. The data is saved locally as JSON-files and indexed to Elasticsearch in real time.

## Data ingestion

Data ingestion is handled in an implementation of *IRecord*-abstract class. In the reference implementation of
Datacollector, the implementation of the class is *Record*, which saves data to JSON-files and calls 
*IDatabaseClient*-implementation *ElasticIndexer* to send the data to an Elasticsearch instance. The actual data 
collection functions are implemented in *MemCpuNodeCollector*-class.

## Local datafile structure

The reference implementation of Datacollector saves the data to local JSON-files. Data from each nodecollector is saved 
to its own folder-file-structure. 

The files are saved using the following structure:
```
data/
├── Datacollector_abc_2020-11-24T07-19-29_abcd1234/
│   └── 127.0.0.1.json
├── Datacollector_abc_2020-11-24T07-19-29_efgh5678/
│   └── 127.0.0.2.json
```
In this structure:
- ``data``: main folder for saving collected data
- ``Datacollector_[agent_id]_2020-11-24T07-19-29_[nodecollector_id]``: subfolder for saving collected data from 
  a specific 
  nodecollector. The name utilises the run ID specific for each nodecollector, which is composed of an agent specific 
  run ID (Datacollector_[agent_id]_[timestamp]) and a unique, nodecollector specific ID. Agent ID is common for all 
  maincollector-nodecollector(s) units running under it. Nodecollector ID is unique for each nodecollector. 
  The timestamp is in UTC, and added when the agent specific run ID is created.
- ``[ip].json``: the actual data JSON-file, named using the target device hostname
## Commands used by the collector

The reference implementation includes colleting memory, CPU and processes related data from Linux OS systems.

### Memory

The memory data is collected using the following command:

```
cat /proc/meminfo
```

### CPU

The CPU data is collected using the following command:

```
cat /proc/stat
```

The most relevant information provided by the command, CPU utilization percentage, has to be calculated separately. 
The functionality for the calculation is provided in ``memcpu_parser.py``. The utilization percentage is calculated with
the following algorithm:
```
# Example output of cat /proc/stat:
     user    nice   system  idle      iowait irq   softirq  steal  guest  guest_nice
cpu  74608   2520   24433   1117073   6176   4054  0        0      0      0

# Prev-prefix refers to the previous output of the command
PrevIdle = previdle + previowait
Idle = idle + iowait

PrevNonIdle = prevuser + prevnice + prevsystem + previrq + prevsoftirq + prevsteal
NonIdle = user + nice + system + irq + softirq + steal

PrevTotal = PrevIdle + PrevNonIdle
Total = Idle + NonIdle

totald = Total - PrevTotal
idled = Idle - PrevIdle

CPU_utilisation = (totald - idled)/totald
```

### Process

The process data is collected with the following command:
```
top -b -n 1
```

## Data model

Datacollector prodcues nested JSON-data that includes the collected data.
Includes:
- ``timestamp``: variable, in UTC,  ISO-8601
- ``run_id``: variable, an identifier for a specific NodeCollector (device)
- ``cpu``: object, includes CPU data, total of all CPU cores
- ``cpu0..n``: object(s), CPU core specific data
- ``memory``: object, memory related data
- ``process_0..n``: object(s), process related data

The following shows an example of the data model:
```
{
	"timestamp": "2020-10-16T06:41:05.881504",
	"run_id": "Data_collector_2020-10-16T06-41-02_d6408b1f",
        "memory": {
		"MemTotal": "28803616",
		"MemFree": "27841200",
		"MemAvailable": "28058048",
		"Buffers": "44012",
		"Cached": "481248",
		"SwapCached": "0",
		"Active": "281428",
		"Inactive": "371976",
		"Active(anon)": "127564",
		"Inactive(anon)": "3548",
		"Active(file)": "153864",
		"Inactive(file)": "368428",
		"Unevictable": "0",
		"Mlocked": "0",
		"SwapTotal": "2097148",
		"SwapFree": "2097148",
		"Dirty": "984",
		"Writeback": "0",
		"AnonPages": "127892",
		"Mapped": "150548",
		"Shmem": "4412",
		"Slab": "174228",
		"SReclaimable": "70272",
		"SUnreclaim": "103956",
		"KernelStack": "6672",
		"PageTables": "11112",
		"NFS_Unstable": "0",
		"Bounce": "0",
		"WritebackTmp": "0",
		"CommitLimit": "16498956",
		"Committed_AS": "1358440",
		"VmallocTotal": "34359738367",
		"VmallocUsed": "0",
		"VmallocChunk": "0",
		"HardwareCorrupted": "0",
		"AnonHugePages": "0",
		"ShmemHugePages": "0",
		"ShmemPmdMapped": "0",
		"CmaTotal": "0",
		"CmaFree": "0",
		"HugePages_Total": "0",
		"HugePages_Free": "0",
		"HugePages_Rsvd": "0",
		"HugePages_Surp": "0",
		"Hugepagesize": "2048",
		"DirectMap4k": "207648",
		"DirectMap2M": "3981312",
		"DirectMap1G": "27262976"
	},
	"cpu": {
		"user": "480",
		"nice": "0",
		"system": "1060",
		"idle": "128113",
		"iowait": "241",
		"irq": "0",
		"softirq": "0",
		"steal": "20",
		"guest": "0",
		"guest_nice": "0"
	},
	"cpu0": {
		"user": "28",
		"nice": "0",
		"system": "39",
		"idle": "7108",
		"iowait": "3",
		"irq": "0",
		"softirq": "0",
		"steal": "8",
		"guest": "0",
		"guest_nice": "0"
	},
        ...
	"cpun": {
		...
	},
	"process_0": {
		"kib": "KiB",
		"mem": "Swap:",
		":": "2097148",
		"28803616": "total,",
		"total,": "2097148",
		"27840628": "free,",
		"free,": "0",
		"367456": "used.",
		"used,": "28057476",
		"595532": "avail",
		"buff/cache": "Mem"
	},
        ...
	"process_n":{
        ...
        }
}
``` 