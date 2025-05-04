# openapi_client.V2SearchApi

All URIs are relative to *https://api.dasch.swiss:443*

Method | HTTP request | Description
------------- | ------------- | -------------
[**get_v2_search_count_searchterm**](V2SearchApi.md#get_v2_search_count_searchterm) | **GET** /v2/search/count/{searchTerm} | 
[**get_v2_search_searchterm**](V2SearchApi.md#get_v2_search_searchterm) | **GET** /v2/search/{searchTerm} | 
[**get_v2_searchbylabel_count_searchterm**](V2SearchApi.md#get_v2_searchbylabel_count_searchterm) | **GET** /v2/searchbylabel/count/{searchTerm} | 
[**get_v2_searchbylabel_searchterm**](V2SearchApi.md#get_v2_searchbylabel_searchterm) | **GET** /v2/searchbylabel/{searchTerm} | 
[**get_v2_searchextended_count_p1**](V2SearchApi.md#get_v2_searchextended_count_p1) | **GET** /v2/searchextended/count/{p1} | 
[**get_v2_searchextended_p1**](V2SearchApi.md#get_v2_searchextended_p1) | **GET** /v2/searchextended/{p1} | 
[**get_v2_searchincominglinks_resourceiri**](V2SearchApi.md#get_v2_searchincominglinks_resourceiri) | **GET** /v2/searchIncomingLinks/{resourceIri} | 
[**get_v2_searchincomingregions_resourceiri**](V2SearchApi.md#get_v2_searchincomingregions_resourceiri) | **GET** /v2/searchIncomingRegions/{resourceIri} | 
[**post_v2_searchextended**](V2SearchApi.md#post_v2_searchextended) | **POST** /v2/searchextended | 
[**post_v2_searchextended_count**](V2SearchApi.md#post_v2_searchextended_count) | **POST** /v2/searchextended/count | 


# **get_v2_search_count_searchterm**
> str get_v2_search_count_searchterm(search_term, knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9, x_knora_accept_schema=x_knora_accept_schema, var_schema=var_schema, x_knora_json_ld_rendering=x_knora_json_ld_rendering, markup=markup, x_knora_accept_markup=x_knora_accept_markup, limit_to_project=limit_to_project, limit_to_resource_class=limit_to_resource_class, limit_to_standoff_class=limit_to_standoff_class)

Search for resources by label.

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
    api_instance = openapi_client.V2SearchApi(api_client)
    search_term = 'search_term_example' # str | 
    knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9 = 'knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9_example' # str |  (optional)
    x_knora_accept_schema = 'x_knora_accept_schema_example' # str | The ontology schema to be used for the request. If not specified, the default schema ApiV2Complex will be used. (optional)
    var_schema = 'var_schema_example' # str | The ontology schema to be used for the request. If not specified, the default schema ApiV2Complex will be used. (optional)
    x_knora_json_ld_rendering = 'x_knora_json_ld_rendering_example' # str | The JSON-LD rendering to be used for the request (flat or hierarchical). If not specified, hierarchical JSON-LD will be used. (optional)
    markup = 'markup_example' # str | The markup rendering to be used for the request (XML or standoff). (optional)
    x_knora_accept_markup = 'x_knora_accept_markup_example' # str | The markup rendering to be used for the request (XML or standoff). (optional)
    limit_to_project = 'limit_to_project_example' # str | The project to limit the search to. (optional)
    limit_to_resource_class = 'limit_to_resource_class_example' # str | The resource class to limit the search to. (optional)
    limit_to_standoff_class = 'limit_to_standoff_class_example' # str | The standoff class to limit the search to. (optional)

    try:
        api_response = api_instance.get_v2_search_count_searchterm(search_term, knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9, x_knora_accept_schema=x_knora_accept_schema, var_schema=var_schema, x_knora_json_ld_rendering=x_knora_json_ld_rendering, markup=markup, x_knora_accept_markup=x_knora_accept_markup, limit_to_project=limit_to_project, limit_to_resource_class=limit_to_resource_class, limit_to_standoff_class=limit_to_standoff_class)
        print("The response of V2SearchApi->get_v2_search_count_searchterm:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling V2SearchApi->get_v2_search_count_searchterm: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **search_term** | **str**|  | 
 **knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9** | **str**|  | [optional] 
 **x_knora_accept_schema** | **str**| The ontology schema to be used for the request. If not specified, the default schema ApiV2Complex will be used. | [optional] 
 **var_schema** | **str**| The ontology schema to be used for the request. If not specified, the default schema ApiV2Complex will be used. | [optional] 
 **x_knora_json_ld_rendering** | **str**| The JSON-LD rendering to be used for the request (flat or hierarchical). If not specified, hierarchical JSON-LD will be used. | [optional] 
 **markup** | **str**| The markup rendering to be used for the request (XML or standoff). | [optional] 
 **x_knora_accept_markup** | **str**| The markup rendering to be used for the request (XML or standoff). | [optional] 
 **limit_to_project** | **str**| The project to limit the search to. | [optional] 
 **limit_to_resource_class** | **str**| The resource class to limit the search to. | [optional] 
 **limit_to_standoff_class** | **str**| The standoff class to limit the search to. | [optional] 

### Return type

**str**

### Authorization

[httpAuth1](../README.md#httpAuth1), [httpAuth](../README.md#httpAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: text/plain, application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** |  |  * Content-Type -  <br>  |
**400** |  |  -  |
**401** |  |  -  |
**403** |  |  -  |
**404** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_v2_search_searchterm**
> str get_v2_search_searchterm(search_term, knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9, x_knora_accept_schema=x_knora_accept_schema, var_schema=var_schema, x_knora_json_ld_rendering=x_knora_json_ld_rendering, markup=markup, x_knora_accept_markup=x_knora_accept_markup, offset=offset, limit_to_project=limit_to_project, limit_to_resource_class=limit_to_resource_class, limit_to_standoff_class=limit_to_standoff_class, return_files=return_files)

Search for resources by label.

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
    api_instance = openapi_client.V2SearchApi(api_client)
    search_term = 'search_term_example' # str | 
    knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9 = 'knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9_example' # str |  (optional)
    x_knora_accept_schema = 'x_knora_accept_schema_example' # str | The ontology schema to be used for the request. If not specified, the default schema ApiV2Complex will be used. (optional)
    var_schema = 'var_schema_example' # str | The ontology schema to be used for the request. If not specified, the default schema ApiV2Complex will be used. (optional)
    x_knora_json_ld_rendering = 'x_knora_json_ld_rendering_example' # str | The JSON-LD rendering to be used for the request (flat or hierarchical). If not specified, hierarchical JSON-LD will be used. (optional)
    markup = 'markup_example' # str | The markup rendering to be used for the request (XML or standoff). (optional)
    x_knora_accept_markup = 'x_knora_accept_markup_example' # str | The markup rendering to be used for the request (XML or standoff). (optional)
    offset = 0 # int | The offset to be used for paging. (optional) (default to 0)
    limit_to_project = 'limit_to_project_example' # str | The project to limit the search to. (optional)
    limit_to_resource_class = 'limit_to_resource_class_example' # str | The resource class to limit the search to. (optional)
    limit_to_standoff_class = 'limit_to_standoff_class_example' # str | The standoff class to limit the search to. (optional)
    return_files = False # bool | Whether to return files in the search results. (optional) (default to False)

    try:
        api_response = api_instance.get_v2_search_searchterm(search_term, knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9, x_knora_accept_schema=x_knora_accept_schema, var_schema=var_schema, x_knora_json_ld_rendering=x_knora_json_ld_rendering, markup=markup, x_knora_accept_markup=x_knora_accept_markup, offset=offset, limit_to_project=limit_to_project, limit_to_resource_class=limit_to_resource_class, limit_to_standoff_class=limit_to_standoff_class, return_files=return_files)
        print("The response of V2SearchApi->get_v2_search_searchterm:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling V2SearchApi->get_v2_search_searchterm: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **search_term** | **str**|  | 
 **knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9** | **str**|  | [optional] 
 **x_knora_accept_schema** | **str**| The ontology schema to be used for the request. If not specified, the default schema ApiV2Complex will be used. | [optional] 
 **var_schema** | **str**| The ontology schema to be used for the request. If not specified, the default schema ApiV2Complex will be used. | [optional] 
 **x_knora_json_ld_rendering** | **str**| The JSON-LD rendering to be used for the request (flat or hierarchical). If not specified, hierarchical JSON-LD will be used. | [optional] 
 **markup** | **str**| The markup rendering to be used for the request (XML or standoff). | [optional] 
 **x_knora_accept_markup** | **str**| The markup rendering to be used for the request (XML or standoff). | [optional] 
 **offset** | **int**| The offset to be used for paging. | [optional] [default to 0]
 **limit_to_project** | **str**| The project to limit the search to. | [optional] 
 **limit_to_resource_class** | **str**| The resource class to limit the search to. | [optional] 
 **limit_to_standoff_class** | **str**| The standoff class to limit the search to. | [optional] 
 **return_files** | **bool**| Whether to return files in the search results. | [optional] [default to False]

### Return type

**str**

### Authorization

[httpAuth1](../README.md#httpAuth1), [httpAuth](../README.md#httpAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: text/plain, application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** |  |  * Content-Type -  <br>  |
**400** |  |  -  |
**401** |  |  -  |
**403** |  |  -  |
**404** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_v2_searchbylabel_count_searchterm**
> str get_v2_searchbylabel_count_searchterm(search_term, knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9, x_knora_accept_schema=x_knora_accept_schema, var_schema=var_schema, x_knora_json_ld_rendering=x_knora_json_ld_rendering, markup=markup, x_knora_accept_markup=x_knora_accept_markup, limit_to_project=limit_to_project, limit_to_resource_class=limit_to_resource_class)

Search for resources by label.

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
    api_instance = openapi_client.V2SearchApi(api_client)
    search_term = 'search_term_example' # str | 
    knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9 = 'knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9_example' # str |  (optional)
    x_knora_accept_schema = 'x_knora_accept_schema_example' # str | The ontology schema to be used for the request. If not specified, the default schema ApiV2Complex will be used. (optional)
    var_schema = 'var_schema_example' # str | The ontology schema to be used for the request. If not specified, the default schema ApiV2Complex will be used. (optional)
    x_knora_json_ld_rendering = 'x_knora_json_ld_rendering_example' # str | The JSON-LD rendering to be used for the request (flat or hierarchical). If not specified, hierarchical JSON-LD will be used. (optional)
    markup = 'markup_example' # str | The markup rendering to be used for the request (XML or standoff). (optional)
    x_knora_accept_markup = 'x_knora_accept_markup_example' # str | The markup rendering to be used for the request (XML or standoff). (optional)
    limit_to_project = 'limit_to_project_example' # str | The project to limit the search to. (optional)
    limit_to_resource_class = 'limit_to_resource_class_example' # str | The resource class to limit the search to. (optional)

    try:
        api_response = api_instance.get_v2_searchbylabel_count_searchterm(search_term, knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9, x_knora_accept_schema=x_knora_accept_schema, var_schema=var_schema, x_knora_json_ld_rendering=x_knora_json_ld_rendering, markup=markup, x_knora_accept_markup=x_knora_accept_markup, limit_to_project=limit_to_project, limit_to_resource_class=limit_to_resource_class)
        print("The response of V2SearchApi->get_v2_searchbylabel_count_searchterm:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling V2SearchApi->get_v2_searchbylabel_count_searchterm: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **search_term** | **str**|  | 
 **knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9** | **str**|  | [optional] 
 **x_knora_accept_schema** | **str**| The ontology schema to be used for the request. If not specified, the default schema ApiV2Complex will be used. | [optional] 
 **var_schema** | **str**| The ontology schema to be used for the request. If not specified, the default schema ApiV2Complex will be used. | [optional] 
 **x_knora_json_ld_rendering** | **str**| The JSON-LD rendering to be used for the request (flat or hierarchical). If not specified, hierarchical JSON-LD will be used. | [optional] 
 **markup** | **str**| The markup rendering to be used for the request (XML or standoff). | [optional] 
 **x_knora_accept_markup** | **str**| The markup rendering to be used for the request (XML or standoff). | [optional] 
 **limit_to_project** | **str**| The project to limit the search to. | [optional] 
 **limit_to_resource_class** | **str**| The resource class to limit the search to. | [optional] 

### Return type

**str**

### Authorization

[httpAuth1](../README.md#httpAuth1), [httpAuth](../README.md#httpAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: text/plain, application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** |  |  * Content-Type -  <br>  |
**400** |  |  -  |
**401** |  |  -  |
**403** |  |  -  |
**404** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_v2_searchbylabel_searchterm**
> str get_v2_searchbylabel_searchterm(search_term, knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9, x_knora_accept_schema=x_knora_accept_schema, var_schema=var_schema, x_knora_json_ld_rendering=x_knora_json_ld_rendering, markup=markup, x_knora_accept_markup=x_knora_accept_markup, offset=offset, limit_to_project=limit_to_project, limit_to_resource_class=limit_to_resource_class)

Search for resources by label.

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
    api_instance = openapi_client.V2SearchApi(api_client)
    search_term = 'search_term_example' # str | 
    knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9 = 'knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9_example' # str |  (optional)
    x_knora_accept_schema = 'x_knora_accept_schema_example' # str | The ontology schema to be used for the request. If not specified, the default schema ApiV2Complex will be used. (optional)
    var_schema = 'var_schema_example' # str | The ontology schema to be used for the request. If not specified, the default schema ApiV2Complex will be used. (optional)
    x_knora_json_ld_rendering = 'x_knora_json_ld_rendering_example' # str | The JSON-LD rendering to be used for the request (flat or hierarchical). If not specified, hierarchical JSON-LD will be used. (optional)
    markup = 'markup_example' # str | The markup rendering to be used for the request (XML or standoff). (optional)
    x_knora_accept_markup = 'x_knora_accept_markup_example' # str | The markup rendering to be used for the request (XML or standoff). (optional)
    offset = 0 # int | The offset to be used for paging. (optional) (default to 0)
    limit_to_project = 'limit_to_project_example' # str | The project to limit the search to. (optional)
    limit_to_resource_class = 'limit_to_resource_class_example' # str | The resource class to limit the search to. (optional)

    try:
        api_response = api_instance.get_v2_searchbylabel_searchterm(search_term, knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9, x_knora_accept_schema=x_knora_accept_schema, var_schema=var_schema, x_knora_json_ld_rendering=x_knora_json_ld_rendering, markup=markup, x_knora_accept_markup=x_knora_accept_markup, offset=offset, limit_to_project=limit_to_project, limit_to_resource_class=limit_to_resource_class)
        print("The response of V2SearchApi->get_v2_searchbylabel_searchterm:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling V2SearchApi->get_v2_searchbylabel_searchterm: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **search_term** | **str**|  | 
 **knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9** | **str**|  | [optional] 
 **x_knora_accept_schema** | **str**| The ontology schema to be used for the request. If not specified, the default schema ApiV2Complex will be used. | [optional] 
 **var_schema** | **str**| The ontology schema to be used for the request. If not specified, the default schema ApiV2Complex will be used. | [optional] 
 **x_knora_json_ld_rendering** | **str**| The JSON-LD rendering to be used for the request (flat or hierarchical). If not specified, hierarchical JSON-LD will be used. | [optional] 
 **markup** | **str**| The markup rendering to be used for the request (XML or standoff). | [optional] 
 **x_knora_accept_markup** | **str**| The markup rendering to be used for the request (XML or standoff). | [optional] 
 **offset** | **int**| The offset to be used for paging. | [optional] [default to 0]
 **limit_to_project** | **str**| The project to limit the search to. | [optional] 
 **limit_to_resource_class** | **str**| The resource class to limit the search to. | [optional] 

### Return type

**str**

### Authorization

[httpAuth1](../README.md#httpAuth1), [httpAuth](../README.md#httpAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: text/plain, application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** |  |  * Content-Type -  <br>  |
**400** |  |  -  |
**401** |  |  -  |
**403** |  |  -  |
**404** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_v2_searchextended_count_p1**
> str get_v2_searchextended_count_p1(p1, knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9, x_knora_accept_schema=x_knora_accept_schema, var_schema=var_schema, x_knora_json_ld_rendering=x_knora_json_ld_rendering, markup=markup, x_knora_accept_markup=x_knora_accept_markup, limit_to_project=limit_to_project)

Count resources using a Gravsearch query.

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
    api_instance = openapi_client.V2SearchApi(api_client)
    p1 = 'p1_example' # str | The Gravsearch query. See https://docs.dasch.swiss/latest/DSP-API/03-endpoints/api-v2/query-language/
    knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9 = 'knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9_example' # str |  (optional)
    x_knora_accept_schema = 'x_knora_accept_schema_example' # str | The ontology schema to be used for the request. If not specified, the default schema ApiV2Complex will be used. (optional)
    var_schema = 'var_schema_example' # str | The ontology schema to be used for the request. If not specified, the default schema ApiV2Complex will be used. (optional)
    x_knora_json_ld_rendering = 'x_knora_json_ld_rendering_example' # str | The JSON-LD rendering to be used for the request (flat or hierarchical). If not specified, hierarchical JSON-LD will be used. (optional)
    markup = 'markup_example' # str | The markup rendering to be used for the request (XML or standoff). (optional)
    x_knora_accept_markup = 'x_knora_accept_markup_example' # str | The markup rendering to be used for the request (XML or standoff). (optional)
    limit_to_project = 'limit_to_project_example' # str | The project to limit the search to. (optional)

    try:
        api_response = api_instance.get_v2_searchextended_count_p1(p1, knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9, x_knora_accept_schema=x_knora_accept_schema, var_schema=var_schema, x_knora_json_ld_rendering=x_knora_json_ld_rendering, markup=markup, x_knora_accept_markup=x_knora_accept_markup, limit_to_project=limit_to_project)
        print("The response of V2SearchApi->get_v2_searchextended_count_p1:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling V2SearchApi->get_v2_searchextended_count_p1: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **p1** | **str**| The Gravsearch query. See https://docs.dasch.swiss/latest/DSP-API/03-endpoints/api-v2/query-language/ | 
 **knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9** | **str**|  | [optional] 
 **x_knora_accept_schema** | **str**| The ontology schema to be used for the request. If not specified, the default schema ApiV2Complex will be used. | [optional] 
 **var_schema** | **str**| The ontology schema to be used for the request. If not specified, the default schema ApiV2Complex will be used. | [optional] 
 **x_knora_json_ld_rendering** | **str**| The JSON-LD rendering to be used for the request (flat or hierarchical). If not specified, hierarchical JSON-LD will be used. | [optional] 
 **markup** | **str**| The markup rendering to be used for the request (XML or standoff). | [optional] 
 **x_knora_accept_markup** | **str**| The markup rendering to be used for the request (XML or standoff). | [optional] 
 **limit_to_project** | **str**| The project to limit the search to. | [optional] 

### Return type

**str**

### Authorization

[httpAuth1](../README.md#httpAuth1), [httpAuth](../README.md#httpAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: text/plain, application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** |  |  * Content-Type -  <br>  |
**400** |  |  -  |
**401** |  |  -  |
**403** |  |  -  |
**404** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_v2_searchextended_p1**
> str get_v2_searchextended_p1(p1, knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9, x_knora_accept_schema=x_knora_accept_schema, var_schema=var_schema, x_knora_json_ld_rendering=x_knora_json_ld_rendering, markup=markup, x_knora_accept_markup=x_knora_accept_markup, limit_to_project=limit_to_project)

Search for resources using a Gravsearch query.

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
    api_instance = openapi_client.V2SearchApi(api_client)
    p1 = 'p1_example' # str | The Gravsearch query. See https://docs.dasch.swiss/latest/DSP-API/03-endpoints/api-v2/query-language/
    knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9 = 'knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9_example' # str |  (optional)
    x_knora_accept_schema = 'x_knora_accept_schema_example' # str | The ontology schema to be used for the request. If not specified, the default schema ApiV2Complex will be used. (optional)
    var_schema = 'var_schema_example' # str | The ontology schema to be used for the request. If not specified, the default schema ApiV2Complex will be used. (optional)
    x_knora_json_ld_rendering = 'x_knora_json_ld_rendering_example' # str | The JSON-LD rendering to be used for the request (flat or hierarchical). If not specified, hierarchical JSON-LD will be used. (optional)
    markup = 'markup_example' # str | The markup rendering to be used for the request (XML or standoff). (optional)
    x_knora_accept_markup = 'x_knora_accept_markup_example' # str | The markup rendering to be used for the request (XML or standoff). (optional)
    limit_to_project = 'limit_to_project_example' # str | The project to limit the search to. (optional)

    try:
        api_response = api_instance.get_v2_searchextended_p1(p1, knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9, x_knora_accept_schema=x_knora_accept_schema, var_schema=var_schema, x_knora_json_ld_rendering=x_knora_json_ld_rendering, markup=markup, x_knora_accept_markup=x_knora_accept_markup, limit_to_project=limit_to_project)
        print("The response of V2SearchApi->get_v2_searchextended_p1:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling V2SearchApi->get_v2_searchextended_p1: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **p1** | **str**| The Gravsearch query. See https://docs.dasch.swiss/latest/DSP-API/03-endpoints/api-v2/query-language/ | 
 **knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9** | **str**|  | [optional] 
 **x_knora_accept_schema** | **str**| The ontology schema to be used for the request. If not specified, the default schema ApiV2Complex will be used. | [optional] 
 **var_schema** | **str**| The ontology schema to be used for the request. If not specified, the default schema ApiV2Complex will be used. | [optional] 
 **x_knora_json_ld_rendering** | **str**| The JSON-LD rendering to be used for the request (flat or hierarchical). If not specified, hierarchical JSON-LD will be used. | [optional] 
 **markup** | **str**| The markup rendering to be used for the request (XML or standoff). | [optional] 
 **x_knora_accept_markup** | **str**| The markup rendering to be used for the request (XML or standoff). | [optional] 
 **limit_to_project** | **str**| The project to limit the search to. | [optional] 

### Return type

**str**

### Authorization

[httpAuth1](../README.md#httpAuth1), [httpAuth](../README.md#httpAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: text/plain, application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** |  |  * Content-Type -  <br>  |
**400** |  |  -  |
**401** |  |  -  |
**403** |  |  -  |
**404** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_v2_searchincominglinks_resourceiri**
> str get_v2_searchincominglinks_resourceiri(resource_iri, knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9, offset=offset, x_knora_accept_schema=x_knora_accept_schema, var_schema=var_schema, x_knora_json_ld_rendering=x_knora_json_ld_rendering, markup=markup, x_knora_accept_markup=x_knora_accept_markup, limit_to_project=limit_to_project)

Search for incoming links using a Gravsearch query with an offset.

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
    api_instance = openapi_client.V2SearchApi(api_client)
    resource_iri = 'resource_iri_example' # str | The IRI of the resource to retrieve
    knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9 = 'knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9_example' # str |  (optional)
    offset = 0 # int | The offset to be used for paging. (optional) (default to 0)
    x_knora_accept_schema = 'x_knora_accept_schema_example' # str | The ontology schema to be used for the request. If not specified, the default schema ApiV2Complex will be used. (optional)
    var_schema = 'var_schema_example' # str | The ontology schema to be used for the request. If not specified, the default schema ApiV2Complex will be used. (optional)
    x_knora_json_ld_rendering = 'x_knora_json_ld_rendering_example' # str | The JSON-LD rendering to be used for the request (flat or hierarchical). If not specified, hierarchical JSON-LD will be used. (optional)
    markup = 'markup_example' # str | The markup rendering to be used for the request (XML or standoff). (optional)
    x_knora_accept_markup = 'x_knora_accept_markup_example' # str | The markup rendering to be used for the request (XML or standoff). (optional)
    limit_to_project = 'limit_to_project_example' # str | The project to limit the search to. (optional)

    try:
        api_response = api_instance.get_v2_searchincominglinks_resourceiri(resource_iri, knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9, offset=offset, x_knora_accept_schema=x_knora_accept_schema, var_schema=var_schema, x_knora_json_ld_rendering=x_knora_json_ld_rendering, markup=markup, x_knora_accept_markup=x_knora_accept_markup, limit_to_project=limit_to_project)
        print("The response of V2SearchApi->get_v2_searchincominglinks_resourceiri:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling V2SearchApi->get_v2_searchincominglinks_resourceiri: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **resource_iri** | **str**| The IRI of the resource to retrieve | 
 **knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9** | **str**|  | [optional] 
 **offset** | **int**| The offset to be used for paging. | [optional] [default to 0]
 **x_knora_accept_schema** | **str**| The ontology schema to be used for the request. If not specified, the default schema ApiV2Complex will be used. | [optional] 
 **var_schema** | **str**| The ontology schema to be used for the request. If not specified, the default schema ApiV2Complex will be used. | [optional] 
 **x_knora_json_ld_rendering** | **str**| The JSON-LD rendering to be used for the request (flat or hierarchical). If not specified, hierarchical JSON-LD will be used. | [optional] 
 **markup** | **str**| The markup rendering to be used for the request (XML or standoff). | [optional] 
 **x_knora_accept_markup** | **str**| The markup rendering to be used for the request (XML or standoff). | [optional] 
 **limit_to_project** | **str**| The project to limit the search to. | [optional] 

### Return type

**str**

### Authorization

[httpAuth1](../README.md#httpAuth1), [httpAuth](../README.md#httpAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: text/plain, application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** |  |  * Content-Type -  <br>  |
**400** |  |  -  |
**401** |  |  -  |
**403** |  |  -  |
**404** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_v2_searchincomingregions_resourceiri**
> str get_v2_searchincomingregions_resourceiri(resource_iri, knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9, offset=offset, x_knora_accept_schema=x_knora_accept_schema, var_schema=var_schema, x_knora_json_ld_rendering=x_knora_json_ld_rendering, markup=markup, x_knora_accept_markup=x_knora_accept_markup, limit_to_project=limit_to_project)

Search for incoming regions using a Gravsearch query with an offset.

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
    api_instance = openapi_client.V2SearchApi(api_client)
    resource_iri = 'resource_iri_example' # str | The IRI of the resource to retrieve
    knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9 = 'knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9_example' # str |  (optional)
    offset = 0 # int | The offset to be used for paging. (optional) (default to 0)
    x_knora_accept_schema = 'x_knora_accept_schema_example' # str | The ontology schema to be used for the request. If not specified, the default schema ApiV2Complex will be used. (optional)
    var_schema = 'var_schema_example' # str | The ontology schema to be used for the request. If not specified, the default schema ApiV2Complex will be used. (optional)
    x_knora_json_ld_rendering = 'x_knora_json_ld_rendering_example' # str | The JSON-LD rendering to be used for the request (flat or hierarchical). If not specified, hierarchical JSON-LD will be used. (optional)
    markup = 'markup_example' # str | The markup rendering to be used for the request (XML or standoff). (optional)
    x_knora_accept_markup = 'x_knora_accept_markup_example' # str | The markup rendering to be used for the request (XML or standoff). (optional)
    limit_to_project = 'limit_to_project_example' # str | The project to limit the search to. (optional)

    try:
        api_response = api_instance.get_v2_searchincomingregions_resourceiri(resource_iri, knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9, offset=offset, x_knora_accept_schema=x_knora_accept_schema, var_schema=var_schema, x_knora_json_ld_rendering=x_knora_json_ld_rendering, markup=markup, x_knora_accept_markup=x_knora_accept_markup, limit_to_project=limit_to_project)
        print("The response of V2SearchApi->get_v2_searchincomingregions_resourceiri:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling V2SearchApi->get_v2_searchincomingregions_resourceiri: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **resource_iri** | **str**| The IRI of the resource to retrieve | 
 **knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9** | **str**|  | [optional] 
 **offset** | **int**| The offset to be used for paging. | [optional] [default to 0]
 **x_knora_accept_schema** | **str**| The ontology schema to be used for the request. If not specified, the default schema ApiV2Complex will be used. | [optional] 
 **var_schema** | **str**| The ontology schema to be used for the request. If not specified, the default schema ApiV2Complex will be used. | [optional] 
 **x_knora_json_ld_rendering** | **str**| The JSON-LD rendering to be used for the request (flat or hierarchical). If not specified, hierarchical JSON-LD will be used. | [optional] 
 **markup** | **str**| The markup rendering to be used for the request (XML or standoff). | [optional] 
 **x_knora_accept_markup** | **str**| The markup rendering to be used for the request (XML or standoff). | [optional] 
 **limit_to_project** | **str**| The project to limit the search to. | [optional] 

### Return type

**str**

### Authorization

[httpAuth1](../README.md#httpAuth1), [httpAuth](../README.md#httpAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: text/plain, application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** |  |  * Content-Type -  <br>  |
**400** |  |  -  |
**401** |  |  -  |
**403** |  |  -  |
**404** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **post_v2_searchextended**
> str post_v2_searchextended(body, knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9, x_knora_accept_schema=x_knora_accept_schema, var_schema=var_schema, x_knora_json_ld_rendering=x_knora_json_ld_rendering, markup=markup, x_knora_accept_markup=x_knora_accept_markup, limit_to_project=limit_to_project)

Search for resources using a Gravsearch query.

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
    api_instance = openapi_client.V2SearchApi(api_client)
    body = 'body_example' # str | The Gravsearch query. See https://docs.dasch.swiss/latest/DSP-API/03-endpoints/api-v2/query-language/
    knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9 = 'knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9_example' # str |  (optional)
    x_knora_accept_schema = 'x_knora_accept_schema_example' # str | The ontology schema to be used for the request. If not specified, the default schema ApiV2Complex will be used. (optional)
    var_schema = 'var_schema_example' # str | The ontology schema to be used for the request. If not specified, the default schema ApiV2Complex will be used. (optional)
    x_knora_json_ld_rendering = 'x_knora_json_ld_rendering_example' # str | The JSON-LD rendering to be used for the request (flat or hierarchical). If not specified, hierarchical JSON-LD will be used. (optional)
    markup = 'markup_example' # str | The markup rendering to be used for the request (XML or standoff). (optional)
    x_knora_accept_markup = 'x_knora_accept_markup_example' # str | The markup rendering to be used for the request (XML or standoff). (optional)
    limit_to_project = 'limit_to_project_example' # str | The project to limit the search to. (optional)

    try:
        api_response = api_instance.post_v2_searchextended(body, knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9, x_knora_accept_schema=x_knora_accept_schema, var_schema=var_schema, x_knora_json_ld_rendering=x_knora_json_ld_rendering, markup=markup, x_knora_accept_markup=x_knora_accept_markup, limit_to_project=limit_to_project)
        print("The response of V2SearchApi->post_v2_searchextended:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling V2SearchApi->post_v2_searchextended: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | **str**| The Gravsearch query. See https://docs.dasch.swiss/latest/DSP-API/03-endpoints/api-v2/query-language/ | 
 **knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9** | **str**|  | [optional] 
 **x_knora_accept_schema** | **str**| The ontology schema to be used for the request. If not specified, the default schema ApiV2Complex will be used. | [optional] 
 **var_schema** | **str**| The ontology schema to be used for the request. If not specified, the default schema ApiV2Complex will be used. | [optional] 
 **x_knora_json_ld_rendering** | **str**| The JSON-LD rendering to be used for the request (flat or hierarchical). If not specified, hierarchical JSON-LD will be used. | [optional] 
 **markup** | **str**| The markup rendering to be used for the request (XML or standoff). | [optional] 
 **x_knora_accept_markup** | **str**| The markup rendering to be used for the request (XML or standoff). | [optional] 
 **limit_to_project** | **str**| The project to limit the search to. | [optional] 

### Return type

**str**

### Authorization

[httpAuth1](../README.md#httpAuth1), [httpAuth](../README.md#httpAuth)

### HTTP request headers

 - **Content-Type**: text/plain
 - **Accept**: text/plain, application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** |  |  * Content-Type -  <br>  |
**400** |  |  -  |
**401** |  |  -  |
**403** |  |  -  |
**404** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **post_v2_searchextended_count**
> str post_v2_searchextended_count(body, knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9, x_knora_accept_schema=x_knora_accept_schema, var_schema=var_schema, x_knora_json_ld_rendering=x_knora_json_ld_rendering, markup=markup, x_knora_accept_markup=x_knora_accept_markup, limit_to_project=limit_to_project)

Count resources using a Gravsearch query.

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
    api_instance = openapi_client.V2SearchApi(api_client)
    body = 'body_example' # str | The Gravsearch query. See https://docs.dasch.swiss/latest/DSP-API/03-endpoints/api-v2/query-language/
    knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9 = 'knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9_example' # str |  (optional)
    x_knora_accept_schema = 'x_knora_accept_schema_example' # str | The ontology schema to be used for the request. If not specified, the default schema ApiV2Complex will be used. (optional)
    var_schema = 'var_schema_example' # str | The ontology schema to be used for the request. If not specified, the default schema ApiV2Complex will be used. (optional)
    x_knora_json_ld_rendering = 'x_knora_json_ld_rendering_example' # str | The JSON-LD rendering to be used for the request (flat or hierarchical). If not specified, hierarchical JSON-LD will be used. (optional)
    markup = 'markup_example' # str | The markup rendering to be used for the request (XML or standoff). (optional)
    x_knora_accept_markup = 'x_knora_accept_markup_example' # str | The markup rendering to be used for the request (XML or standoff). (optional)
    limit_to_project = 'limit_to_project_example' # str | The project to limit the search to. (optional)

    try:
        api_response = api_instance.post_v2_searchextended_count(body, knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9, x_knora_accept_schema=x_knora_accept_schema, var_schema=var_schema, x_knora_json_ld_rendering=x_knora_json_ld_rendering, markup=markup, x_knora_accept_markup=x_knora_accept_markup, limit_to_project=limit_to_project)
        print("The response of V2SearchApi->post_v2_searchextended_count:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling V2SearchApi->post_v2_searchextended_count: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | **str**| The Gravsearch query. See https://docs.dasch.swiss/latest/DSP-API/03-endpoints/api-v2/query-language/ | 
 **knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9** | **str**|  | [optional] 
 **x_knora_accept_schema** | **str**| The ontology schema to be used for the request. If not specified, the default schema ApiV2Complex will be used. | [optional] 
 **var_schema** | **str**| The ontology schema to be used for the request. If not specified, the default schema ApiV2Complex will be used. | [optional] 
 **x_knora_json_ld_rendering** | **str**| The JSON-LD rendering to be used for the request (flat or hierarchical). If not specified, hierarchical JSON-LD will be used. | [optional] 
 **markup** | **str**| The markup rendering to be used for the request (XML or standoff). | [optional] 
 **x_knora_accept_markup** | **str**| The markup rendering to be used for the request (XML or standoff). | [optional] 
 **limit_to_project** | **str**| The project to limit the search to. | [optional] 

### Return type

**str**

### Authorization

[httpAuth1](../README.md#httpAuth1), [httpAuth](../README.md#httpAuth)

### HTTP request headers

 - **Content-Type**: text/plain
 - **Accept**: text/plain, application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** |  |  * Content-Type -  <br>  |
**400** |  |  -  |
**401** |  |  -  |
**403** |  |  -  |
**404** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

