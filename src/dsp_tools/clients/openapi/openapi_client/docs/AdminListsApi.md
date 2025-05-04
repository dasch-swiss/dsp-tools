# openapi_client.AdminListsApi

All URIs are relative to *https://api.dasch.swiss:443*

Method | HTTP request | Description
------------- | ------------- | -------------
[**delete_admin_lists_comments_p1**](AdminListsApi.md#delete_admin_lists_comments_p1) | **DELETE** /admin/lists/comments/{p1} | 
[**delete_admin_lists_p1**](AdminListsApi.md#delete_admin_lists_p1) | **DELETE** /admin/lists/{p1} | 
[**get_admin_lists**](AdminListsApi.md#get_admin_lists) | **GET** /admin/lists | 
[**get_admin_lists_candelete_p1**](AdminListsApi.md#get_admin_lists_candelete_p1) | **GET** /admin/lists/candelete/{p1} | 
[**get_admin_lists_p1**](AdminListsApi.md#get_admin_lists_p1) | **GET** /admin/lists/{p1} | 
[**get_admin_lists_p1_info**](AdminListsApi.md#get_admin_lists_p1_info) | **GET** /admin/lists/{p1}/info | 
[**post_admin_lists**](AdminListsApi.md#post_admin_lists) | **POST** /admin/lists | 
[**put_admin_lists_p1**](AdminListsApi.md#put_admin_lists_p1) | **PUT** /admin/lists/{p1} | 
[**put_admin_lists_p1_comments**](AdminListsApi.md#put_admin_lists_p1_comments) | **PUT** /admin/lists/{p1}/comments | 
[**put_admin_lists_p1_labels**](AdminListsApi.md#put_admin_lists_p1_labels) | **PUT** /admin/lists/{p1}/labels | 
[**put_admin_lists_p1_name**](AdminListsApi.md#put_admin_lists_p1_name) | **PUT** /admin/lists/{p1}/name | 
[**put_admin_lists_p1_position**](AdminListsApi.md#put_admin_lists_p1_position) | **PUT** /admin/lists/{p1}/position | 


# **delete_admin_lists_comments_p1**
> ListNodeCommentsDeleteResponseADM delete_admin_lists_comments_p1(p1, knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9)

### Example

* Basic Authentication (httpAuth1):
* Bearer Authentication (httpAuth):

```python
import openapi_client
from openapi_client.models.list_node_comments_delete_response_adm import ListNodeCommentsDeleteResponseADM
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
    api_instance = openapi_client.AdminListsApi(api_client)
    p1 = 'p1_example' # str | The IRI of the list.
    knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9 = 'knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9_example' # str |  (optional)

    try:
        api_response = api_instance.delete_admin_lists_comments_p1(p1, knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9)
        print("The response of AdminListsApi->delete_admin_lists_comments_p1:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AdminListsApi->delete_admin_lists_comments_p1: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **p1** | **str**| The IRI of the list. | 
 **knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9** | **str**|  | [optional] 

### Return type

[**ListNodeCommentsDeleteResponseADM**](ListNodeCommentsDeleteResponseADM.md)

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

# **delete_admin_lists_p1**
> ListItemDeleteResponseADM delete_admin_lists_p1(p1, knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9)

### Example

* Basic Authentication (httpAuth1):
* Bearer Authentication (httpAuth):

```python
import openapi_client
from openapi_client.models.list_item_delete_response_adm import ListItemDeleteResponseADM
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
    api_instance = openapi_client.AdminListsApi(api_client)
    p1 = 'p1_example' # str | The IRI of the list.
    knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9 = 'knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9_example' # str |  (optional)

    try:
        api_response = api_instance.delete_admin_lists_p1(p1, knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9)
        print("The response of AdminListsApi->delete_admin_lists_p1:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AdminListsApi->delete_admin_lists_p1: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **p1** | **str**| The IRI of the list. | 
 **knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9** | **str**|  | [optional] 

### Return type

[**ListItemDeleteResponseADM**](ListItemDeleteResponseADM.md)

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

# **get_admin_lists**
> ListsGetResponseADM get_admin_lists(project_iri=project_iri, project_shortcode=project_shortcode)

Get all lists or all lists belonging to a project. Note that you can provide either a project IRI or a project shortcode.

### Example


```python
import openapi_client
from openapi_client.models.lists_get_response_adm import ListsGetResponseADM
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
    api_instance = openapi_client.AdminListsApi(api_client)
    project_iri = 'http://rdfh.ch/projects/0042' # str | The (optional) IRI of the project. (optional)
    project_shortcode = '0042' # str | The (optional) shortcode of the project. (optional)

    try:
        api_response = api_instance.get_admin_lists(project_iri=project_iri, project_shortcode=project_shortcode)
        print("The response of AdminListsApi->get_admin_lists:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AdminListsApi->get_admin_lists: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **project_iri** | **str**| The (optional) IRI of the project. | [optional] 
 **project_shortcode** | **str**| The (optional) shortcode of the project. | [optional] 

### Return type

[**ListsGetResponseADM**](ListsGetResponseADM.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Contains the list of all root nodes of each found list. |  -  |
**400** |  |  -  |
**401** |  |  -  |
**403** |  |  -  |
**404** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_admin_lists_candelete_p1**
> CanDeleteListResponseADM get_admin_lists_candelete_p1(p1)

Checks if a list can be deleted (none of its nodes is used in data).

### Example


```python
import openapi_client
from openapi_client.models.can_delete_list_response_adm import CanDeleteListResponseADM
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
    api_instance = openapi_client.AdminListsApi(api_client)
    p1 = 'p1_example' # str | The IRI of the list.

    try:
        api_response = api_instance.get_admin_lists_candelete_p1(p1)
        print("The response of AdminListsApi->get_admin_lists_candelete_p1:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AdminListsApi->get_admin_lists_candelete_p1: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **p1** | **str**| The IRI of the list. | 

### Return type

[**CanDeleteListResponseADM**](CanDeleteListResponseADM.md)

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

# **get_admin_lists_p1**
> ListItemGetResponseADM get_admin_lists_p1(p1)

Returns a list node, root or child, with children (if exist).

### Example


```python
import openapi_client
from openapi_client.models.list_item_get_response_adm import ListItemGetResponseADM
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
    api_instance = openapi_client.AdminListsApi(api_client)
    p1 = 'p1_example' # str | The IRI of the list.

    try:
        api_response = api_instance.get_admin_lists_p1(p1)
        print("The response of AdminListsApi->get_admin_lists_p1:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AdminListsApi->get_admin_lists_p1: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **p1** | **str**| The IRI of the list. | 

### Return type

[**ListItemGetResponseADM**](ListItemGetResponseADM.md)

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

# **get_admin_lists_p1_info**
> NodeInfoGetResponseADM get_admin_lists_p1_info(p1)

Returns basic information about a list node, root or child, w/o children (if exist).

### Example


```python
import openapi_client
from openapi_client.models.node_info_get_response_adm import NodeInfoGetResponseADM
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
    api_instance = openapi_client.AdminListsApi(api_client)
    p1 = 'p1_example' # str | The IRI of the list.

    try:
        api_response = api_instance.get_admin_lists_p1_info(p1)
        print("The response of AdminListsApi->get_admin_lists_p1_info:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AdminListsApi->get_admin_lists_p1_info: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **p1** | **str**| The IRI of the list. | 

### Return type

[**NodeInfoGetResponseADM**](NodeInfoGetResponseADM.md)

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

# **post_admin_lists**
> ListGetResponseADM post_admin_lists(list_create_root_node_request, knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9)

### Example

* Basic Authentication (httpAuth1):
* Bearer Authentication (httpAuth):

```python
import openapi_client
from openapi_client.models.list_create_root_node_request import ListCreateRootNodeRequest
from openapi_client.models.list_get_response_adm import ListGetResponseADM
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
    api_instance = openapi_client.AdminListsApi(api_client)
    list_create_root_node_request = openapi_client.ListCreateRootNodeRequest() # ListCreateRootNodeRequest | 
    knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9 = 'knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9_example' # str |  (optional)

    try:
        api_response = api_instance.post_admin_lists(list_create_root_node_request, knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9)
        print("The response of AdminListsApi->post_admin_lists:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AdminListsApi->post_admin_lists: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **list_create_root_node_request** | [**ListCreateRootNodeRequest**](ListCreateRootNodeRequest.md)|  | 
 **knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9** | **str**|  | [optional] 

### Return type

[**ListGetResponseADM**](ListGetResponseADM.md)

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

# **put_admin_lists_p1**
> NodeInfoGetResponseADM put_admin_lists_p1(p1, list_change_request, knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9)

### Example

* Basic Authentication (httpAuth1):
* Bearer Authentication (httpAuth):

```python
import openapi_client
from openapi_client.models.list_change_request import ListChangeRequest
from openapi_client.models.node_info_get_response_adm import NodeInfoGetResponseADM
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
    api_instance = openapi_client.AdminListsApi(api_client)
    p1 = 'p1_example' # str | The IRI of the list.
    list_change_request = openapi_client.ListChangeRequest() # ListChangeRequest | 
    knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9 = 'knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9_example' # str |  (optional)

    try:
        api_response = api_instance.put_admin_lists_p1(p1, list_change_request, knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9)
        print("The response of AdminListsApi->put_admin_lists_p1:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AdminListsApi->put_admin_lists_p1: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **p1** | **str**| The IRI of the list. | 
 **list_change_request** | [**ListChangeRequest**](ListChangeRequest.md)|  | 
 **knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9** | **str**|  | [optional] 

### Return type

[**NodeInfoGetResponseADM**](NodeInfoGetResponseADM.md)

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

# **put_admin_lists_p1_comments**
> NodeInfoGetResponseADM put_admin_lists_p1_comments(p1, list_change_comments_request, knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9)

### Example

* Basic Authentication (httpAuth1):
* Bearer Authentication (httpAuth):

```python
import openapi_client
from openapi_client.models.list_change_comments_request import ListChangeCommentsRequest
from openapi_client.models.node_info_get_response_adm import NodeInfoGetResponseADM
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
    api_instance = openapi_client.AdminListsApi(api_client)
    p1 = 'p1_example' # str | The IRI of the list.
    list_change_comments_request = openapi_client.ListChangeCommentsRequest() # ListChangeCommentsRequest | 
    knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9 = 'knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9_example' # str |  (optional)

    try:
        api_response = api_instance.put_admin_lists_p1_comments(p1, list_change_comments_request, knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9)
        print("The response of AdminListsApi->put_admin_lists_p1_comments:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AdminListsApi->put_admin_lists_p1_comments: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **p1** | **str**| The IRI of the list. | 
 **list_change_comments_request** | [**ListChangeCommentsRequest**](ListChangeCommentsRequest.md)|  | 
 **knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9** | **str**|  | [optional] 

### Return type

[**NodeInfoGetResponseADM**](NodeInfoGetResponseADM.md)

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

# **put_admin_lists_p1_labels**
> NodeInfoGetResponseADM put_admin_lists_p1_labels(p1, list_change_labels_request, knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9)

### Example

* Basic Authentication (httpAuth1):
* Bearer Authentication (httpAuth):

```python
import openapi_client
from openapi_client.models.list_change_labels_request import ListChangeLabelsRequest
from openapi_client.models.node_info_get_response_adm import NodeInfoGetResponseADM
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
    api_instance = openapi_client.AdminListsApi(api_client)
    p1 = 'p1_example' # str | The IRI of the list.
    list_change_labels_request = openapi_client.ListChangeLabelsRequest() # ListChangeLabelsRequest | 
    knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9 = 'knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9_example' # str |  (optional)

    try:
        api_response = api_instance.put_admin_lists_p1_labels(p1, list_change_labels_request, knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9)
        print("The response of AdminListsApi->put_admin_lists_p1_labels:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AdminListsApi->put_admin_lists_p1_labels: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **p1** | **str**| The IRI of the list. | 
 **list_change_labels_request** | [**ListChangeLabelsRequest**](ListChangeLabelsRequest.md)|  | 
 **knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9** | **str**|  | [optional] 

### Return type

[**NodeInfoGetResponseADM**](NodeInfoGetResponseADM.md)

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

# **put_admin_lists_p1_name**
> NodeInfoGetResponseADM put_admin_lists_p1_name(p1, list_change_name_request, knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9)

### Example

* Basic Authentication (httpAuth1):
* Bearer Authentication (httpAuth):

```python
import openapi_client
from openapi_client.models.list_change_name_request import ListChangeNameRequest
from openapi_client.models.node_info_get_response_adm import NodeInfoGetResponseADM
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
    api_instance = openapi_client.AdminListsApi(api_client)
    p1 = 'p1_example' # str | The IRI of the list.
    list_change_name_request = openapi_client.ListChangeNameRequest() # ListChangeNameRequest | 
    knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9 = 'knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9_example' # str |  (optional)

    try:
        api_response = api_instance.put_admin_lists_p1_name(p1, list_change_name_request, knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9)
        print("The response of AdminListsApi->put_admin_lists_p1_name:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AdminListsApi->put_admin_lists_p1_name: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **p1** | **str**| The IRI of the list. | 
 **list_change_name_request** | [**ListChangeNameRequest**](ListChangeNameRequest.md)|  | 
 **knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9** | **str**|  | [optional] 

### Return type

[**NodeInfoGetResponseADM**](NodeInfoGetResponseADM.md)

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

# **put_admin_lists_p1_position**
> NodePositionChangeResponseADM put_admin_lists_p1_position(p1, list_change_position_request, knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9)

### Example

* Basic Authentication (httpAuth1):
* Bearer Authentication (httpAuth):

```python
import openapi_client
from openapi_client.models.list_change_position_request import ListChangePositionRequest
from openapi_client.models.node_position_change_response_adm import NodePositionChangeResponseADM
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
    api_instance = openapi_client.AdminListsApi(api_client)
    p1 = 'p1_example' # str | The IRI of the list.
    list_change_position_request = openapi_client.ListChangePositionRequest() # ListChangePositionRequest | 
    knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9 = 'knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9_example' # str |  (optional)

    try:
        api_response = api_instance.put_admin_lists_p1_position(p1, list_change_position_request, knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9)
        print("The response of AdminListsApi->put_admin_lists_p1_position:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AdminListsApi->put_admin_lists_p1_position: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **p1** | **str**| The IRI of the list. | 
 **list_change_position_request** | [**ListChangePositionRequest**](ListChangePositionRequest.md)|  | 
 **knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9** | **str**|  | [optional] 

### Return type

[**NodePositionChangeResponseADM**](NodePositionChangeResponseADM.md)

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

