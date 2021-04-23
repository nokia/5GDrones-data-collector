# Overview

The reference implementation of Datacollector can be run by using a handler script ``run.py`` or via API, 
which can be started with ``run_api.py``.

## Without API

To start the collector, run e.g., the following from project root directory using Python 3 from console:  
``
python datacollector/run.py
``  
or   
``
python -m datacollector.run
``
```

usage: run.py [-h] [-s START] [-e END] [-i INTERVAL]

Set start, end, and collection interval values for datacollector.

optional arguments:
  -h, --help            show this help message and exit
  -s START, --start START
                        Time interval to start the collector. In seconds. Must
                        be a positive integer.
  -e END, --end END     Time interval to stop the collector. In seconds. Must
                        be a positive integer.
  -i INTERVAL, --interval INTERVAL
                        Time interval between individual collection events. In
                        seconds. Must be a positive integer.
                        
```

To stop the collector, exit the terminal/prompt.

## With API

To use the collector with API, run ``run_api.py`` from project root folder using Python 3 from console, e.g.:  
``
python datacollector/run_api.py
``  
or  
``
python -m datacollector.run_api
``

### API usage

By default, the api runs at 127.0.0.1:5000.

#### Start collector

Start the collector instance. 
-   Method: POST, endpoint: 127.0.0.1:5000/api/start
-   Body:
```
{
	"start": 5,
	"stop": 30,
	"interval": 3
}
```
- Response:
```
{
    "ret": "ok",
    "message": "Parameters for starting the collector received.", 
    "id": "Data_collector_e1a_2020-11-10T09-49-18"
}
```

#### Stop collector

Use the id from the start-command response to stop the collector instance.
- Method: POST, endpoint: 127.0.0.1:5000/api/stop
- Body:
```
{
    "id": "Data_collector_e1a_2020-11-10T09-49-18"
}
```
- Response:
```
{
    "message": "Collector has been stopped."
}
```
#### Get collection IDs

Get a list of all collections runs currently locally saved at Datacollector.
- Method: GET, endpoint: 127.0.0.1:5000/api/results/collections
- Body: None
- Response (example):
```
{
    "ret": "ok", 
    "message": "Names of collections retrieved successfully.", 
    "data": ["Datacollector_022_2020-11-24T08-57-20_ddf45f50", "Datacollector_152_2020-11-24T08-52-32_8f833b0d"]
}
```

### Get collection results

Get collected data for a specific collection run.
- Method: GET, endpoint: 127.0.0.1:5000/api/results/collections/[id]/[target_device_hostname]
- Body: None
- Response (example):
```
{
    "ret": "ok", 
    "message": "Results for collection retrieved successfully.", 
    "data": [<collected_data_as_json>]
}
```