# openapi_client.BulkIngestApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**get_projects_shortcode_bulk_ingest_mapping_csv**](BulkIngestApi.md#get_projects_shortcode_bulk_ingest_mapping_csv) | **GET** /projects/{shortcode}/bulk-ingest/mapping.csv | 
[**post_projects_shortcode_bulk_ingest**](BulkIngestApi.md#post_projects_shortcode_bulk_ingest) | **POST** /projects/{shortcode}/bulk-ingest | 
[**post_projects_shortcode_bulk_ingest_finalize**](BulkIngestApi.md#post_projects_shortcode_bulk_ingest_finalize) | **POST** /projects/{shortcode}/bulk-ingest/finalize | 
[**post_projects_shortcode_bulk_ingest_ingest_file**](BulkIngestApi.md#post_projects_shortcode_bulk_ingest_ingest_file) | **POST** /projects/{shortcode}/bulk-ingest/ingest/{file} | 


# **get_projects_shortcode_bulk_ingest_mapping_csv**
> str get_projects_shortcode_bulk_ingest_mapping_csv(shortcode)

Get the current result of the bulk ingest. The result is a csv with the following structure: `original,derivative`. Will return 409 Conflict if a bulk-ingest is currently running for the project.Authorization: admin scope required.

### Example

* Bearer Authentication (httpAuth):

```python
import openapi_client
from openapi_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "http://localhost"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization: httpAuth
configuration = openapi_client.Configuration(
    access_token = os.environ["BEARER_TOKEN"]
)

# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = openapi_client.BulkIngestApi(api_client)
    shortcode = '0001' # str | The shortcode of the project must be an exactly 4 characters long hexadecimal string.

    try:
        api_response = api_instance.get_projects_shortcode_bulk_ingest_mapping_csv(shortcode)
        print("The response of BulkIngestApi->get_projects_shortcode_bulk_ingest_mapping_csv:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling BulkIngestApi->get_projects_shortcode_bulk_ingest_mapping_csv: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **shortcode** | **str**| The shortcode of the project must be an exactly 4 characters long hexadecimal string. | 

### Return type

**str**

### Authorization

[httpAuth](../README.md#httpAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: text/csv, application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** |  |  * Content-Type -  <br>  * Content-Disposition -  <br>  |
**400** |  |  -  |
**401** |  |  -  |
**403** |  |  -  |
**404** |  |  -  |
**409** |  |  -  |
**500** |  |  -  |
**503** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **post_projects_shortcode_bulk_ingest**
> ProjectResponse post_projects_shortcode_bulk_ingest(shortcode)

Triggers an ingest on the project with the given shortcode. The files are expected to be in the `tmp/<project_shortcode>` directory. Will return 409 Conflict if a bulk-ingest is currently running for the project. Authorization: admin scope required.

### Example

* Bearer Authentication (httpAuth):

```python
import openapi_client
from openapi_client.models.project_response import ProjectResponse
from openapi_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "http://localhost"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization: httpAuth
configuration = openapi_client.Configuration(
    access_token = os.environ["BEARER_TOKEN"]
)

# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = openapi_client.BulkIngestApi(api_client)
    shortcode = '0001' # str | The shortcode of the project must be an exactly 4 characters long hexadecimal string.

    try:
        api_response = api_instance.post_projects_shortcode_bulk_ingest(shortcode)
        print("The response of BulkIngestApi->post_projects_shortcode_bulk_ingest:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling BulkIngestApi->post_projects_shortcode_bulk_ingest: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **shortcode** | **str**| The shortcode of the project must be an exactly 4 characters long hexadecimal string. | 

### Return type

[**ProjectResponse**](ProjectResponse.md)

### Authorization

[httpAuth](../README.md#httpAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**202** |  |  -  |
**400** |  |  -  |
**401** |  |  -  |
**403** |  |  -  |
**404** |  |  -  |
**409** |  |  -  |
**500** |  |  -  |
**503** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **post_projects_shortcode_bulk_ingest_finalize**
> ProjectResponse post_projects_shortcode_bulk_ingest_finalize(shortcode)

Finalizes the bulk ingest. This will remove the files from the `tmp/<project_shortcode>` directory and the directory itself. This will remove also the mapping.csv file. Will return 409 Conflict if a bulk-ingest is currently running for the project. Authorization: admin scope required.

### Example

* Bearer Authentication (httpAuth):

```python
import openapi_client
from openapi_client.models.project_response import ProjectResponse
from openapi_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "http://localhost"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization: httpAuth
configuration = openapi_client.Configuration(
    access_token = os.environ["BEARER_TOKEN"]
)

# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = openapi_client.BulkIngestApi(api_client)
    shortcode = '0001' # str | The shortcode of the project must be an exactly 4 characters long hexadecimal string.

    try:
        api_response = api_instance.post_projects_shortcode_bulk_ingest_finalize(shortcode)
        print("The response of BulkIngestApi->post_projects_shortcode_bulk_ingest_finalize:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling BulkIngestApi->post_projects_shortcode_bulk_ingest_finalize: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **shortcode** | **str**| The shortcode of the project must be an exactly 4 characters long hexadecimal string. | 

### Return type

[**ProjectResponse**](ProjectResponse.md)

### Authorization

[httpAuth](../README.md#httpAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** |  |  -  |
**400** |  |  -  |
**401** |  |  -  |
**403** |  |  -  |
**404** |  |  -  |
**409** |  |  -  |
**500** |  |  -  |
**503** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **post_projects_shortcode_bulk_ingest_ingest_file**
> UploadResponse post_projects_shortcode_bulk_ingest_ingest_file(shortcode, file, body)

Uploads a file for consumption with the bulk-ingest route.Will return 409 Conflict if a bulk-ingest is currently running for the project.Authorization: admin scope required.

### Example

* Bearer Authentication (httpAuth):

```python
import openapi_client
from openapi_client.models.upload_response import UploadResponse
from openapi_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "http://localhost"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization: httpAuth
configuration = openapi_client.Configuration(
    access_token = os.environ["BEARER_TOKEN"]
)

# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = openapi_client.BulkIngestApi(api_client)
    shortcode = '0001' # str | The shortcode of the project must be an exactly 4 characters long hexadecimal string.
    file = 'file_example' # str | 
    body = None # bytearray | 

    try:
        api_response = api_instance.post_projects_shortcode_bulk_ingest_ingest_file(shortcode, file, body)
        print("The response of BulkIngestApi->post_projects_shortcode_bulk_ingest_ingest_file:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling BulkIngestApi->post_projects_shortcode_bulk_ingest_ingest_file: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **shortcode** | **str**| The shortcode of the project must be an exactly 4 characters long hexadecimal string. | 
 **file** | **str**|  | 
 **body** | **bytearray**|  | 

### Return type

[**UploadResponse**](UploadResponse.md)

### Authorization

[httpAuth](../README.md#httpAuth)

### HTTP request headers

 - **Content-Type**: application/octet-stream
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** |  |  -  |
**400** |  |  -  |
**401** |  |  -  |
**403** |  |  -  |
**404** |  |  -  |
**409** |  |  -  |
**500** |  |  -  |
**503** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

