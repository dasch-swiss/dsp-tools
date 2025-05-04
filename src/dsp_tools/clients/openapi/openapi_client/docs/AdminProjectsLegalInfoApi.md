# openapi_client.AdminProjectsLegalInfoApi

All URIs are relative to *https://api.dasch.swiss:443*

Method | HTTP request | Description
------------- | ------------- | -------------
[**get_admin_projects_shortcode_projectshortcode_legal_info_authorships**](AdminProjectsLegalInfoApi.md#get_admin_projects_shortcode_projectshortcode_legal_info_authorships) | **GET** /admin/projects/shortcode/{projectShortcode}/legal-info/authorships | 
[**get_admin_projects_shortcode_projectshortcode_legal_info_copyright_holders**](AdminProjectsLegalInfoApi.md#get_admin_projects_shortcode_projectshortcode_legal_info_copyright_holders) | **GET** /admin/projects/shortcode/{projectShortcode}/legal-info/copyright-holders | 
[**get_admin_projects_shortcode_projectshortcode_legal_info_licenses**](AdminProjectsLegalInfoApi.md#get_admin_projects_shortcode_projectshortcode_legal_info_licenses) | **GET** /admin/projects/shortcode/{projectShortcode}/legal-info/licenses | 
[**post_admin_projects_shortcode_projectshortcode_legal_info_copyright_holders**](AdminProjectsLegalInfoApi.md#post_admin_projects_shortcode_projectshortcode_legal_info_copyright_holders) | **POST** /admin/projects/shortcode/{projectShortcode}/legal-info/copyright-holders | 
[**put_admin_projects_shortcode_projectshortcode_legal_info_copyright_holders**](AdminProjectsLegalInfoApi.md#put_admin_projects_shortcode_projectshortcode_legal_info_copyright_holders) | **PUT** /admin/projects/shortcode/{projectShortcode}/legal-info/copyright-holders | 


# **get_admin_projects_shortcode_projectshortcode_legal_info_authorships**
> PagedResponseAuthorship get_admin_projects_shortcode_projectshortcode_legal_info_authorships(project_shortcode, knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9, page=page, page_size=page_size, filter=filter, order=order)

Get the allowed authorships for use within this project. The user must be project member, project admin or system admin.

### Example

* Basic Authentication (httpAuth1):
* Bearer Authentication (httpAuth):

```python
import openapi_client
from openapi_client.models.paged_response_authorship import PagedResponseAuthorship
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
    api_instance = openapi_client.AdminProjectsLegalInfoApi(api_client)
    project_shortcode = '0001' # str | The shortcode of a project. Must be a 4 digit hexadecimal String.
    knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9 = 'knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9_example' # str |  (optional)
    page = 1 # int | The number of the desired page to be returned. (optional) (default to 1)
    page_size = 25 # int | The number of items per page to be returned. (optional) (default to 25)
    filter = 'filter_example' # str | Filter the results. (optional)
    order = 'Asc' # str | Sort the results in ascending (asc) or descending (desc) order. (optional) (default to 'Asc')

    try:
        api_response = api_instance.get_admin_projects_shortcode_projectshortcode_legal_info_authorships(project_shortcode, knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9, page=page, page_size=page_size, filter=filter, order=order)
        print("The response of AdminProjectsLegalInfoApi->get_admin_projects_shortcode_projectshortcode_legal_info_authorships:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AdminProjectsLegalInfoApi->get_admin_projects_shortcode_projectshortcode_legal_info_authorships: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **project_shortcode** | **str**| The shortcode of a project. Must be a 4 digit hexadecimal String. | 
 **knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9** | **str**|  | [optional] 
 **page** | **int**| The number of the desired page to be returned. | [optional] [default to 1]
 **page_size** | **int**| The number of items per page to be returned. | [optional] [default to 25]
 **filter** | **str**| Filter the results. | [optional] 
 **order** | **str**| Sort the results in ascending (asc) or descending (desc) order. | [optional] [default to &#39;Asc&#39;]

### Return type

[**PagedResponseAuthorship**](PagedResponseAuthorship.md)

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

# **get_admin_projects_shortcode_projectshortcode_legal_info_copyright_holders**
> PagedResponseCopyrightHolder get_admin_projects_shortcode_projectshortcode_legal_info_copyright_holders(project_shortcode, knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9, page=page, page_size=page_size, filter=filter, order=order)

Get the allowed copyright holders for use within this project. The user must be project member, project admin or system admin.

### Example

* Basic Authentication (httpAuth1):
* Bearer Authentication (httpAuth):

```python
import openapi_client
from openapi_client.models.paged_response_copyright_holder import PagedResponseCopyrightHolder
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
    api_instance = openapi_client.AdminProjectsLegalInfoApi(api_client)
    project_shortcode = '0001' # str | The shortcode of a project. Must be a 4 digit hexadecimal String.
    knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9 = 'knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9_example' # str |  (optional)
    page = 1 # int | The number of the desired page to be returned. (optional) (default to 1)
    page_size = 25 # int | The number of items per page to be returned. (optional) (default to 25)
    filter = 'filter_example' # str | Filter the results. (optional)
    order = 'Asc' # str | Sort the results in ascending (asc) or descending (desc) order. (optional) (default to 'Asc')

    try:
        api_response = api_instance.get_admin_projects_shortcode_projectshortcode_legal_info_copyright_holders(project_shortcode, knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9, page=page, page_size=page_size, filter=filter, order=order)
        print("The response of AdminProjectsLegalInfoApi->get_admin_projects_shortcode_projectshortcode_legal_info_copyright_holders:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AdminProjectsLegalInfoApi->get_admin_projects_shortcode_projectshortcode_legal_info_copyright_holders: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **project_shortcode** | **str**| The shortcode of a project. Must be a 4 digit hexadecimal String. | 
 **knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9** | **str**|  | [optional] 
 **page** | **int**| The number of the desired page to be returned. | [optional] [default to 1]
 **page_size** | **int**| The number of items per page to be returned. | [optional] [default to 25]
 **filter** | **str**| Filter the results. | [optional] 
 **order** | **str**| Sort the results in ascending (asc) or descending (desc) order. | [optional] [default to &#39;Asc&#39;]

### Return type

[**PagedResponseCopyrightHolder**](PagedResponseCopyrightHolder.md)

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

# **get_admin_projects_shortcode_projectshortcode_legal_info_licenses**
> PagedResponseLicenseDto get_admin_projects_shortcode_projectshortcode_legal_info_licenses(project_shortcode, knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9, page=page, page_size=page_size, filter=filter, order=order)

Get the allowed licenses for use within this project. The user must be project member, project admin or system admin.

### Example

* Basic Authentication (httpAuth1):
* Bearer Authentication (httpAuth):

```python
import openapi_client
from openapi_client.models.paged_response_license_dto import PagedResponseLicenseDto
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
    api_instance = openapi_client.AdminProjectsLegalInfoApi(api_client)
    project_shortcode = '0001' # str | The shortcode of a project. Must be a 4 digit hexadecimal String.
    knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9 = 'knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9_example' # str |  (optional)
    page = 1 # int | The number of the desired page to be returned. (optional) (default to 1)
    page_size = 25 # int | The number of items per page to be returned. (optional) (default to 25)
    filter = 'filter_example' # str | Filter the results. (optional)
    order = 'Asc' # str | Sort the results in ascending (asc) or descending (desc) order. (optional) (default to 'Asc')

    try:
        api_response = api_instance.get_admin_projects_shortcode_projectshortcode_legal_info_licenses(project_shortcode, knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9, page=page, page_size=page_size, filter=filter, order=order)
        print("The response of AdminProjectsLegalInfoApi->get_admin_projects_shortcode_projectshortcode_legal_info_licenses:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AdminProjectsLegalInfoApi->get_admin_projects_shortcode_projectshortcode_legal_info_licenses: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **project_shortcode** | **str**| The shortcode of a project. Must be a 4 digit hexadecimal String. | 
 **knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9** | **str**|  | [optional] 
 **page** | **int**| The number of the desired page to be returned. | [optional] [default to 1]
 **page_size** | **int**| The number of items per page to be returned. | [optional] [default to 25]
 **filter** | **str**| Filter the results. | [optional] 
 **order** | **str**| Sort the results in ascending (asc) or descending (desc) order. | [optional] [default to &#39;Asc&#39;]

### Return type

[**PagedResponseLicenseDto**](PagedResponseLicenseDto.md)

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

# **post_admin_projects_shortcode_projectshortcode_legal_info_copyright_holders**
> post_admin_projects_shortcode_projectshortcode_legal_info_copyright_holders(project_shortcode, copyright_holder_add_request, knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9)

Add new allowed copyright holders for use within this project. The user must be a system or project admin.

### Example

* Basic Authentication (httpAuth1):
* Bearer Authentication (httpAuth):

```python
import openapi_client
from openapi_client.models.copyright_holder_add_request import CopyrightHolderAddRequest
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
    api_instance = openapi_client.AdminProjectsLegalInfoApi(api_client)
    project_shortcode = '0001' # str | The shortcode of a project. Must be a 4 digit hexadecimal String.
    copyright_holder_add_request = {"data":["DaSCH","University of Zurich"]} # CopyrightHolderAddRequest | 
    knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9 = 'knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9_example' # str |  (optional)

    try:
        api_instance.post_admin_projects_shortcode_projectshortcode_legal_info_copyright_holders(project_shortcode, copyright_holder_add_request, knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9)
    except Exception as e:
        print("Exception when calling AdminProjectsLegalInfoApi->post_admin_projects_shortcode_projectshortcode_legal_info_copyright_holders: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **project_shortcode** | **str**| The shortcode of a project. Must be a 4 digit hexadecimal String. | 
 **copyright_holder_add_request** | [**CopyrightHolderAddRequest**](CopyrightHolderAddRequest.md)|  | 
 **knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9** | **str**|  | [optional] 

### Return type

void (empty response body)

### Authorization

[httpAuth1](../README.md#httpAuth1), [httpAuth](../README.md#httpAuth)

### HTTP request headers

 - **Content-Type**: application/json
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

# **put_admin_projects_shortcode_projectshortcode_legal_info_copyright_holders**
> put_admin_projects_shortcode_projectshortcode_legal_info_copyright_holders(project_shortcode, copyright_holder_replace_request, knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9)

Update a particular allowed copyright holder for use within this project, does not update existing values on assets. The user must be a system admin.

### Example

* Basic Authentication (httpAuth1):
* Bearer Authentication (httpAuth):

```python
import openapi_client
from openapi_client.models.copyright_holder_replace_request import CopyrightHolderReplaceRequest
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
    api_instance = openapi_client.AdminProjectsLegalInfoApi(api_client)
    project_shortcode = '0001' # str | The shortcode of a project. Must be a 4 digit hexadecimal String.
    copyright_holder_replace_request = {"old-value":"DaSch","new-value":"DaSCH"} # CopyrightHolderReplaceRequest | 
    knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9 = 'knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9_example' # str |  (optional)

    try:
        api_instance.put_admin_projects_shortcode_projectshortcode_legal_info_copyright_holders(project_shortcode, copyright_holder_replace_request, knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9)
    except Exception as e:
        print("Exception when calling AdminProjectsLegalInfoApi->put_admin_projects_shortcode_projectshortcode_legal_info_copyright_holders: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **project_shortcode** | **str**| The shortcode of a project. Must be a 4 digit hexadecimal String. | 
 **copyright_holder_replace_request** | [**CopyrightHolderReplaceRequest**](CopyrightHolderReplaceRequest.md)|  | 
 **knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9** | **str**|  | [optional] 

### Return type

void (empty response body)

### Authorization

[httpAuth1](../README.md#httpAuth1), [httpAuth](../README.md#httpAuth)

### HTTP request headers

 - **Content-Type**: application/json
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

