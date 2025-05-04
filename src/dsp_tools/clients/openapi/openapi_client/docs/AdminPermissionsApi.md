# openapi_client.AdminPermissionsApi

All URIs are relative to *https://api.dasch.swiss:443*

Method | HTTP request | Description
------------- | ------------- | -------------
[**delete_admin_permissions_permissioniri**](AdminPermissionsApi.md#delete_admin_permissions_permissioniri) | **DELETE** /admin/permissions/{permissionIri} | 
[**get_admin_permissions_ap_projectiri**](AdminPermissionsApi.md#get_admin_permissions_ap_projectiri) | **GET** /admin/permissions/ap/{projectIri} | 
[**get_admin_permissions_ap_projectiri_groupiri**](AdminPermissionsApi.md#get_admin_permissions_ap_projectiri_groupiri) | **GET** /admin/permissions/ap/{projectIri}/{groupIri} | 
[**get_admin_permissions_doap_projectiri**](AdminPermissionsApi.md#get_admin_permissions_doap_projectiri) | **GET** /admin/permissions/doap/{projectIri} | 
[**get_admin_permissions_projectiri**](AdminPermissionsApi.md#get_admin_permissions_projectiri) | **GET** /admin/permissions/{projectIri} | 
[**post_admin_permissions_ap**](AdminPermissionsApi.md#post_admin_permissions_ap) | **POST** /admin/permissions/ap | 
[**post_admin_permissions_doap**](AdminPermissionsApi.md#post_admin_permissions_doap) | **POST** /admin/permissions/doap | 
[**put_admin_permissions_doap_permissioniri**](AdminPermissionsApi.md#put_admin_permissions_doap_permissioniri) | **PUT** /admin/permissions/doap/{permissionIri} | 
[**put_admin_permissions_permissioniri_group**](AdminPermissionsApi.md#put_admin_permissions_permissioniri_group) | **PUT** /admin/permissions/{permissionIri}/group | 
[**put_admin_permissions_permissioniri_haspermissions**](AdminPermissionsApi.md#put_admin_permissions_permissioniri_haspermissions) | **PUT** /admin/permissions/{permissionIri}/hasPermissions | 
[**put_admin_permissions_permissioniri_property**](AdminPermissionsApi.md#put_admin_permissions_permissioniri_property) | **PUT** /admin/permissions/{permissionIri}/property | 
[**put_admin_permissions_permissioniri_resourceclass**](AdminPermissionsApi.md#put_admin_permissions_permissioniri_resourceclass) | **PUT** /admin/permissions/{permissionIri}/resourceClass | 


# **delete_admin_permissions_permissioniri**
> PermissionDeleteResponseADM delete_admin_permissions_permissioniri(permission_iri, knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9)

Delete an permission.

### Example

* Basic Authentication (httpAuth1):
* Bearer Authentication (httpAuth):

```python
import openapi_client
from openapi_client.models.permission_delete_response_adm import PermissionDeleteResponseADM
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
    api_instance = openapi_client.AdminPermissionsApi(api_client)
    permission_iri = 'http://rdfh.ch/permissions/00FF/Mck2xJDjQ_Oimi_9z4aFaA' # str | The IRI of a permission. Must be URL-encoded.
    knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9 = 'knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9_example' # str |  (optional)

    try:
        api_response = api_instance.delete_admin_permissions_permissioniri(permission_iri, knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9)
        print("The response of AdminPermissionsApi->delete_admin_permissions_permissioniri:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AdminPermissionsApi->delete_admin_permissions_permissioniri: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **permission_iri** | **str**| The IRI of a permission. Must be URL-encoded. | 
 **knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9** | **str**|  | [optional] 

### Return type

[**PermissionDeleteResponseADM**](PermissionDeleteResponseADM.md)

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

# **get_admin_permissions_ap_projectiri**
> AdministrativePermissionsForProjectGetResponseADM get_admin_permissions_ap_projectiri(project_iri, knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9)

Get all administrative permissions for a project.

### Example

* Basic Authentication (httpAuth1):
* Bearer Authentication (httpAuth):

```python
import openapi_client
from openapi_client.models.administrative_permissions_for_project_get_response_adm import AdministrativePermissionsForProjectGetResponseADM
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
    api_instance = openapi_client.AdminPermissionsApi(api_client)
    project_iri = 'http://rdfh.ch/projects/0001' # str | The IRI of a project. Must be URL-encoded.
    knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9 = 'knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9_example' # str |  (optional)

    try:
        api_response = api_instance.get_admin_permissions_ap_projectiri(project_iri, knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9)
        print("The response of AdminPermissionsApi->get_admin_permissions_ap_projectiri:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AdminPermissionsApi->get_admin_permissions_ap_projectiri: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **project_iri** | **str**| The IRI of a project. Must be URL-encoded. | 
 **knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9** | **str**|  | [optional] 

### Return type

[**AdministrativePermissionsForProjectGetResponseADM**](AdministrativePermissionsForProjectGetResponseADM.md)

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

# **get_admin_permissions_ap_projectiri_groupiri**
> AdministrativePermissionGetResponseADM get_admin_permissions_ap_projectiri_groupiri(project_iri, group_iri, knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9)

Get all administrative permissions for a project and a group.

### Example

* Basic Authentication (httpAuth1):
* Bearer Authentication (httpAuth):

```python
import openapi_client
from openapi_client.models.administrative_permission_get_response_adm import AdministrativePermissionGetResponseADM
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
    api_instance = openapi_client.AdminPermissionsApi(api_client)
    project_iri = 'http://rdfh.ch/projects/0001' # str | The IRI of a project. Must be URL-encoded.
    group_iri = 'http://rdfh.ch/groups/0042/a95UWs71KUklnFOe1rcw1w' # str | The IRI of a group. Must be URL-encoded.
    knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9 = 'knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9_example' # str |  (optional)

    try:
        api_response = api_instance.get_admin_permissions_ap_projectiri_groupiri(project_iri, group_iri, knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9)
        print("The response of AdminPermissionsApi->get_admin_permissions_ap_projectiri_groupiri:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AdminPermissionsApi->get_admin_permissions_ap_projectiri_groupiri: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **project_iri** | **str**| The IRI of a project. Must be URL-encoded. | 
 **group_iri** | **str**| The IRI of a group. Must be URL-encoded. | 
 **knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9** | **str**|  | [optional] 

### Return type

[**AdministrativePermissionGetResponseADM**](AdministrativePermissionGetResponseADM.md)

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

# **get_admin_permissions_doap_projectiri**
> DefaultObjectAccessPermissionsForProjectGetResponseADM get_admin_permissions_doap_projectiri(project_iri, knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9)

Get all default object access permissions for a project.

### Example

* Basic Authentication (httpAuth1):
* Bearer Authentication (httpAuth):

```python
import openapi_client
from openapi_client.models.default_object_access_permissions_for_project_get_response_adm import DefaultObjectAccessPermissionsForProjectGetResponseADM
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
    api_instance = openapi_client.AdminPermissionsApi(api_client)
    project_iri = 'http://rdfh.ch/projects/0001' # str | The IRI of a project. Must be URL-encoded.
    knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9 = 'knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9_example' # str |  (optional)

    try:
        api_response = api_instance.get_admin_permissions_doap_projectiri(project_iri, knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9)
        print("The response of AdminPermissionsApi->get_admin_permissions_doap_projectiri:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AdminPermissionsApi->get_admin_permissions_doap_projectiri: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **project_iri** | **str**| The IRI of a project. Must be URL-encoded. | 
 **knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9** | **str**|  | [optional] 

### Return type

[**DefaultObjectAccessPermissionsForProjectGetResponseADM**](DefaultObjectAccessPermissionsForProjectGetResponseADM.md)

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

# **get_admin_permissions_projectiri**
> PermissionsForProjectGetResponseADM get_admin_permissions_projectiri(project_iri, knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9)

Get all permissions for a project.

### Example

* Basic Authentication (httpAuth1):
* Bearer Authentication (httpAuth):

```python
import openapi_client
from openapi_client.models.permissions_for_project_get_response_adm import PermissionsForProjectGetResponseADM
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
    api_instance = openapi_client.AdminPermissionsApi(api_client)
    project_iri = 'http://rdfh.ch/projects/0001' # str | The IRI of a project. Must be URL-encoded.
    knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9 = 'knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9_example' # str |  (optional)

    try:
        api_response = api_instance.get_admin_permissions_projectiri(project_iri, knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9)
        print("The response of AdminPermissionsApi->get_admin_permissions_projectiri:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AdminPermissionsApi->get_admin_permissions_projectiri: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **project_iri** | **str**| The IRI of a project. Must be URL-encoded. | 
 **knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9** | **str**|  | [optional] 

### Return type

[**PermissionsForProjectGetResponseADM**](PermissionsForProjectGetResponseADM.md)

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

# **post_admin_permissions_ap**
> AdministrativePermissionCreateResponseADM post_admin_permissions_ap(create_administrative_permission_api_request_adm, knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9)

Create a new administrative permission

### Example

* Basic Authentication (httpAuth1):
* Bearer Authentication (httpAuth):

```python
import openapi_client
from openapi_client.models.administrative_permission_create_response_adm import AdministrativePermissionCreateResponseADM
from openapi_client.models.create_administrative_permission_api_request_adm import CreateAdministrativePermissionAPIRequestADM
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
    api_instance = openapi_client.AdminPermissionsApi(api_client)
    create_administrative_permission_api_request_adm = openapi_client.CreateAdministrativePermissionAPIRequestADM() # CreateAdministrativePermissionAPIRequestADM | 
    knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9 = 'knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9_example' # str |  (optional)

    try:
        api_response = api_instance.post_admin_permissions_ap(create_administrative_permission_api_request_adm, knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9)
        print("The response of AdminPermissionsApi->post_admin_permissions_ap:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AdminPermissionsApi->post_admin_permissions_ap: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **create_administrative_permission_api_request_adm** | [**CreateAdministrativePermissionAPIRequestADM**](CreateAdministrativePermissionAPIRequestADM.md)|  | 
 **knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9** | **str**|  | [optional] 

### Return type

[**AdministrativePermissionCreateResponseADM**](AdministrativePermissionCreateResponseADM.md)

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

# **post_admin_permissions_doap**
> DefaultObjectAccessPermissionCreateResponseADM post_admin_permissions_doap(create_default_object_access_permission_api_request_adm, knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9)

Create a new default object access permission

### Example

* Basic Authentication (httpAuth1):
* Bearer Authentication (httpAuth):

```python
import openapi_client
from openapi_client.models.create_default_object_access_permission_api_request_adm import CreateDefaultObjectAccessPermissionAPIRequestADM
from openapi_client.models.default_object_access_permission_create_response_adm import DefaultObjectAccessPermissionCreateResponseADM
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
    api_instance = openapi_client.AdminPermissionsApi(api_client)
    create_default_object_access_permission_api_request_adm = openapi_client.CreateDefaultObjectAccessPermissionAPIRequestADM() # CreateDefaultObjectAccessPermissionAPIRequestADM | 
    knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9 = 'knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9_example' # str |  (optional)

    try:
        api_response = api_instance.post_admin_permissions_doap(create_default_object_access_permission_api_request_adm, knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9)
        print("The response of AdminPermissionsApi->post_admin_permissions_doap:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AdminPermissionsApi->post_admin_permissions_doap: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **create_default_object_access_permission_api_request_adm** | [**CreateDefaultObjectAccessPermissionAPIRequestADM**](CreateDefaultObjectAccessPermissionAPIRequestADM.md)|  | 
 **knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9** | **str**|  | [optional] 

### Return type

[**DefaultObjectAccessPermissionCreateResponseADM**](DefaultObjectAccessPermissionCreateResponseADM.md)

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

# **put_admin_permissions_doap_permissioniri**
> DefaultObjectAccessPermissionGetResponseADM put_admin_permissions_doap_permissioniri(permission_iri, change_doap_request, knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9)

Update an existing default object access permission. The request may update the hasPermission and/or any allowed combination of group, resource class and property for the permission.

### Example

* Basic Authentication (httpAuth1):
* Bearer Authentication (httpAuth):

```python
import openapi_client
from openapi_client.models.change_doap_request import ChangeDoapRequest
from openapi_client.models.default_object_access_permission_get_response_adm import DefaultObjectAccessPermissionGetResponseADM
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
    api_instance = openapi_client.AdminPermissionsApi(api_client)
    permission_iri = 'http://rdfh.ch/permissions/00FF/Mck2xJDjQ_Oimi_9z4aFaA' # str | The IRI of a permission. Must be URL-encoded.
    change_doap_request = {"forGroup":"http://www.knora.org/ontology/knora-admin#ProjectMember"} # ChangeDoapRequest | Default object access permissions can be only for group, resource class, property or both resource class and property.If an invalid combination is provided, the request will fail with a Bad Request response.The iris for resource class and property must be valid Api V2 complex iris.
    knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9 = 'knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9_example' # str |  (optional)

    try:
        api_response = api_instance.put_admin_permissions_doap_permissioniri(permission_iri, change_doap_request, knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9)
        print("The response of AdminPermissionsApi->put_admin_permissions_doap_permissioniri:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AdminPermissionsApi->put_admin_permissions_doap_permissioniri: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **permission_iri** | **str**| The IRI of a permission. Must be URL-encoded. | 
 **change_doap_request** | [**ChangeDoapRequest**](ChangeDoapRequest.md)| Default object access permissions can be only for group, resource class, property or both resource class and property.If an invalid combination is provided, the request will fail with a Bad Request response.The iris for resource class and property must be valid Api V2 complex iris. | 
 **knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9** | **str**|  | [optional] 

### Return type

[**DefaultObjectAccessPermissionGetResponseADM**](DefaultObjectAccessPermissionGetResponseADM.md)

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

# **put_admin_permissions_permissioniri_group**
> PermissionGetResponseADM put_admin_permissions_permissioniri_group(permission_iri, change_permission_group_api_request_adm, knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9)

Update a permission's group

### Example

* Basic Authentication (httpAuth1):
* Bearer Authentication (httpAuth):

```python
import openapi_client
from openapi_client.models.change_permission_group_api_request_adm import ChangePermissionGroupApiRequestADM
from openapi_client.models.permission_get_response_adm import PermissionGetResponseADM
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
    api_instance = openapi_client.AdminPermissionsApi(api_client)
    permission_iri = 'http://rdfh.ch/permissions/00FF/Mck2xJDjQ_Oimi_9z4aFaA' # str | The IRI of a permission. Must be URL-encoded.
    change_permission_group_api_request_adm = openapi_client.ChangePermissionGroupApiRequestADM() # ChangePermissionGroupApiRequestADM | 
    knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9 = 'knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9_example' # str |  (optional)

    try:
        api_response = api_instance.put_admin_permissions_permissioniri_group(permission_iri, change_permission_group_api_request_adm, knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9)
        print("The response of AdminPermissionsApi->put_admin_permissions_permissioniri_group:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AdminPermissionsApi->put_admin_permissions_permissioniri_group: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **permission_iri** | **str**| The IRI of a permission. Must be URL-encoded. | 
 **change_permission_group_api_request_adm** | [**ChangePermissionGroupApiRequestADM**](ChangePermissionGroupApiRequestADM.md)|  | 
 **knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9** | **str**|  | [optional] 

### Return type

[**PermissionGetResponseADM**](PermissionGetResponseADM.md)

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

# **put_admin_permissions_permissioniri_haspermissions**
> PermissionGetResponseADM put_admin_permissions_permissioniri_haspermissions(permission_iri, change_permission_has_permissions_api_request_adm, knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9)

Update a permission's set of hasPermissions

### Example

* Basic Authentication (httpAuth1):
* Bearer Authentication (httpAuth):

```python
import openapi_client
from openapi_client.models.change_permission_has_permissions_api_request_adm import ChangePermissionHasPermissionsApiRequestADM
from openapi_client.models.permission_get_response_adm import PermissionGetResponseADM
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
    api_instance = openapi_client.AdminPermissionsApi(api_client)
    permission_iri = 'http://rdfh.ch/permissions/00FF/Mck2xJDjQ_Oimi_9z4aFaA' # str | The IRI of a permission. Must be URL-encoded.
    change_permission_has_permissions_api_request_adm = openapi_client.ChangePermissionHasPermissionsApiRequestADM() # ChangePermissionHasPermissionsApiRequestADM | 
    knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9 = 'knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9_example' # str |  (optional)

    try:
        api_response = api_instance.put_admin_permissions_permissioniri_haspermissions(permission_iri, change_permission_has_permissions_api_request_adm, knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9)
        print("The response of AdminPermissionsApi->put_admin_permissions_permissioniri_haspermissions:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AdminPermissionsApi->put_admin_permissions_permissioniri_haspermissions: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **permission_iri** | **str**| The IRI of a permission. Must be URL-encoded. | 
 **change_permission_has_permissions_api_request_adm** | [**ChangePermissionHasPermissionsApiRequestADM**](ChangePermissionHasPermissionsApiRequestADM.md)|  | 
 **knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9** | **str**|  | [optional] 

### Return type

[**PermissionGetResponseADM**](PermissionGetResponseADM.md)

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

# **put_admin_permissions_permissioniri_property**
> DefaultObjectAccessPermissionGetResponseADM put_admin_permissions_permissioniri_property(permission_iri, change_permission_property_api_request_adm, knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9)

Update a DAOP's property. Use `PUT /admin/permissions/doap/{permissionIri}` instead.

### Example

* Basic Authentication (httpAuth1):
* Bearer Authentication (httpAuth):

```python
import openapi_client
from openapi_client.models.change_permission_property_api_request_adm import ChangePermissionPropertyApiRequestADM
from openapi_client.models.default_object_access_permission_get_response_adm import DefaultObjectAccessPermissionGetResponseADM
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
    api_instance = openapi_client.AdminPermissionsApi(api_client)
    permission_iri = 'http://rdfh.ch/permissions/00FF/Mck2xJDjQ_Oimi_9z4aFaA' # str | The IRI of a permission. Must be URL-encoded.
    change_permission_property_api_request_adm = openapi_client.ChangePermissionPropertyApiRequestADM() # ChangePermissionPropertyApiRequestADM | 
    knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9 = 'knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9_example' # str |  (optional)

    try:
        api_response = api_instance.put_admin_permissions_permissioniri_property(permission_iri, change_permission_property_api_request_adm, knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9)
        print("The response of AdminPermissionsApi->put_admin_permissions_permissioniri_property:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AdminPermissionsApi->put_admin_permissions_permissioniri_property: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **permission_iri** | **str**| The IRI of a permission. Must be URL-encoded. | 
 **change_permission_property_api_request_adm** | [**ChangePermissionPropertyApiRequestADM**](ChangePermissionPropertyApiRequestADM.md)|  | 
 **knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9** | **str**|  | [optional] 

### Return type

[**DefaultObjectAccessPermissionGetResponseADM**](DefaultObjectAccessPermissionGetResponseADM.md)

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

# **put_admin_permissions_permissioniri_resourceclass**
> DefaultObjectAccessPermissionGetResponseADM put_admin_permissions_permissioniri_resourceclass(permission_iri, change_permission_resource_class_api_request_adm, knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9)

Update a DOAP's resource class. Use `PUT /admin/permissions/doap/{permissionIri}` instead.

### Example

* Basic Authentication (httpAuth1):
* Bearer Authentication (httpAuth):

```python
import openapi_client
from openapi_client.models.change_permission_resource_class_api_request_adm import ChangePermissionResourceClassApiRequestADM
from openapi_client.models.default_object_access_permission_get_response_adm import DefaultObjectAccessPermissionGetResponseADM
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
    api_instance = openapi_client.AdminPermissionsApi(api_client)
    permission_iri = 'http://rdfh.ch/permissions/00FF/Mck2xJDjQ_Oimi_9z4aFaA' # str | The IRI of a permission. Must be URL-encoded.
    change_permission_resource_class_api_request_adm = openapi_client.ChangePermissionResourceClassApiRequestADM() # ChangePermissionResourceClassApiRequestADM | 
    knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9 = 'knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9_example' # str |  (optional)

    try:
        api_response = api_instance.put_admin_permissions_permissioniri_resourceclass(permission_iri, change_permission_resource_class_api_request_adm, knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9)
        print("The response of AdminPermissionsApi->put_admin_permissions_permissioniri_resourceclass:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AdminPermissionsApi->put_admin_permissions_permissioniri_resourceclass: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **permission_iri** | **str**| The IRI of a permission. Must be URL-encoded. | 
 **change_permission_resource_class_api_request_adm** | [**ChangePermissionResourceClassApiRequestADM**](ChangePermissionResourceClassApiRequestADM.md)|  | 
 **knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9** | **str**|  | [optional] 

### Return type

[**DefaultObjectAccessPermissionGetResponseADM**](DefaultObjectAccessPermissionGetResponseADM.md)

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

