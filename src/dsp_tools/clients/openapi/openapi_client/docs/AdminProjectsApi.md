# openapi_client.AdminProjectsApi

All URIs are relative to *https://api.dasch.swiss:443*

Method | HTTP request | Description
------------- | ------------- | -------------
[**delete_admin_projects_iri_projectiri**](AdminProjectsApi.md#delete_admin_projects_iri_projectiri) | **DELETE** /admin/projects/iri/{projectIri} | 
[**delete_admin_projects_shortcode_projectshortcode_erase**](AdminProjectsApi.md#delete_admin_projects_shortcode_projectshortcode_erase) | **DELETE** /admin/projects/shortcode/{projectShortcode}/erase | 
[**get_admin_projects**](AdminProjectsApi.md#get_admin_projects) | **GET** /admin/projects | 
[**get_admin_projects_export**](AdminProjectsApi.md#get_admin_projects_export) | **GET** /admin/projects/export | 
[**get_admin_projects_iri_projectiri**](AdminProjectsApi.md#get_admin_projects_iri_projectiri) | **GET** /admin/projects/iri/{projectIri} | 
[**get_admin_projects_iri_projectiri_admin_members**](AdminProjectsApi.md#get_admin_projects_iri_projectiri_admin_members) | **GET** /admin/projects/iri/{projectIri}/admin-members | 
[**get_admin_projects_iri_projectiri_alldata**](AdminProjectsApi.md#get_admin_projects_iri_projectiri_alldata) | **GET** /admin/projects/iri/{projectIri}/AllData | 
[**get_admin_projects_iri_projectiri_keywords**](AdminProjectsApi.md#get_admin_projects_iri_projectiri_keywords) | **GET** /admin/projects/iri/{projectIri}/Keywords | 
[**get_admin_projects_iri_projectiri_members**](AdminProjectsApi.md#get_admin_projects_iri_projectiri_members) | **GET** /admin/projects/iri/{projectIri}/members | 
[**get_admin_projects_iri_projectiri_restrictedviewsettings**](AdminProjectsApi.md#get_admin_projects_iri_projectiri_restrictedviewsettings) | **GET** /admin/projects/iri/{projectIri}/RestrictedViewSettings | 
[**get_admin_projects_keywords**](AdminProjectsApi.md#get_admin_projects_keywords) | **GET** /admin/projects/Keywords | 
[**get_admin_projects_shortcode_projectshortcode**](AdminProjectsApi.md#get_admin_projects_shortcode_projectshortcode) | **GET** /admin/projects/shortcode/{projectShortcode} | 
[**get_admin_projects_shortcode_projectshortcode_admin_members**](AdminProjectsApi.md#get_admin_projects_shortcode_projectshortcode_admin_members) | **GET** /admin/projects/shortcode/{projectShortcode}/admin-members | 
[**get_admin_projects_shortcode_projectshortcode_members**](AdminProjectsApi.md#get_admin_projects_shortcode_projectshortcode_members) | **GET** /admin/projects/shortcode/{projectShortcode}/members | 
[**get_admin_projects_shortcode_projectshortcode_restrictedviewsettings**](AdminProjectsApi.md#get_admin_projects_shortcode_projectshortcode_restrictedviewsettings) | **GET** /admin/projects/shortcode/{projectShortcode}/RestrictedViewSettings | 
[**get_admin_projects_shortname_projectshortname**](AdminProjectsApi.md#get_admin_projects_shortname_projectshortname) | **GET** /admin/projects/shortname/{projectShortname} | 
[**get_admin_projects_shortname_projectshortname_admin_members**](AdminProjectsApi.md#get_admin_projects_shortname_projectshortname_admin_members) | **GET** /admin/projects/shortname/{projectShortname}/admin-members | 
[**get_admin_projects_shortname_projectshortname_members**](AdminProjectsApi.md#get_admin_projects_shortname_projectshortname_members) | **GET** /admin/projects/shortname/{projectShortname}/members | 
[**get_admin_projects_shortname_projectshortname_restrictedviewsettings**](AdminProjectsApi.md#get_admin_projects_shortname_projectshortname_restrictedviewsettings) | **GET** /admin/projects/shortname/{projectShortname}/RestrictedViewSettings | 
[**post_admin_projects**](AdminProjectsApi.md#post_admin_projects) | **POST** /admin/projects | 
[**post_admin_projects_iri_projectiri_restrictedviewsettings**](AdminProjectsApi.md#post_admin_projects_iri_projectiri_restrictedviewsettings) | **POST** /admin/projects/iri/{projectIri}/RestrictedViewSettings | 
[**post_admin_projects_shortcode_projectshortcode_export**](AdminProjectsApi.md#post_admin_projects_shortcode_projectshortcode_export) | **POST** /admin/projects/shortcode/{projectShortcode}/export | 
[**post_admin_projects_shortcode_projectshortcode_export_await**](AdminProjectsApi.md#post_admin_projects_shortcode_projectshortcode_export_await) | **POST** /admin/projects/shortcode/{projectShortcode}/export-await | 
[**post_admin_projects_shortcode_projectshortcode_import**](AdminProjectsApi.md#post_admin_projects_shortcode_projectshortcode_import) | **POST** /admin/projects/shortcode/{projectShortcode}/import | 
[**post_admin_projects_shortcode_projectshortcode_restrictedviewsettings**](AdminProjectsApi.md#post_admin_projects_shortcode_projectshortcode_restrictedviewsettings) | **POST** /admin/projects/shortcode/{projectShortcode}/RestrictedViewSettings | 
[**put_admin_projects_iri_projectiri**](AdminProjectsApi.md#put_admin_projects_iri_projectiri) | **PUT** /admin/projects/iri/{projectIri} | 


# **delete_admin_projects_iri_projectiri**
> ProjectOperationResponseADM delete_admin_projects_iri_projectiri(project_iri, knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9)

Deletes a project identified by the IRI.

### Example

* Basic Authentication (httpAuth1):
* Bearer Authentication (httpAuth):

```python
import openapi_client
from openapi_client.models.project_operation_response_adm import ProjectOperationResponseADM
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
    api_instance = openapi_client.AdminProjectsApi(api_client)
    project_iri = 'http://rdfh.ch/projects/0001' # str | The IRI of a project. Must be URL-encoded.
    knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9 = 'knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9_example' # str |  (optional)

    try:
        api_response = api_instance.delete_admin_projects_iri_projectiri(project_iri, knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9)
        print("The response of AdminProjectsApi->delete_admin_projects_iri_projectiri:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AdminProjectsApi->delete_admin_projects_iri_projectiri: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **project_iri** | **str**| The IRI of a project. Must be URL-encoded. | 
 **knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9** | **str**|  | [optional] 

### Return type

[**ProjectOperationResponseADM**](ProjectOperationResponseADM.md)

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

# **delete_admin_projects_shortcode_projectshortcode_erase**
> ProjectOperationResponseADM delete_admin_projects_shortcode_projectshortcode_erase(project_shortcode, knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9, keep_assets=keep_assets)

!ATTENTION! Erase a project with the given shortcode.
This will permanently and irrecoverably remove the project and all of its assets.
Authorization: Requires system admin permissions.
Only available if the feature has been configured on the server side.

### Example

* Basic Authentication (httpAuth1):
* Bearer Authentication (httpAuth):

```python
import openapi_client
from openapi_client.models.project_operation_response_adm import ProjectOperationResponseADM
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
    api_instance = openapi_client.AdminProjectsApi(api_client)
    project_shortcode = '0001' # str | The shortcode of a project. Must be a 4 digit hexadecimal String.
    knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9 = 'knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9_example' # str |  (optional)
    keep_assets = False # bool | If set to true the assets in ingest will not be removed. (optional) (default to False)

    try:
        api_response = api_instance.delete_admin_projects_shortcode_projectshortcode_erase(project_shortcode, knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9, keep_assets=keep_assets)
        print("The response of AdminProjectsApi->delete_admin_projects_shortcode_projectshortcode_erase:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AdminProjectsApi->delete_admin_projects_shortcode_projectshortcode_erase: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **project_shortcode** | **str**| The shortcode of a project. Must be a 4 digit hexadecimal String. | 
 **knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9** | **str**|  | [optional] 
 **keep_assets** | **bool**| If set to true the assets in ingest will not be removed. | [optional] [default to False]

### Return type

[**ProjectOperationResponseADM**](ProjectOperationResponseADM.md)

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

# **get_admin_projects**
> ProjectsGetResponse get_admin_projects()

Returns all projects.

### Example


```python
import openapi_client
from openapi_client.models.projects_get_response import ProjectsGetResponse
from openapi_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://api.dasch.swiss:443
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "https://api.dasch.swiss:443"
)


# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = openapi_client.AdminProjectsApi(api_client)

    try:
        api_response = api_instance.get_admin_projects()
        print("The response of AdminProjectsApi->get_admin_projects:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AdminProjectsApi->get_admin_projects: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

[**ProjectsGetResponse**](ProjectsGetResponse.md)

### Authorization

No authorization required

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

# **get_admin_projects_export**
> List[ProjectExportInfoResponse] get_admin_projects_export(knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9)

Lists existing exports of all projects.

### Example

* Basic Authentication (httpAuth1):
* Bearer Authentication (httpAuth):

```python
import openapi_client
from openapi_client.models.project_export_info_response import ProjectExportInfoResponse
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
    api_instance = openapi_client.AdminProjectsApi(api_client)
    knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9 = 'knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9_example' # str |  (optional)

    try:
        api_response = api_instance.get_admin_projects_export(knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9)
        print("The response of AdminProjectsApi->get_admin_projects_export:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AdminProjectsApi->get_admin_projects_export: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9** | **str**|  | [optional] 

### Return type

[**List[ProjectExportInfoResponse]**](ProjectExportInfoResponse.md)

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

# **get_admin_projects_iri_projectiri**
> ProjectGetResponse get_admin_projects_iri_projectiri(project_iri)

Returns a single project identified by the IRI.

### Example


```python
import openapi_client
from openapi_client.models.project_get_response import ProjectGetResponse
from openapi_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://api.dasch.swiss:443
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "https://api.dasch.swiss:443"
)


# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = openapi_client.AdminProjectsApi(api_client)
    project_iri = 'http://rdfh.ch/projects/0001' # str | The IRI of a project. Must be URL-encoded.

    try:
        api_response = api_instance.get_admin_projects_iri_projectiri(project_iri)
        print("The response of AdminProjectsApi->get_admin_projects_iri_projectiri:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AdminProjectsApi->get_admin_projects_iri_projectiri: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **project_iri** | **str**| The IRI of a project. Must be URL-encoded. | 

### Return type

[**ProjectGetResponse**](ProjectGetResponse.md)

### Authorization

No authorization required

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

# **get_admin_projects_iri_projectiri_admin_members**
> ProjectAdminMembersGetResponseADM get_admin_projects_iri_projectiri_admin_members(project_iri, knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9)

### Example

* Basic Authentication (httpAuth1):
* Bearer Authentication (httpAuth):

```python
import openapi_client
from openapi_client.models.project_admin_members_get_response_adm import ProjectAdminMembersGetResponseADM
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
    api_instance = openapi_client.AdminProjectsApi(api_client)
    project_iri = 'http://rdfh.ch/projects/0001' # str | The IRI of a project. Must be URL-encoded.
    knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9 = 'knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9_example' # str |  (optional)

    try:
        api_response = api_instance.get_admin_projects_iri_projectiri_admin_members(project_iri, knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9)
        print("The response of AdminProjectsApi->get_admin_projects_iri_projectiri_admin_members:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AdminProjectsApi->get_admin_projects_iri_projectiri_admin_members: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **project_iri** | **str**| The IRI of a project. Must be URL-encoded. | 
 **knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9** | **str**|  | [optional] 

### Return type

[**ProjectAdminMembersGetResponseADM**](ProjectAdminMembersGetResponseADM.md)

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

# **get_admin_projects_iri_projectiri_alldata**
> bytearray get_admin_projects_iri_projectiri_alldata(project_iri, knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9)

Returns all ontologies, data, and configuration belonging to a project identified by the IRI.

### Example

* Basic Authentication (httpAuth1):
* Bearer Authentication (httpAuth):

```python
import openapi_client
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
    api_instance = openapi_client.AdminProjectsApi(api_client)
    project_iri = 'http://rdfh.ch/projects/0001' # str | The IRI of a project. Must be URL-encoded.
    knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9 = 'knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9_example' # str |  (optional)

    try:
        api_response = api_instance.get_admin_projects_iri_projectiri_alldata(project_iri, knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9)
        print("The response of AdminProjectsApi->get_admin_projects_iri_projectiri_alldata:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AdminProjectsApi->get_admin_projects_iri_projectiri_alldata: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **project_iri** | **str**| The IRI of a project. Must be URL-encoded. | 
 **knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9** | **str**|  | [optional] 

### Return type

**bytearray**

### Authorization

[httpAuth1](../README.md#httpAuth1), [httpAuth](../README.md#httpAuth)

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

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_admin_projects_iri_projectiri_keywords**
> ProjectKeywordsGetResponse get_admin_projects_iri_projectiri_keywords(project_iri)

Returns all keywords for a single project.

### Example


```python
import openapi_client
from openapi_client.models.project_keywords_get_response import ProjectKeywordsGetResponse
from openapi_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://api.dasch.swiss:443
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "https://api.dasch.swiss:443"
)


# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = openapi_client.AdminProjectsApi(api_client)
    project_iri = 'http://rdfh.ch/projects/0001' # str | The IRI of a project. Must be URL-encoded.

    try:
        api_response = api_instance.get_admin_projects_iri_projectiri_keywords(project_iri)
        print("The response of AdminProjectsApi->get_admin_projects_iri_projectiri_keywords:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AdminProjectsApi->get_admin_projects_iri_projectiri_keywords: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **project_iri** | **str**| The IRI of a project. Must be URL-encoded. | 

### Return type

[**ProjectKeywordsGetResponse**](ProjectKeywordsGetResponse.md)

### Authorization

No authorization required

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

# **get_admin_projects_iri_projectiri_members**
> ProjectMembersGetResponseADM get_admin_projects_iri_projectiri_members(project_iri, knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9)

Returns all project members of a project identified by the IRI.

### Example

* Basic Authentication (httpAuth1):
* Bearer Authentication (httpAuth):

```python
import openapi_client
from openapi_client.models.project_members_get_response_adm import ProjectMembersGetResponseADM
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
    api_instance = openapi_client.AdminProjectsApi(api_client)
    project_iri = 'http://rdfh.ch/projects/0001' # str | The IRI of a project. Must be URL-encoded.
    knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9 = 'knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9_example' # str |  (optional)

    try:
        api_response = api_instance.get_admin_projects_iri_projectiri_members(project_iri, knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9)
        print("The response of AdminProjectsApi->get_admin_projects_iri_projectiri_members:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AdminProjectsApi->get_admin_projects_iri_projectiri_members: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **project_iri** | **str**| The IRI of a project. Must be URL-encoded. | 
 **knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9** | **str**|  | [optional] 

### Return type

[**ProjectMembersGetResponseADM**](ProjectMembersGetResponseADM.md)

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

# **get_admin_projects_iri_projectiri_restrictedviewsettings**
> ProjectRestrictedViewSettingsGetResponseADM get_admin_projects_iri_projectiri_restrictedviewsettings(project_iri)

Returns the project's restricted view settings identified by the IRI.

### Example


```python
import openapi_client
from openapi_client.models.project_restricted_view_settings_get_response_adm import ProjectRestrictedViewSettingsGetResponseADM
from openapi_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://api.dasch.swiss:443
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "https://api.dasch.swiss:443"
)


# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = openapi_client.AdminProjectsApi(api_client)
    project_iri = 'http://rdfh.ch/projects/0001' # str | The IRI of a project. Must be URL-encoded.

    try:
        api_response = api_instance.get_admin_projects_iri_projectiri_restrictedviewsettings(project_iri)
        print("The response of AdminProjectsApi->get_admin_projects_iri_projectiri_restrictedviewsettings:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AdminProjectsApi->get_admin_projects_iri_projectiri_restrictedviewsettings: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **project_iri** | **str**| The IRI of a project. Must be URL-encoded. | 

### Return type

[**ProjectRestrictedViewSettingsGetResponseADM**](ProjectRestrictedViewSettingsGetResponseADM.md)

### Authorization

No authorization required

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

# **get_admin_projects_keywords**
> ProjectsKeywordsGetResponse get_admin_projects_keywords()

Returns all unique keywords for all projects as a list.

### Example


```python
import openapi_client
from openapi_client.models.projects_keywords_get_response import ProjectsKeywordsGetResponse
from openapi_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://api.dasch.swiss:443
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "https://api.dasch.swiss:443"
)


# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = openapi_client.AdminProjectsApi(api_client)

    try:
        api_response = api_instance.get_admin_projects_keywords()
        print("The response of AdminProjectsApi->get_admin_projects_keywords:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AdminProjectsApi->get_admin_projects_keywords: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

[**ProjectsKeywordsGetResponse**](ProjectsKeywordsGetResponse.md)

### Authorization

No authorization required

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

# **get_admin_projects_shortcode_projectshortcode**
> ProjectGetResponse get_admin_projects_shortcode_projectshortcode(project_shortcode)

Returns a single project identified by the shortcode.

### Example


```python
import openapi_client
from openapi_client.models.project_get_response import ProjectGetResponse
from openapi_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://api.dasch.swiss:443
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "https://api.dasch.swiss:443"
)


# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = openapi_client.AdminProjectsApi(api_client)
    project_shortcode = '0001' # str | The shortcode of a project. Must be a 4 digit hexadecimal String.

    try:
        api_response = api_instance.get_admin_projects_shortcode_projectshortcode(project_shortcode)
        print("The response of AdminProjectsApi->get_admin_projects_shortcode_projectshortcode:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AdminProjectsApi->get_admin_projects_shortcode_projectshortcode: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **project_shortcode** | **str**| The shortcode of a project. Must be a 4 digit hexadecimal String. | 

### Return type

[**ProjectGetResponse**](ProjectGetResponse.md)

### Authorization

No authorization required

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

# **get_admin_projects_shortcode_projectshortcode_admin_members**
> ProjectAdminMembersGetResponseADM get_admin_projects_shortcode_projectshortcode_admin_members(project_shortcode, knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9)

Returns all admin members of a project identified by the shortcode.

### Example

* Basic Authentication (httpAuth1):
* Bearer Authentication (httpAuth):

```python
import openapi_client
from openapi_client.models.project_admin_members_get_response_adm import ProjectAdminMembersGetResponseADM
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
    api_instance = openapi_client.AdminProjectsApi(api_client)
    project_shortcode = '0001' # str | The shortcode of a project. Must be a 4 digit hexadecimal String.
    knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9 = 'knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9_example' # str |  (optional)

    try:
        api_response = api_instance.get_admin_projects_shortcode_projectshortcode_admin_members(project_shortcode, knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9)
        print("The response of AdminProjectsApi->get_admin_projects_shortcode_projectshortcode_admin_members:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AdminProjectsApi->get_admin_projects_shortcode_projectshortcode_admin_members: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **project_shortcode** | **str**| The shortcode of a project. Must be a 4 digit hexadecimal String. | 
 **knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9** | **str**|  | [optional] 

### Return type

[**ProjectAdminMembersGetResponseADM**](ProjectAdminMembersGetResponseADM.md)

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

# **get_admin_projects_shortcode_projectshortcode_members**
> ProjectMembersGetResponseADM get_admin_projects_shortcode_projectshortcode_members(project_shortcode, knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9)

Returns all project members of a project identified by the shortcode.

### Example

* Basic Authentication (httpAuth1):
* Bearer Authentication (httpAuth):

```python
import openapi_client
from openapi_client.models.project_members_get_response_adm import ProjectMembersGetResponseADM
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
    api_instance = openapi_client.AdminProjectsApi(api_client)
    project_shortcode = '0001' # str | The shortcode of a project. Must be a 4 digit hexadecimal String.
    knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9 = 'knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9_example' # str |  (optional)

    try:
        api_response = api_instance.get_admin_projects_shortcode_projectshortcode_members(project_shortcode, knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9)
        print("The response of AdminProjectsApi->get_admin_projects_shortcode_projectshortcode_members:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AdminProjectsApi->get_admin_projects_shortcode_projectshortcode_members: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **project_shortcode** | **str**| The shortcode of a project. Must be a 4 digit hexadecimal String. | 
 **knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9** | **str**|  | [optional] 

### Return type

[**ProjectMembersGetResponseADM**](ProjectMembersGetResponseADM.md)

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

# **get_admin_projects_shortcode_projectshortcode_restrictedviewsettings**
> ProjectRestrictedViewSettingsGetResponseADM get_admin_projects_shortcode_projectshortcode_restrictedviewsettings(project_shortcode)

Returns the project's restricted view settings identified by the shortcode.

### Example


```python
import openapi_client
from openapi_client.models.project_restricted_view_settings_get_response_adm import ProjectRestrictedViewSettingsGetResponseADM
from openapi_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://api.dasch.swiss:443
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "https://api.dasch.swiss:443"
)


# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = openapi_client.AdminProjectsApi(api_client)
    project_shortcode = '0001' # str | The shortcode of a project. Must be a 4 digit hexadecimal String.

    try:
        api_response = api_instance.get_admin_projects_shortcode_projectshortcode_restrictedviewsettings(project_shortcode)
        print("The response of AdminProjectsApi->get_admin_projects_shortcode_projectshortcode_restrictedviewsettings:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AdminProjectsApi->get_admin_projects_shortcode_projectshortcode_restrictedviewsettings: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **project_shortcode** | **str**| The shortcode of a project. Must be a 4 digit hexadecimal String. | 

### Return type

[**ProjectRestrictedViewSettingsGetResponseADM**](ProjectRestrictedViewSettingsGetResponseADM.md)

### Authorization

No authorization required

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

# **get_admin_projects_shortname_projectshortname**
> ProjectGetResponse get_admin_projects_shortname_projectshortname(project_shortname)

Returns a single project identified by the shortname.

### Example


```python
import openapi_client
from openapi_client.models.project_get_response import ProjectGetResponse
from openapi_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://api.dasch.swiss:443
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "https://api.dasch.swiss:443"
)


# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = openapi_client.AdminProjectsApi(api_client)
    project_shortname = 'someShortname' # str | The shortname of a project.

    try:
        api_response = api_instance.get_admin_projects_shortname_projectshortname(project_shortname)
        print("The response of AdminProjectsApi->get_admin_projects_shortname_projectshortname:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AdminProjectsApi->get_admin_projects_shortname_projectshortname: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **project_shortname** | **str**| The shortname of a project. | 

### Return type

[**ProjectGetResponse**](ProjectGetResponse.md)

### Authorization

No authorization required

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

# **get_admin_projects_shortname_projectshortname_admin_members**
> ProjectAdminMembersGetResponseADM get_admin_projects_shortname_projectshortname_admin_members(project_shortname, knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9)

Returns all admin members of a project identified by the shortname.

### Example

* Basic Authentication (httpAuth1):
* Bearer Authentication (httpAuth):

```python
import openapi_client
from openapi_client.models.project_admin_members_get_response_adm import ProjectAdminMembersGetResponseADM
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
    api_instance = openapi_client.AdminProjectsApi(api_client)
    project_shortname = 'someShortname' # str | The shortname of a project.
    knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9 = 'knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9_example' # str |  (optional)

    try:
        api_response = api_instance.get_admin_projects_shortname_projectshortname_admin_members(project_shortname, knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9)
        print("The response of AdminProjectsApi->get_admin_projects_shortname_projectshortname_admin_members:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AdminProjectsApi->get_admin_projects_shortname_projectshortname_admin_members: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **project_shortname** | **str**| The shortname of a project. | 
 **knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9** | **str**|  | [optional] 

### Return type

[**ProjectAdminMembersGetResponseADM**](ProjectAdminMembersGetResponseADM.md)

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

# **get_admin_projects_shortname_projectshortname_members**
> ProjectMembersGetResponseADM get_admin_projects_shortname_projectshortname_members(project_shortname, knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9)

Returns all project members of a project identified by the shortname.

### Example

* Basic Authentication (httpAuth1):
* Bearer Authentication (httpAuth):

```python
import openapi_client
from openapi_client.models.project_members_get_response_adm import ProjectMembersGetResponseADM
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
    api_instance = openapi_client.AdminProjectsApi(api_client)
    project_shortname = 'someShortname' # str | The shortname of a project.
    knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9 = 'knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9_example' # str |  (optional)

    try:
        api_response = api_instance.get_admin_projects_shortname_projectshortname_members(project_shortname, knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9)
        print("The response of AdminProjectsApi->get_admin_projects_shortname_projectshortname_members:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AdminProjectsApi->get_admin_projects_shortname_projectshortname_members: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **project_shortname** | **str**| The shortname of a project. | 
 **knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9** | **str**|  | [optional] 

### Return type

[**ProjectMembersGetResponseADM**](ProjectMembersGetResponseADM.md)

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

# **get_admin_projects_shortname_projectshortname_restrictedviewsettings**
> ProjectRestrictedViewSettingsGetResponseADM get_admin_projects_shortname_projectshortname_restrictedviewsettings(project_shortname)

Returns the project's restricted view settings identified by the shortname.

### Example


```python
import openapi_client
from openapi_client.models.project_restricted_view_settings_get_response_adm import ProjectRestrictedViewSettingsGetResponseADM
from openapi_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://api.dasch.swiss:443
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "https://api.dasch.swiss:443"
)


# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = openapi_client.AdminProjectsApi(api_client)
    project_shortname = 'someShortname' # str | The shortname of a project.

    try:
        api_response = api_instance.get_admin_projects_shortname_projectshortname_restrictedviewsettings(project_shortname)
        print("The response of AdminProjectsApi->get_admin_projects_shortname_projectshortname_restrictedviewsettings:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AdminProjectsApi->get_admin_projects_shortname_projectshortname_restrictedviewsettings: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **project_shortname** | **str**| The shortname of a project. | 

### Return type

[**ProjectRestrictedViewSettingsGetResponseADM**](ProjectRestrictedViewSettingsGetResponseADM.md)

### Authorization

No authorization required

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

# **post_admin_projects**
> ProjectOperationResponseADM post_admin_projects(project_create_request, knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9)

Creates a new project.

### Example

* Basic Authentication (httpAuth1):
* Bearer Authentication (httpAuth):

```python
import openapi_client
from openapi_client.models.project_create_request import ProjectCreateRequest
from openapi_client.models.project_operation_response_adm import ProjectOperationResponseADM
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
    api_instance = openapi_client.AdminProjectsApi(api_client)
    project_create_request = openapi_client.ProjectCreateRequest() # ProjectCreateRequest | 
    knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9 = 'knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9_example' # str |  (optional)

    try:
        api_response = api_instance.post_admin_projects(project_create_request, knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9)
        print("The response of AdminProjectsApi->post_admin_projects:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AdminProjectsApi->post_admin_projects: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **project_create_request** | [**ProjectCreateRequest**](ProjectCreateRequest.md)|  | 
 **knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9** | **str**|  | [optional] 

### Return type

[**ProjectOperationResponseADM**](ProjectOperationResponseADM.md)

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

# **post_admin_projects_iri_projectiri_restrictedviewsettings**
> RestrictedViewResponse post_admin_projects_iri_projectiri_restrictedviewsettings(project_iri, set_restricted_view_request, knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9)

Sets the project's restricted view settings identified by the IRI.

### Example

* Basic Authentication (httpAuth1):
* Bearer Authentication (httpAuth):

```python
import openapi_client
from openapi_client.models.restricted_view_response import RestrictedViewResponse
from openapi_client.models.set_restricted_view_request import SetRestrictedViewRequest
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
    api_instance = openapi_client.AdminProjectsApi(api_client)
    project_iri = 'http://rdfh.ch/projects/0001' # str | The IRI of a project. Must be URL-encoded.
    set_restricted_view_request = {"size":"!128,128"} # SetRestrictedViewRequest | Set how all still image resources of a projects should be displayed when viewed as restricted. This can be either a size restriction or a watermark. For that, we support two of the (IIIF size)[https://iiif.io/api/image/3.0/#42-size] forms: * `!d,d` The returned image is scaled so that the width and height of the returned image are not greater than d, while maintaining the aspect ratio. * `pct:n` The width and height of the returned image is scaled to n percent of the width and height of the original image. 1<= n <= 100.  If the watermark is set to `true`, the returned image will be watermarked, otherwise the default size !128,128 is set.  It is only possible to set either the size or the watermark, not both at the same time.
    knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9 = 'knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9_example' # str |  (optional)

    try:
        api_response = api_instance.post_admin_projects_iri_projectiri_restrictedviewsettings(project_iri, set_restricted_view_request, knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9)
        print("The response of AdminProjectsApi->post_admin_projects_iri_projectiri_restrictedviewsettings:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AdminProjectsApi->post_admin_projects_iri_projectiri_restrictedviewsettings: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **project_iri** | **str**| The IRI of a project. Must be URL-encoded. | 
 **set_restricted_view_request** | [**SetRestrictedViewRequest**](SetRestrictedViewRequest.md)| Set how all still image resources of a projects should be displayed when viewed as restricted. This can be either a size restriction or a watermark. For that, we support two of the (IIIF size)[https://iiif.io/api/image/3.0/#42-size] forms: * &#x60;!d,d&#x60; The returned image is scaled so that the width and height of the returned image are not greater than d, while maintaining the aspect ratio. * &#x60;pct:n&#x60; The width and height of the returned image is scaled to n percent of the width and height of the original image. 1&lt;&#x3D; n &lt;&#x3D; 100.  If the watermark is set to &#x60;true&#x60;, the returned image will be watermarked, otherwise the default size !128,128 is set.  It is only possible to set either the size or the watermark, not both at the same time. | 
 **knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9** | **str**|  | [optional] 

### Return type

[**RestrictedViewResponse**](RestrictedViewResponse.md)

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

# **post_admin_projects_shortcode_projectshortcode_export**
> post_admin_projects_shortcode_projectshortcode_export(project_shortcode, knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9)

Trigger an export of a project identified by the shortcode.

### Example

* Basic Authentication (httpAuth1):
* Bearer Authentication (httpAuth):

```python
import openapi_client
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
    api_instance = openapi_client.AdminProjectsApi(api_client)
    project_shortcode = '0001' # str | The shortcode of a project. Must be a 4 digit hexadecimal String.
    knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9 = 'knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9_example' # str |  (optional)

    try:
        api_instance.post_admin_projects_shortcode_projectshortcode_export(project_shortcode, knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9)
    except Exception as e:
        print("Exception when calling AdminProjectsApi->post_admin_projects_shortcode_projectshortcode_export: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **project_shortcode** | **str**| The shortcode of a project. Must be a 4 digit hexadecimal String. | 
 **knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9** | **str**|  | [optional] 

### Return type

void (empty response body)

### Authorization

[httpAuth1](../README.md#httpAuth1), [httpAuth](../README.md#httpAuth)

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

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **post_admin_projects_shortcode_projectshortcode_export_await**
> ProjectExportInfoResponse post_admin_projects_shortcode_projectshortcode_export_await(project_shortcode, knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9)

Trigger an export of a project identified by the shortcode.Returns the shortcode and the export location when the process has finished successfully.

### Example

* Basic Authentication (httpAuth1):
* Bearer Authentication (httpAuth):

```python
import openapi_client
from openapi_client.models.project_export_info_response import ProjectExportInfoResponse
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
    api_instance = openapi_client.AdminProjectsApi(api_client)
    project_shortcode = '0001' # str | The shortcode of a project. Must be a 4 digit hexadecimal String.
    knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9 = 'knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9_example' # str |  (optional)

    try:
        api_response = api_instance.post_admin_projects_shortcode_projectshortcode_export_await(project_shortcode, knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9)
        print("The response of AdminProjectsApi->post_admin_projects_shortcode_projectshortcode_export_await:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AdminProjectsApi->post_admin_projects_shortcode_projectshortcode_export_await: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **project_shortcode** | **str**| The shortcode of a project. Must be a 4 digit hexadecimal String. | 
 **knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9** | **str**|  | [optional] 

### Return type

[**ProjectExportInfoResponse**](ProjectExportInfoResponse.md)

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

# **post_admin_projects_shortcode_projectshortcode_import**
> ProjectImportResponse post_admin_projects_shortcode_projectshortcode_import(project_shortcode, knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9)

Trigger an import of a project identified by the shortcode.

### Example

* Basic Authentication (httpAuth1):
* Bearer Authentication (httpAuth):

```python
import openapi_client
from openapi_client.models.project_import_response import ProjectImportResponse
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
    api_instance = openapi_client.AdminProjectsApi(api_client)
    project_shortcode = '0001' # str | The shortcode of a project. Must be a 4 digit hexadecimal String.
    knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9 = 'knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9_example' # str |  (optional)

    try:
        api_response = api_instance.post_admin_projects_shortcode_projectshortcode_import(project_shortcode, knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9)
        print("The response of AdminProjectsApi->post_admin_projects_shortcode_projectshortcode_import:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AdminProjectsApi->post_admin_projects_shortcode_projectshortcode_import: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **project_shortcode** | **str**| The shortcode of a project. Must be a 4 digit hexadecimal String. | 
 **knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9** | **str**|  | [optional] 

### Return type

[**ProjectImportResponse**](ProjectImportResponse.md)

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

# **post_admin_projects_shortcode_projectshortcode_restrictedviewsettings**
> RestrictedViewResponse post_admin_projects_shortcode_projectshortcode_restrictedviewsettings(project_shortcode, set_restricted_view_request, knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9)

Sets the project's restricted view settings identified by the shortcode.

### Example

* Basic Authentication (httpAuth1):
* Bearer Authentication (httpAuth):

```python
import openapi_client
from openapi_client.models.restricted_view_response import RestrictedViewResponse
from openapi_client.models.set_restricted_view_request import SetRestrictedViewRequest
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
    api_instance = openapi_client.AdminProjectsApi(api_client)
    project_shortcode = '0001' # str | The shortcode of a project. Must be a 4 digit hexadecimal String.
    set_restricted_view_request = {size=!128,128} # SetRestrictedViewRequest | Set how all still image resources of a projects should be displayed when viewed as restricted. This can be either a size restriction or a watermark. For that, we support two of the (IIIF size)[https://iiif.io/api/image/3.0/#42-size] forms: * `!d,d` The returned image is scaled so that the width and height of the returned image are not greater than d, while maintaining the aspect ratio. * `pct:n` The width and height of the returned image is scaled to n percent of the width and height of the original image. 1<= n <= 100.  If the watermark is set to `true`, the returned image will be watermarked, otherwise the default size !128,128 is set.  It is only possible to set either the size or the watermark, not both at the same time.
    knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9 = 'knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9_example' # str |  (optional)

    try:
        api_response = api_instance.post_admin_projects_shortcode_projectshortcode_restrictedviewsettings(project_shortcode, set_restricted_view_request, knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9)
        print("The response of AdminProjectsApi->post_admin_projects_shortcode_projectshortcode_restrictedviewsettings:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AdminProjectsApi->post_admin_projects_shortcode_projectshortcode_restrictedviewsettings: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **project_shortcode** | **str**| The shortcode of a project. Must be a 4 digit hexadecimal String. | 
 **set_restricted_view_request** | [**SetRestrictedViewRequest**](SetRestrictedViewRequest.md)| Set how all still image resources of a projects should be displayed when viewed as restricted. This can be either a size restriction or a watermark. For that, we support two of the (IIIF size)[https://iiif.io/api/image/3.0/#42-size] forms: * &#x60;!d,d&#x60; The returned image is scaled so that the width and height of the returned image are not greater than d, while maintaining the aspect ratio. * &#x60;pct:n&#x60; The width and height of the returned image is scaled to n percent of the width and height of the original image. 1&lt;&#x3D; n &lt;&#x3D; 100.  If the watermark is set to &#x60;true&#x60;, the returned image will be watermarked, otherwise the default size !128,128 is set.  It is only possible to set either the size or the watermark, not both at the same time. | 
 **knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9** | **str**|  | [optional] 

### Return type

[**RestrictedViewResponse**](RestrictedViewResponse.md)

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

# **put_admin_projects_iri_projectiri**
> ProjectOperationResponseADM put_admin_projects_iri_projectiri(project_iri, project_update_request, knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9)

Updates a project identified by the IRI.

### Example

* Basic Authentication (httpAuth1):
* Bearer Authentication (httpAuth):

```python
import openapi_client
from openapi_client.models.project_operation_response_adm import ProjectOperationResponseADM
from openapi_client.models.project_update_request import ProjectUpdateRequest
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
    api_instance = openapi_client.AdminProjectsApi(api_client)
    project_iri = 'http://rdfh.ch/projects/0001' # str | The IRI of a project. Must be URL-encoded.
    project_update_request = openapi_client.ProjectUpdateRequest() # ProjectUpdateRequest | 
    knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9 = 'knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9_example' # str |  (optional)

    try:
        api_response = api_instance.put_admin_projects_iri_projectiri(project_iri, project_update_request, knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9)
        print("The response of AdminProjectsApi->put_admin_projects_iri_projectiri:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AdminProjectsApi->put_admin_projects_iri_projectiri: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **project_iri** | **str**| The IRI of a project. Must be URL-encoded. | 
 **project_update_request** | [**ProjectUpdateRequest**](ProjectUpdateRequest.md)|  | 
 **knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9** | **str**|  | [optional] 

### Return type

[**ProjectOperationResponseADM**](ProjectOperationResponseADM.md)

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

