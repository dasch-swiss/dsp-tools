# openapi_client.AssetsApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**get_projects_shortcode_assets_assetid**](AssetsApi.md#get_projects_shortcode_assets_assetid) | **GET** /projects/{shortcode}/assets/{assetId} | 
[**get_projects_shortcode_assets_assetid_original**](AssetsApi.md#get_projects_shortcode_assets_assetid_original) | **GET** /projects/{shortcode}/assets/{assetId}/original | 
[**post_projects_shortcode_assets_ingest_filename**](AssetsApi.md#post_projects_shortcode_assets_ingest_filename) | **POST** /projects/{shortcode}/assets/ingest/{filename} | 


# **get_projects_shortcode_assets_assetid**
> AssetInfoResponse get_projects_shortcode_assets_assetid(shortcode, asset_id)

Authorization: read:project:1234 scope required.

### Example

* Bearer Authentication (httpAuth):

```python
import openapi_client
from openapi_client.models.asset_info_response import AssetInfoResponse
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
    api_instance = openapi_client.AssetsApi(api_client)
    shortcode = '0001' # str | The shortcode of the project must be an exactly 4 characters long hexadecimal string.
    asset_id = '5RMOnH7RmAY-qKzgr431bg7' # str | The id of the asset

    try:
        api_response = api_instance.get_projects_shortcode_assets_assetid(shortcode, asset_id)
        print("The response of AssetsApi->get_projects_shortcode_assets_assetid:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AssetsApi->get_projects_shortcode_assets_assetid: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **shortcode** | **str**| The shortcode of the project must be an exactly 4 characters long hexadecimal string. | 
 **asset_id** | **str**| The id of the asset | 

### Return type

[**AssetInfoResponse**](AssetInfoResponse.md)

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

# **get_projects_shortcode_assets_assetid_original**
> bytearray get_projects_shortcode_assets_assetid_original(shortcode, asset_id)

Offers the original file for download, provided the API permisisons allow.
Authorization: JWT bearer token.

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
    api_instance = openapi_client.AssetsApi(api_client)
    shortcode = '0001' # str | The shortcode of the project must be an exactly 4 characters long hexadecimal string.
    asset_id = '5RMOnH7RmAY-qKzgr431bg7' # str | The id of the asset

    try:
        api_response = api_instance.get_projects_shortcode_assets_assetid_original(shortcode, asset_id)
        print("The response of AssetsApi->get_projects_shortcode_assets_assetid_original:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AssetsApi->get_projects_shortcode_assets_assetid_original: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **shortcode** | **str**| The shortcode of the project must be an exactly 4 characters long hexadecimal string. | 
 **asset_id** | **str**| The id of the asset | 

### Return type

**bytearray**

### Authorization

[httpAuth](../README.md#httpAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/octet-stream, application/json

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

# **post_projects_shortcode_assets_ingest_filename**
> AssetInfoResponse post_projects_shortcode_assets_ingest_filename(shortcode, filename, body)

### Example

* Bearer Authentication (httpAuth):

```python
import openapi_client
from openapi_client.models.asset_info_response import AssetInfoResponse
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
    api_instance = openapi_client.AssetsApi(api_client)
    shortcode = '0001' # str | The shortcode of the project must be an exactly 4 characters long hexadecimal string.
    filename = 'filename_example' # str | 
    body = None # bytearray | 

    try:
        api_response = api_instance.post_projects_shortcode_assets_ingest_filename(shortcode, filename, body)
        print("The response of AssetsApi->post_projects_shortcode_assets_ingest_filename:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AssetsApi->post_projects_shortcode_assets_ingest_filename: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **shortcode** | **str**| The shortcode of the project must be an exactly 4 characters long hexadecimal string. | 
 **filename** | **str**|  | 
 **body** | **bytearray**|  | 

### Return type

[**AssetInfoResponse**](AssetInfoResponse.md)

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

