# openapi_client.MaintenanceApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**get_maintenance_needs_top_left_correction**](MaintenanceApi.md#get_maintenance_needs_top_left_correction) | **GET** /maintenance/needs-top-left-correction | 
[**get_maintenance_was_top_left_correction_applied**](MaintenanceApi.md#get_maintenance_was_top_left_correction_applied) | **GET** /maintenance/was-top-left-correction-applied | 
[**post_maintenance_name**](MaintenanceApi.md#post_maintenance_name) | **POST** /maintenance/{name} | 
[**post_report_asset_overview**](MaintenanceApi.md#post_report_asset_overview) | **POST** /report/asset-overview | 


# **get_maintenance_needs_top_left_correction**
> str get_maintenance_needs_top_left_correction()

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
    api_instance = openapi_client.MaintenanceApi(api_client)

    try:
        api_response = api_instance.get_maintenance_needs_top_left_correction()
        print("The response of MaintenanceApi->get_maintenance_needs_top_left_correction:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling MaintenanceApi->get_maintenance_needs_top_left_correction: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

**str**

### Authorization

[httpAuth](../README.md#httpAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: text/plain, application/json

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

# **get_maintenance_was_top_left_correction_applied**
> str get_maintenance_was_top_left_correction_applied()

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
    api_instance = openapi_client.MaintenanceApi(api_client)

    try:
        api_response = api_instance.get_maintenance_was_top_left_correction_applied()
        print("The response of MaintenanceApi->get_maintenance_was_top_left_correction_applied:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling MaintenanceApi->get_maintenance_was_top_left_correction_applied: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

**str**

### Authorization

[httpAuth](../README.md#httpAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: text/plain, application/json

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

# **post_maintenance_name**
> str post_maintenance_name(name, restrict_to_projects=restrict_to_projects)

Authorization: admin scope required.

### Example

* Bearer Authentication (httpAuth):

```python
import openapi_client
from openapi_client.models.action_name import ActionName
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
    api_instance = openapi_client.MaintenanceApi(api_client)
    name = openapi_client.ActionName() # ActionName | The name of the action to be performed
    restrict_to_projects = ['restrict_to_projects_example'] # List[str] | Restrict the action to a list of projects, if no project is given apply the action to all projects. (optional)

    try:
        api_response = api_instance.post_maintenance_name(name, restrict_to_projects=restrict_to_projects)
        print("The response of MaintenanceApi->post_maintenance_name:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling MaintenanceApi->post_maintenance_name: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **name** | [**ActionName**](.md)| The name of the action to be performed | 
 **restrict_to_projects** | [**List[str]**](str.md)| Restrict the action to a list of projects, if no project is given apply the action to all projects. | [optional] 

### Return type

**str**

### Authorization

[httpAuth](../README.md#httpAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: text/plain, application/json

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

# **post_report_asset_overview**
> str post_report_asset_overview()

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
    api_instance = openapi_client.MaintenanceApi(api_client)

    try:
        api_response = api_instance.post_report_asset_overview()
        print("The response of MaintenanceApi->post_report_asset_overview:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling MaintenanceApi->post_report_asset_overview: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

**str**

### Authorization

[httpAuth](../README.md#httpAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: text/plain, application/json

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

