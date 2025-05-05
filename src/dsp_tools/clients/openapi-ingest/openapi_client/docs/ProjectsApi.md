# openapi_client.ProjectsApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**delete_projects_shortcode_erase**](ProjectsApi.md#delete_projects_shortcode_erase) | **DELETE** /projects/{shortcode}/erase | 
[**get_projects**](ProjectsApi.md#get_projects) | **GET** /projects | 
[**get_projects_shortcode**](ProjectsApi.md#get_projects_shortcode) | **GET** /projects/{shortcode} | 
[**get_projects_shortcode_checksumreport**](ProjectsApi.md#get_projects_shortcode_checksumreport) | **GET** /projects/{shortcode}/checksumreport | 


# **delete_projects_shortcode_erase**
> ProjectResponse delete_projects_shortcode_erase(shortcode)

!ATTENTION! Erase a project with the given shortcode.
This will permanently and irrecoverably remove the project and all of its assets.
Authorization: admin scope required.

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
    api_instance = openapi_client.ProjectsApi(api_client)
    shortcode = '0001' # str | The shortcode of the project must be an exactly 4 characters long hexadecimal string.

    try:
        api_response = api_instance.delete_projects_shortcode_erase(shortcode)
        print("The response of ProjectsApi->delete_projects_shortcode_erase:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ProjectsApi->delete_projects_shortcode_erase: %s\n" % e)
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

# **get_projects**
> List[ProjectResponse] get_projects()

Authorization: admin scope required.

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
    api_instance = openapi_client.ProjectsApi(api_client)

    try:
        api_response = api_instance.get_projects()
        print("The response of ProjectsApi->get_projects:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ProjectsApi->get_projects: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

[**List[ProjectResponse]**](ProjectResponse.md)

### Authorization

[httpAuth](../README.md#httpAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** |  |  * Content-Range -  <br>  |
**400** |  |  -  |
**401** |  |  -  |
**403** |  |  -  |
**404** |  |  -  |
**409** |  |  -  |
**500** |  |  -  |
**503** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_projects_shortcode**
> ProjectResponse get_projects_shortcode(shortcode)

Authorization: read:project:1234 scope required.

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
    api_instance = openapi_client.ProjectsApi(api_client)
    shortcode = '0001' # str | The shortcode of the project must be an exactly 4 characters long hexadecimal string.

    try:
        api_response = api_instance.get_projects_shortcode(shortcode)
        print("The response of ProjectsApi->get_projects_shortcode:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ProjectsApi->get_projects_shortcode: %s\n" % e)
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

# **get_projects_shortcode_checksumreport**
> AssetCheckResultResponse get_projects_shortcode_checksumreport(shortcode)

Authorization: read:project:1234 scope required.

### Example

* Bearer Authentication (httpAuth):

```python
import openapi_client
from openapi_client.models.asset_check_result_response import AssetCheckResultResponse
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
    api_instance = openapi_client.ProjectsApi(api_client)
    shortcode = '0001' # str | The shortcode of the project must be an exactly 4 characters long hexadecimal string.

    try:
        api_response = api_instance.get_projects_shortcode_checksumreport(shortcode)
        print("The response of ProjectsApi->get_projects_shortcode_checksumreport:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ProjectsApi->get_projects_shortcode_checksumreport: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **shortcode** | **str**| The shortcode of the project must be an exactly 4 characters long hexadecimal string. | 

### Return type

[**AssetCheckResultResponse**](AssetCheckResultResponse.md)

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

