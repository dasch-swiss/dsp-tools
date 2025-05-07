# openapi_client.ImportExportApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**get_projects_shortcode_import**](ImportExportApi.md#get_projects_shortcode_import) | **GET** /projects/{shortcode}/import | 
[**post_projects_shortcode_export**](ImportExportApi.md#post_projects_shortcode_export) | **POST** /projects/{shortcode}/export | 


# **get_projects_shortcode_import**
> UploadResponse get_projects_shortcode_import(shortcode, content_type, body)

Authorization: admin scope required.

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
    api_instance = openapi_client.ImportExportApi(api_client)
    shortcode = '0001' # str | The shortcode of the project must be an exactly 4 characters long hexadecimal string.
    content_type = 'application/zip' # str | 
    body = None # bytearray | 

    try:
        api_response = api_instance.get_projects_shortcode_import(shortcode, content_type, body)
        print("The response of ImportExportApi->get_projects_shortcode_import:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ImportExportApi->get_projects_shortcode_import: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **shortcode** | **str**| The shortcode of the project must be an exactly 4 characters long hexadecimal string. | 
 **content_type** | **str**|  | 
 **body** | **bytearray**|  | 

### Return type

[**UploadResponse**](UploadResponse.md)

### Authorization

[httpAuth](../README.md#httpAuth)

### HTTP request headers

 - **Content-Type**: application/zip
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

# **post_projects_shortcode_export**
> bytearray post_projects_shortcode_export(shortcode)

Authorization: admin scope required.

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
    api_instance = openapi_client.ImportExportApi(api_client)
    shortcode = '0001' # str | The shortcode of the project must be an exactly 4 characters long hexadecimal string.

    try:
        api_response = api_instance.post_projects_shortcode_export(shortcode)
        print("The response of ImportExportApi->post_projects_shortcode_export:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ImportExportApi->post_projects_shortcode_export: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **shortcode** | **str**| The shortcode of the project must be an exactly 4 characters long hexadecimal string. | 

### Return type

**bytearray**

### Authorization

[httpAuth](../README.md#httpAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/zip, application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** |  |  * Content-Disposition -  <br>  * Content-Type -  <br>  |
**400** |  |  -  |
**401** |  |  -  |
**403** |  |  -  |
**404** |  |  -  |
**409** |  |  -  |
**500** |  |  -  |
**503** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

