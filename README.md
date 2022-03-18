# Insights Analytics Collector

This package helps with collecting data by user-defined collector methods. 
It packs collected data to one or more tarballs and sends them to user-defined URL.

Some data and classes has to be implemented.
By function:
- persisting settings
- data like credentials, content type etc. for shipping (POST request)

By Classes:
- Collector
- Package
- collector_module: 
  - functions with `@register` decorator, one with `config=True, format='json'`
  - slicing functions (optional) for splitting large data (db tables) by time intervals

## Implement Collector 

Collector is an Abstract class, implement abstract methods.

- `_package_class`: Returns class of your implementation of Package   
- `_is_valid_license`: Check for valid license specific to your service
- `_is_shipping_configured`: Check if shipping to cloud is configured
- `_last_gathering`: returns datetime. Loading last successful run from some persistent storage
- `_save_last_gather`: Persisting last successful run
- `_load_last_gathered_entries`: Has to fill dictionary `self.last_gathered_entries`. Load from persistent storage 
  Dict contains keys equal to collector's registered functions' keys (with @register decorator)
- `_save_last_gathered_entries`: Persisting `self.last_gathered_entries` 

An example can be found in [Test collector](tests/classes/analytics_collector.py)

## Implement Package

Package is also abstract class. You have to implement basically info for POST request to cloud.

- `PAYLOAD_CONTENT_TYPE`: contains registered content type for cloud's ingress service
- `MAX_DATA_SIZE`: maximum size in bytes of **uncompressed** data for one tarball. Ingress limits uploads to 100MB. Defaults to
  200MB.
- `get_ingress_url`: Cloud's ingress service URL
- `_get_rh_user`: User for POST request 
- `_get_rh_password`: Password for POST request
- `_get_x_rh_identity`: X-RH Identity Used for local testing instead of user and password
- `_get_http_request_headers`: Dict with any custom headers for POST request 
 
An example can be found in [Test package](tests/classes/package.py)

## Collector module

Module with gathering functions is the main part you need to implement.
It should contain functions returning data either in `dict` format or list of CSV files.

Function is registered by `@register` decorator:
```python
from insights_analytics_collector import register

@register('json_data', '1.0', format='json', description="Data description")
def json_data(**kwargs):
    return {'my_data': 'True'}
```

Decorator `@register` has following attributes:
- **key**: (string) name of output file (usually the same as function name)
- **version**: (string) i.e. '1.0'. Version of data - added to the manifest.json for parsing on cloud's side
- **description**: (string)  not used yet
- **format**: (string) Default: 'json' extension of output file, can be "json" of "csv". Also determines function output. 
- **config**: (bool) Default: False. there **has to be one** function with `config=True, format=json`
- **fnc_slicing**: Intended for large data. Described in [Slicing function](#slicing-function) below 
- **shipping_group**: (string) Default: 'default'. Splits data to packages by group, if required.


```python
from <your-namespace> import Collector  # your implementation

collector = Collector
collector.gather()

```

### Slicing function

## Collectors


## Registered collectors


## Abstract classes


## Tarballs
