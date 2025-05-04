# openapi_client.AdminGroupsApi

All URIs are relative to *https://api.dasch.swiss:443*

Method | HTTP request | Description
------------- | ------------- | -------------
[**create_new_group**](AdminGroupsApi.md#create_new_group) | **POST** /admin/groups | 
[**delete_admin_groups_groupiri**](AdminGroupsApi.md#delete_admin_groups_groupiri) | **DELETE** /admin/groups/{groupIri} | 
[**get_admin_groups**](AdminGroupsApi.md#get_admin_groups) | **GET** /admin/groups | 
[**get_admin_groups_groupiri**](AdminGroupsApi.md#get_admin_groups_groupiri) | **GET** /admin/groups/{groupIri} | 
[**get_admin_groups_groupiri_members**](AdminGroupsApi.md#get_admin_groups_groupiri_members) | **GET** /admin/groups/{groupIri}/members | 
[**put_admin_groups_groupiri**](AdminGroupsApi.md#put_admin_groups_groupiri) | **PUT** /admin/groups/{groupIri} | 
[**put_admin_groups_groupiri_status**](AdminGroupsApi.md#put_admin_groups_groupiri_status) | **PUT** /admin/groups/{groupIri}/status | 


# **create_new_group**
> GroupGetResponseADM create_new_group(group_create_request, knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9)

**Required permissions**: User must SystemAdmin or ProjectAdmin of the project the group is created in.

### Example

* Basic Authentication (httpAuth1):
* Bearer Authentication (httpAuth):

```python
import openapi_client
from openapi_client.models.group_create_request import GroupCreateRequest
from openapi_client.models.group_get_response_adm import GroupGetResponseADM
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
    api_instance = openapi_client.AdminGroupsApi(api_client)
    group_create_request = {"name":"NewGroup","descriptions":[{"value":"NewGroup description in English","language":"en"},{"value":"NewGroup Beschreibung auf Deutsch","language":"de"}],"project":"http://rdfh.ch/projects/0042","status":true,"selfjoin":false} # GroupCreateRequest | 
    knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9 = 'knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9_example' # str |  (optional)

    try:
        api_response = api_instance.create_new_group(group_create_request, knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9)
        print("The response of AdminGroupsApi->create_new_group:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AdminGroupsApi->create_new_group: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **group_create_request** | [**GroupCreateRequest**](GroupCreateRequest.md)|  | 
 **knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9** | **str**|  | [optional] 

### Return type

[**GroupGetResponseADM**](GroupGetResponseADM.md)

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

# **delete_admin_groups_groupiri**
> GroupGetResponseADM delete_admin_groups_groupiri(group_iri, knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9)

Deletes a group by changing its status to 'false'.

### Example

* Basic Authentication (httpAuth1):
* Bearer Authentication (httpAuth):

```python
import openapi_client
from openapi_client.models.group_get_response_adm import GroupGetResponseADM
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
    api_instance = openapi_client.AdminGroupsApi(api_client)
    group_iri = 'http://rdfh.ch/groups/0042/a95UWs71KUklnFOe1rcw1w' # str | The IRI of a group. Must be URL-encoded.
    knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9 = 'knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9_example' # str |  (optional)

    try:
        api_response = api_instance.delete_admin_groups_groupiri(group_iri, knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9)
        print("The response of AdminGroupsApi->delete_admin_groups_groupiri:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AdminGroupsApi->delete_admin_groups_groupiri: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **group_iri** | **str**| The IRI of a group. Must be URL-encoded. | 
 **knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9** | **str**|  | [optional] 

### Return type

[**GroupGetResponseADM**](GroupGetResponseADM.md)

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

# **get_admin_groups**
> GroupsGetResponseADM get_admin_groups()

Return all groups.

### Example


```python
import openapi_client
from openapi_client.models.groups_get_response_adm import GroupsGetResponseADM
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
    api_instance = openapi_client.AdminGroupsApi(api_client)

    try:
        api_response = api_instance.get_admin_groups()
        print("The response of AdminGroupsApi->get_admin_groups:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AdminGroupsApi->get_admin_groups: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

[**GroupsGetResponseADM**](GroupsGetResponseADM.md)

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

# **get_admin_groups_groupiri**
> GroupGetResponseADM get_admin_groups_groupiri(group_iri)

Return a single group identified by its IRI.

### Example


```python
import openapi_client
from openapi_client.models.group_get_response_adm import GroupGetResponseADM
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
    api_instance = openapi_client.AdminGroupsApi(api_client)
    group_iri = 'http://rdfh.ch/groups/0042/a95UWs71KUklnFOe1rcw1w' # str | The IRI of a group. Must be URL-encoded.

    try:
        api_response = api_instance.get_admin_groups_groupiri(group_iri)
        print("The response of AdminGroupsApi->get_admin_groups_groupiri:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AdminGroupsApi->get_admin_groups_groupiri: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **group_iri** | **str**| The IRI of a group. Must be URL-encoded. | 

### Return type

[**GroupGetResponseADM**](GroupGetResponseADM.md)

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

# **get_admin_groups_groupiri_members**
> GroupMembersGetResponseADM get_admin_groups_groupiri_members(group_iri, knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9)

Return all members of a single group.

### Example

* Basic Authentication (httpAuth1):
* Bearer Authentication (httpAuth):

```python
import openapi_client
from openapi_client.models.group_members_get_response_adm import GroupMembersGetResponseADM
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
    api_instance = openapi_client.AdminGroupsApi(api_client)
    group_iri = 'http://rdfh.ch/groups/0042/a95UWs71KUklnFOe1rcw1w' # str | The IRI of a group. Must be URL-encoded.
    knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9 = 'knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9_example' # str |  (optional)

    try:
        api_response = api_instance.get_admin_groups_groupiri_members(group_iri, knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9)
        print("The response of AdminGroupsApi->get_admin_groups_groupiri_members:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AdminGroupsApi->get_admin_groups_groupiri_members: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **group_iri** | **str**| The IRI of a group. Must be URL-encoded. | 
 **knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9** | **str**|  | [optional] 

### Return type

[**GroupMembersGetResponseADM**](GroupMembersGetResponseADM.md)

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

# **put_admin_groups_groupiri**
> GroupGetResponseADM put_admin_groups_groupiri(group_iri, group_update_request, knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9)

Update a group's basic information.

### Example

* Basic Authentication (httpAuth1):
* Bearer Authentication (httpAuth):

```python
import openapi_client
from openapi_client.models.group_get_response_adm import GroupGetResponseADM
from openapi_client.models.group_update_request import GroupUpdateRequest
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
    api_instance = openapi_client.AdminGroupsApi(api_client)
    group_iri = 'http://rdfh.ch/groups/0042/a95UWs71KUklnFOe1rcw1w' # str | The IRI of a group. Must be URL-encoded.
    group_update_request = {"name":"NewGroupNewName","descriptions":[{"value":"NewGroupNewName description in English","language":"en"},{"value":"NewGroupNewName Beschreibung auf Deutsch","language":"de"}],"status":false,"selfjoin":true} # GroupUpdateRequest | 
    knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9 = 'knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9_example' # str |  (optional)

    try:
        api_response = api_instance.put_admin_groups_groupiri(group_iri, group_update_request, knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9)
        print("The response of AdminGroupsApi->put_admin_groups_groupiri:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AdminGroupsApi->put_admin_groups_groupiri: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **group_iri** | **str**| The IRI of a group. Must be URL-encoded. | 
 **group_update_request** | [**GroupUpdateRequest**](GroupUpdateRequest.md)|  | 
 **knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9** | **str**|  | [optional] 

### Return type

[**GroupGetResponseADM**](GroupGetResponseADM.md)

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

# **put_admin_groups_groupiri_status**
> GroupGetResponseADM put_admin_groups_groupiri_status(group_iri, group_status_update_request, knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9)

Updates a group's status.

### Example

* Basic Authentication (httpAuth1):
* Bearer Authentication (httpAuth):

```python
import openapi_client
from openapi_client.models.group_get_response_adm import GroupGetResponseADM
from openapi_client.models.group_status_update_request import GroupStatusUpdateRequest
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
    api_instance = openapi_client.AdminGroupsApi(api_client)
    group_iri = 'http://rdfh.ch/groups/0042/a95UWs71KUklnFOe1rcw1w' # str | The IRI of a group. Must be URL-encoded.
    group_status_update_request = openapi_client.GroupStatusUpdateRequest() # GroupStatusUpdateRequest | 
    knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9 = 'knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9_example' # str |  (optional)

    try:
        api_response = api_instance.put_admin_groups_groupiri_status(group_iri, group_status_update_request, knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9)
        print("The response of AdminGroupsApi->put_admin_groups_groupiri_status:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AdminGroupsApi->put_admin_groups_groupiri_status: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **group_iri** | **str**| The IRI of a group. Must be URL-encoded. | 
 **group_status_update_request** | [**GroupStatusUpdateRequest**](GroupStatusUpdateRequest.md)|  | 
 **knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9** | **str**|  | [optional] 

### Return type

[**GroupGetResponseADM**](GroupGetResponseADM.md)

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

