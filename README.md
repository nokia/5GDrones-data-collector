# 5G!Drones Datacollector

## Overview

Datacollector is a Python [threading](https://docs.python.org/3/library/threading.html) based low-level application for 
collecting data from target devices.

The project includes a reference implementation of Datacollector that supports collection of memory, CPU and process 
data over SSH connection from Linux OS based devices.

More information available at project [Wiki](https://github.com/nokia/5GDrones-data-collector/wiki)
or [docs](https://github.com/nokia/5GDrones-data-collector/blob/main/docs) -folder at the project root.

## Dependencies

The project requires an installation of [Python 3](https://www.python.org/downloads/).
For the development of the project, the release version 
[Python 3.7](https://www.python.org/downloads/release/python-3710/) was utilized.

The Python module dependencies are listed in 
[requirements.txt](https://github.com/nokia/5GDrones-data-collector/blob/main/requirements.txt) .

To install the requirements, run e.g., the following from the project root folder:
```
python -m pip install -r requirements.txt
```

## How to use

For more information, see project [Wiki](https://github.com/nokia/5GDrones-data-collector/wiki).
## License

5G!Drones Datacollector is licensed under Apache 2.0. For more information, see the 
[LICENSE](https://github.com/nokia/5GDrones-data-collector/blob/main/LICENSE).

## Authors

Special thanks to the original authors of the work that was used as a basis for 5G!Drones Datacollector:  
Ilari Iso-Junno ([iisojunn](https://github.com/iisojunn))  
Sami Harju ([sharju](https://github.com/sharju))  
Juha Vaaraniemi  

Authors of 5G!Drones Datacollector:  
Katri Pihlajaviita ([kpihlaja](https://github.com/kpihlaja)) - First release (Datacollector code to open-source: 
finalization, documentation, integration and releasing)  
Joonas Pulkkinen ([joopulkkin](https://github.com/joopulkkin)) - Datacollector development  
Riikka Valkama ([rvalkama](https://github.com/rvalkama)) - Datacollector development  
Laura Haapaniemi ([Lhaapani](https://github.com/Lhaapani)) - Datacollector development  