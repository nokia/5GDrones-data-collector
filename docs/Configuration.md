# Overview

To use Datacollector on remote target devices, configurations for establishing connections are required.
Additionally, if Elasticsearch is utilised, a configuration for the Elasticsearch client is also needed.

## Target device configuration

The connection configurations for target devices are defined in ``device_config.ini``-file. Reading of the configuration
file is implemented in an abstract class *IConfig*, which must be implemented as subclasses for object instantiation.
In  the reference architecture, ``connection_config_parser.py`` includes a class called *ConnectionConfig*, which implements
functionality for parsing configuration needed for establishing an SSH-connection to the example target device.
For each individual device, an unique section header name should be defined. Parameters required for the connection should
be declared below the section header. For example:
```
[device_header_name]    ;section header for a target device
hostname =              ;address
port =                  ;port number
username =              ;username
password =              ;password
```

## Database client / Elasticsearch configuration

In the reference implementation of Datacollector, the database utilized is Elasticsearch. The same abstract class can be
used as a basis for implementing any database client. 

The configurations for Elasticsearch client is defined in ``elastic_config.ini``. Similar to target device configuration,
Elasticsearch configuration is read using an implementation of *IConfig* called *ElasticConfig* in ``elastic_config_parser.py``. The configuration parameters are used in an implementation of the class *IElasticIndexer*, in the reference architecture, in *ElasticIndexer*.

```
[elastic]               ;section header for the target (Elasticsearch)
host =                  ;address (for Elasticsearch service)
port =                  ;port number (for Elasticsearch service, typically 9200)
memcpu_index =          ;name of the target index in Elasticsearch
user =                  ;username (for Elasticsearch service)
password =              ;password (for Elasticsearch service)
```