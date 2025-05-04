# openapi_client.AdminFilesApi

All URIs are relative to *https://api.dasch.swiss:443*

Method | HTTP request | Description
------------- | ------------- | -------------
[**get_admin_files_projectshortcode_filename**](AdminFilesApi.md#get_admin_files_projectshortcode_filename) | **GET** /admin/files/{projectShortcode}/{filename} | 


# **get_admin_files_projectshortcode_filename**
> PermissionCodeAndProjectRestrictedViewSettings get_admin_files_projectshortcode_filename(project_shortcode, filename, knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9)

Returns the permission code and the project's restricted view settings for a given shortcode and filename.

### Example

* Basic Authentication (httpAuth1):
* Bearer Authentication (httpAuth):

```python
import openapi_client
from openapi_client.models.permission_code_and_project_restricted_view_settings import PermissionCodeAndProjectRestrictedViewSettings
from openapi_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://api.dasch.swiss:443
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "https://api.dasch.swiss:443"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure HTTP basic authorization: httpAuth1
configuration = openapi_client.Configuration(
    username = os.environ["USERNAME"],
    password = os.environ["PASSWORD"]
)

# Configure Bearer authorization: httpAuth
configuration = openapi_client.Configuration(
    access_token = os.environ["BEARER_TOKEN"]
)

# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = openapi_client.AdminFilesApi(api_client)
    project_shortcode = '0001' # str | The shortcode of a project. Must be a 4 digit hexadecimal String.
    filename = 'filename_example' # str | 
    knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9 = 'knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9_example' # str |  (optional)

    try:
        api_response = api_instance.get_admin_files_projectshortcode_filename(project_shortcode, filename, knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9)
        print("The response of AdminFilesApi->get_admin_files_projectshortcode_filename:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AdminFilesApi->get_admin_files_projectshortcode_filename: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **project_shortcode** | **str**| The shortcode of a project. Must be a 4 digit hexadecimal String. | 
 **filename** | **str**|  | 
 **knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9** | **str**|  | [optional] 

### Return type

[**PermissionCodeAndProjectRestrictedViewSettings**](PermissionCodeAndProjectRestrictedViewSettings.md)

### Authorization

[httpAuth1](../README.md#httpAuth1), [httpAuth](../README.md#httpAuth)

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

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

