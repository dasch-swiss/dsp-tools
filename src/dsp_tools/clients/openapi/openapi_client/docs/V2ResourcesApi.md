# openapi_client.V2ResourcesApi

All URIs are relative to *https://api.dasch.swiss:443*

Method | HTTP request | Description
------------- | ------------- | -------------
[**get_v2_graph_resourceiri**](V2ResourcesApi.md#get_v2_graph_resourceiri) | **GET** /v2/graph/{resourceIri} | 
[**get_v2_resources**](V2ResourcesApi.md#get_v2_resources) | **GET** /v2/resources | 
[**get_v2_resources_history_resourceiri**](V2ResourcesApi.md#get_v2_resources_history_resourceiri) | **GET** /v2/resources/history/{resourceIri} | 
[**get_v2_resources_iiifmanifest_resourceiri**](V2ResourcesApi.md#get_v2_resources_iiifmanifest_resourceiri) | **GET** /v2/resources/iiifmanifest/{resourceIri} | 
[**get_v2_resources_info**](V2ResourcesApi.md#get_v2_resources_info) | **GET** /v2/resources/info | 
[**get_v2_resources_projecthistoryevents_projectiri**](V2ResourcesApi.md#get_v2_resources_projecthistoryevents_projectiri) | **GET** /v2/resources/projectHistoryEvents/{projectIri} | 
[**get_v2_resources_resourcehistoryevents_resourceiri**](V2ResourcesApi.md#get_v2_resources_resourcehistoryevents_resourceiri) | **GET** /v2/resources/resourceHistoryEvents/{resourceIri} | 
[**get_v2_resourcespreview**](V2ResourcesApi.md#get_v2_resourcespreview) | **GET** /v2/resourcespreview | 
[**get_v2_tei_resourceiri**](V2ResourcesApi.md#get_v2_tei_resourceiri) | **GET** /v2/tei/{resourceIri} | 
[**post_v2_resources**](V2ResourcesApi.md#post_v2_resources) | **POST** /v2/resources | 
[**post_v2_resources_delete**](V2ResourcesApi.md#post_v2_resources_delete) | **POST** /v2/resources/delete | 
[**post_v2_resources_erase**](V2ResourcesApi.md#post_v2_resources_erase) | **POST** /v2/resources/erase | 
[**put_v2_resources**](V2ResourcesApi.md#put_v2_resources) | **PUT** /v2/resources | 


# **get_v2_graph_resourceiri**
> str get_v2_graph_resourceiri(resource_iri, knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9, x_knora_accept_schema=x_knora_accept_schema, var_schema=var_schema, x_knora_json_ld_rendering=x_knora_json_ld_rendering, markup=markup, x_knora_accept_markup=x_knora_accept_markup, depth=depth, direction=direction, exclude_property=exclude_property)

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
    api_instance = openapi_client.V2ResourcesApi(api_client)
    resource_iri = 'resource_iri_example' # str | 
    knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9 = 'knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9_example' # str |  (optional)
    x_knora_accept_schema = 'x_knora_accept_schema_example' # str | The ontology schema to be used for the request. If not specified, the default schema ApiV2Complex will be used. (optional)
    var_schema = 'var_schema_example' # str | The ontology schema to be used for the request. If not specified, the default schema ApiV2Complex will be used. (optional)
    x_knora_json_ld_rendering = 'x_knora_json_ld_rendering_example' # str | The JSON-LD rendering to be used for the request (flat or hierarchical). If not specified, hierarchical JSON-LD will be used. (optional)
    markup = 'markup_example' # str | The markup rendering to be used for the request (XML or standoff). (optional)
    x_knora_accept_markup = 'x_knora_accept_markup_example' # str | The markup rendering to be used for the request (XML or standoff). (optional)
    depth = 4 # int |  (optional) (default to 4)
    direction = 'outbound' # str |  (optional) (default to 'outbound')
    exclude_property = 'exclude_property_example' # str |  (optional)

    try:
        api_response = api_instance.get_v2_graph_resourceiri(resource_iri, knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9, x_knora_accept_schema=x_knora_accept_schema, var_schema=var_schema, x_knora_json_ld_rendering=x_knora_json_ld_rendering, markup=markup, x_knora_accept_markup=x_knora_accept_markup, depth=depth, direction=direction, exclude_property=exclude_property)
        print("The response of V2ResourcesApi->get_v2_graph_resourceiri:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling V2ResourcesApi->get_v2_graph_resourceiri: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **resource_iri** | **str**|  | 
 **knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9** | **str**|  | [optional] 
 **x_knora_accept_schema** | **str**| The ontology schema to be used for the request. If not specified, the default schema ApiV2Complex will be used. | [optional] 
 **var_schema** | **str**| The ontology schema to be used for the request. If not specified, the default schema ApiV2Complex will be used. | [optional] 
 **x_knora_json_ld_rendering** | **str**| The JSON-LD rendering to be used for the request (flat or hierarchical). If not specified, hierarchical JSON-LD will be used. | [optional] 
 **markup** | **str**| The markup rendering to be used for the request (XML or standoff). | [optional] 
 **x_knora_accept_markup** | **str**| The markup rendering to be used for the request (XML or standoff). | [optional] 
 **depth** | **int**|  | [optional] [default to 4]
 **direction** | **str**|  | [optional] [default to &#39;outbound&#39;]
 **exclude_property** | **str**|  | [optional] 

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

# **get_v2_resources**
> str get_v2_resources(knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9, x_knora_accept_schema=x_knora_accept_schema, var_schema=var_schema, x_knora_json_ld_rendering=x_knora_json_ld_rendering, markup=markup, x_knora_accept_markup=x_knora_accept_markup, version=version, version_date=version_date)

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
    api_instance = openapi_client.V2ResourcesApi(api_client)
    knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9 = 'knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9_example' # str |  (optional)
    x_knora_accept_schema = 'x_knora_accept_schema_example' # str | The ontology schema to be used for the request. If not specified, the default schema ApiV2Complex will be used. (optional)
    var_schema = 'var_schema_example' # str | The ontology schema to be used for the request. If not specified, the default schema ApiV2Complex will be used. (optional)
    x_knora_json_ld_rendering = 'x_knora_json_ld_rendering_example' # str | The JSON-LD rendering to be used for the request (flat or hierarchical). If not specified, hierarchical JSON-LD will be used. (optional)
    markup = 'markup_example' # str | The markup rendering to be used for the request (XML or standoff). (optional)
    x_knora_accept_markup = 'x_knora_accept_markup_example' # str | The markup rendering to be used for the request (XML or standoff). (optional)
    version = 'version_example' # str |  (optional)
    version_date = 'version_date_example' # str |  (optional)

    try:
        api_response = api_instance.get_v2_resources(knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9, x_knora_accept_schema=x_knora_accept_schema, var_schema=var_schema, x_knora_json_ld_rendering=x_knora_json_ld_rendering, markup=markup, x_knora_accept_markup=x_knora_accept_markup, version=version, version_date=version_date)
        print("The response of V2ResourcesApi->get_v2_resources:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling V2ResourcesApi->get_v2_resources: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9** | **str**|  | [optional] 
 **x_knora_accept_schema** | **str**| The ontology schema to be used for the request. If not specified, the default schema ApiV2Complex will be used. | [optional] 
 **var_schema** | **str**| The ontology schema to be used for the request. If not specified, the default schema ApiV2Complex will be used. | [optional] 
 **x_knora_json_ld_rendering** | **str**| The JSON-LD rendering to be used for the request (flat or hierarchical). If not specified, hierarchical JSON-LD will be used. | [optional] 
 **markup** | **str**| The markup rendering to be used for the request (XML or standoff). | [optional] 
 **x_knora_accept_markup** | **str**| The markup rendering to be used for the request (XML or standoff). | [optional] 
 **version** | **str**|  | [optional] 
 **version_date** | **str**|  | [optional] 

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

# **get_v2_resources_history_resourceiri**
> str get_v2_resources_history_resourceiri(resource_iri, knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9, x_knora_accept_schema=x_knora_accept_schema, var_schema=var_schema, x_knora_json_ld_rendering=x_knora_json_ld_rendering, markup=markup, x_knora_accept_markup=x_knora_accept_markup, start_date=start_date, start_date2=start_date2, end_date=end_date, end_date2=end_date2)

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
    api_instance = openapi_client.V2ResourcesApi(api_client)
    resource_iri = 'resource_iri_example' # str | 
    knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9 = 'knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9_example' # str |  (optional)
    x_knora_accept_schema = 'x_knora_accept_schema_example' # str | The ontology schema to be used for the request. If not specified, the default schema ApiV2Complex will be used. (optional)
    var_schema = 'var_schema_example' # str | The ontology schema to be used for the request. If not specified, the default schema ApiV2Complex will be used. (optional)
    x_knora_json_ld_rendering = 'x_knora_json_ld_rendering_example' # str | The JSON-LD rendering to be used for the request (flat or hierarchical). If not specified, hierarchical JSON-LD will be used. (optional)
    markup = 'markup_example' # str | The markup rendering to be used for the request (XML or standoff). (optional)
    x_knora_accept_markup = 'x_knora_accept_markup_example' # str | The markup rendering to be used for the request (XML or standoff). (optional)
    start_date = 'start_date_example' # str |  (optional)
    start_date2 = 'start_date_example' # str |  (optional)
    end_date = 'end_date_example' # str |  (optional)
    end_date2 = 'end_date_example' # str |  (optional)

    try:
        api_response = api_instance.get_v2_resources_history_resourceiri(resource_iri, knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9, x_knora_accept_schema=x_knora_accept_schema, var_schema=var_schema, x_knora_json_ld_rendering=x_knora_json_ld_rendering, markup=markup, x_knora_accept_markup=x_knora_accept_markup, start_date=start_date, start_date2=start_date2, end_date=end_date, end_date2=end_date2)
        print("The response of V2ResourcesApi->get_v2_resources_history_resourceiri:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling V2ResourcesApi->get_v2_resources_history_resourceiri: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **resource_iri** | **str**|  | 
 **knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9** | **str**|  | [optional] 
 **x_knora_accept_schema** | **str**| The ontology schema to be used for the request. If not specified, the default schema ApiV2Complex will be used. | [optional] 
 **var_schema** | **str**| The ontology schema to be used for the request. If not specified, the default schema ApiV2Complex will be used. | [optional] 
 **x_knora_json_ld_rendering** | **str**| The JSON-LD rendering to be used for the request (flat or hierarchical). If not specified, hierarchical JSON-LD will be used. | [optional] 
 **markup** | **str**| The markup rendering to be used for the request (XML or standoff). | [optional] 
 **x_knora_accept_markup** | **str**| The markup rendering to be used for the request (XML or standoff). | [optional] 
 **start_date** | **str**|  | [optional] 
 **start_date2** | **str**|  | [optional] 
 **end_date** | **str**|  | [optional] 
 **end_date2** | **str**|  | [optional] 

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

# **get_v2_resources_iiifmanifest_resourceiri**
> str get_v2_resources_iiifmanifest_resourceiri(resource_iri, knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9, x_knora_accept_schema=x_knora_accept_schema, var_schema=var_schema, x_knora_json_ld_rendering=x_knora_json_ld_rendering, markup=markup, x_knora_accept_markup=x_knora_accept_markup)

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
    api_instance = openapi_client.V2ResourcesApi(api_client)
    resource_iri = 'resource_iri_example' # str | 
    knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9 = 'knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9_example' # str |  (optional)
    x_knora_accept_schema = 'x_knora_accept_schema_example' # str | The ontology schema to be used for the request. If not specified, the default schema ApiV2Complex will be used. (optional)
    var_schema = 'var_schema_example' # str | The ontology schema to be used for the request. If not specified, the default schema ApiV2Complex will be used. (optional)
    x_knora_json_ld_rendering = 'x_knora_json_ld_rendering_example' # str | The JSON-LD rendering to be used for the request (flat or hierarchical). If not specified, hierarchical JSON-LD will be used. (optional)
    markup = 'markup_example' # str | The markup rendering to be used for the request (XML or standoff). (optional)
    x_knora_accept_markup = 'x_knora_accept_markup_example' # str | The markup rendering to be used for the request (XML or standoff). (optional)

    try:
        api_response = api_instance.get_v2_resources_iiifmanifest_resourceiri(resource_iri, knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9, x_knora_accept_schema=x_knora_accept_schema, var_schema=var_schema, x_knora_json_ld_rendering=x_knora_json_ld_rendering, markup=markup, x_knora_accept_markup=x_knora_accept_markup)
        print("The response of V2ResourcesApi->get_v2_resources_iiifmanifest_resourceiri:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling V2ResourcesApi->get_v2_resources_iiifmanifest_resourceiri: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **resource_iri** | **str**|  | 
 **knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9** | **str**|  | [optional] 
 **x_knora_accept_schema** | **str**| The ontology schema to be used for the request. If not specified, the default schema ApiV2Complex will be used. | [optional] 
 **var_schema** | **str**| The ontology schema to be used for the request. If not specified, the default schema ApiV2Complex will be used. | [optional] 
 **x_knora_json_ld_rendering** | **str**| The JSON-LD rendering to be used for the request (flat or hierarchical). If not specified, hierarchical JSON-LD will be used. | [optional] 
 **markup** | **str**| The markup rendering to be used for the request (XML or standoff). | [optional] 
 **x_knora_accept_markup** | **str**| The markup rendering to be used for the request (XML or standoff). | [optional] 

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

# **get_v2_resources_info**
> ListResponseDto get_v2_resources_info(x_knora_accept_project, resource_class, order=order, order_by=order_by)

### Example


```python
import openapi_client
from openapi_client.models.list_response_dto import ListResponseDto
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
    api_instance = openapi_client.V2ResourcesApi(api_client)
    x_knora_accept_project = 'x_knora_accept_project_example' # str | 
    resource_class = 'resource_class_example' # str | 
    order = 'order_example' # str |  (optional)
    order_by = 'order_by_example' # str |  (optional)

    try:
        api_response = api_instance.get_v2_resources_info(x_knora_accept_project, resource_class, order=order, order_by=order_by)
        print("The response of V2ResourcesApi->get_v2_resources_info:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling V2ResourcesApi->get_v2_resources_info: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **x_knora_accept_project** | **str**|  | 
 **resource_class** | **str**|  | 
 **order** | **str**|  | [optional] 
 **order_by** | **str**|  | [optional] 

### Return type

[**ListResponseDto**](ListResponseDto.md)

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

# **get_v2_resources_projecthistoryevents_projectiri**
> str get_v2_resources_projecthistoryevents_projectiri(project_iri, knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9, x_knora_accept_schema=x_knora_accept_schema, var_schema=var_schema, x_knora_json_ld_rendering=x_knora_json_ld_rendering, markup=markup, x_knora_accept_markup=x_knora_accept_markup)

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
    api_instance = openapi_client.V2ResourcesApi(api_client)
    project_iri = 'project_iri_example' # str | 
    knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9 = 'knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9_example' # str |  (optional)
    x_knora_accept_schema = 'x_knora_accept_schema_example' # str | The ontology schema to be used for the request. If not specified, the default schema ApiV2Complex will be used. (optional)
    var_schema = 'var_schema_example' # str | The ontology schema to be used for the request. If not specified, the default schema ApiV2Complex will be used. (optional)
    x_knora_json_ld_rendering = 'x_knora_json_ld_rendering_example' # str | The JSON-LD rendering to be used for the request (flat or hierarchical). If not specified, hierarchical JSON-LD will be used. (optional)
    markup = 'markup_example' # str | The markup rendering to be used for the request (XML or standoff). (optional)
    x_knora_accept_markup = 'x_knora_accept_markup_example' # str | The markup rendering to be used for the request (XML or standoff). (optional)

    try:
        api_response = api_instance.get_v2_resources_projecthistoryevents_projectiri(project_iri, knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9, x_knora_accept_schema=x_knora_accept_schema, var_schema=var_schema, x_knora_json_ld_rendering=x_knora_json_ld_rendering, markup=markup, x_knora_accept_markup=x_knora_accept_markup)
        print("The response of V2ResourcesApi->get_v2_resources_projecthistoryevents_projectiri:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling V2ResourcesApi->get_v2_resources_projecthistoryevents_projectiri: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **project_iri** | **str**|  | 
 **knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9** | **str**|  | [optional] 
 **x_knora_accept_schema** | **str**| The ontology schema to be used for the request. If not specified, the default schema ApiV2Complex will be used. | [optional] 
 **var_schema** | **str**| The ontology schema to be used for the request. If not specified, the default schema ApiV2Complex will be used. | [optional] 
 **x_knora_json_ld_rendering** | **str**| The JSON-LD rendering to be used for the request (flat or hierarchical). If not specified, hierarchical JSON-LD will be used. | [optional] 
 **markup** | **str**| The markup rendering to be used for the request (XML or standoff). | [optional] 
 **x_knora_accept_markup** | **str**| The markup rendering to be used for the request (XML or standoff). | [optional] 

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

# **get_v2_resources_resourcehistoryevents_resourceiri**
> str get_v2_resources_resourcehistoryevents_resourceiri(resource_iri, knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9, x_knora_accept_schema=x_knora_accept_schema, var_schema=var_schema, x_knora_json_ld_rendering=x_knora_json_ld_rendering, markup=markup, x_knora_accept_markup=x_knora_accept_markup)

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
    api_instance = openapi_client.V2ResourcesApi(api_client)
    resource_iri = 'resource_iri_example' # str | 
    knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9 = 'knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9_example' # str |  (optional)
    x_knora_accept_schema = 'x_knora_accept_schema_example' # str | The ontology schema to be used for the request. If not specified, the default schema ApiV2Complex will be used. (optional)
    var_schema = 'var_schema_example' # str | The ontology schema to be used for the request. If not specified, the default schema ApiV2Complex will be used. (optional)
    x_knora_json_ld_rendering = 'x_knora_json_ld_rendering_example' # str | The JSON-LD rendering to be used for the request (flat or hierarchical). If not specified, hierarchical JSON-LD will be used. (optional)
    markup = 'markup_example' # str | The markup rendering to be used for the request (XML or standoff). (optional)
    x_knora_accept_markup = 'x_knora_accept_markup_example' # str | The markup rendering to be used for the request (XML or standoff). (optional)

    try:
        api_response = api_instance.get_v2_resources_resourcehistoryevents_resourceiri(resource_iri, knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9, x_knora_accept_schema=x_knora_accept_schema, var_schema=var_schema, x_knora_json_ld_rendering=x_knora_json_ld_rendering, markup=markup, x_knora_accept_markup=x_knora_accept_markup)
        print("The response of V2ResourcesApi->get_v2_resources_resourcehistoryevents_resourceiri:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling V2ResourcesApi->get_v2_resources_resourcehistoryevents_resourceiri: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **resource_iri** | **str**|  | 
 **knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9** | **str**|  | [optional] 
 **x_knora_accept_schema** | **str**| The ontology schema to be used for the request. If not specified, the default schema ApiV2Complex will be used. | [optional] 
 **var_schema** | **str**| The ontology schema to be used for the request. If not specified, the default schema ApiV2Complex will be used. | [optional] 
 **x_knora_json_ld_rendering** | **str**| The JSON-LD rendering to be used for the request (flat or hierarchical). If not specified, hierarchical JSON-LD will be used. | [optional] 
 **markup** | **str**| The markup rendering to be used for the request (XML or standoff). | [optional] 
 **x_knora_accept_markup** | **str**| The markup rendering to be used for the request (XML or standoff). | [optional] 

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

# **get_v2_resourcespreview**
> str get_v2_resourcespreview(knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9, x_knora_accept_schema=x_knora_accept_schema, var_schema=var_schema, x_knora_json_ld_rendering=x_knora_json_ld_rendering, markup=markup, x_knora_accept_markup=x_knora_accept_markup)

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
    api_instance = openapi_client.V2ResourcesApi(api_client)
    knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9 = 'knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9_example' # str |  (optional)
    x_knora_accept_schema = 'x_knora_accept_schema_example' # str | The ontology schema to be used for the request. If not specified, the default schema ApiV2Complex will be used. (optional)
    var_schema = 'var_schema_example' # str | The ontology schema to be used for the request. If not specified, the default schema ApiV2Complex will be used. (optional)
    x_knora_json_ld_rendering = 'x_knora_json_ld_rendering_example' # str | The JSON-LD rendering to be used for the request (flat or hierarchical). If not specified, hierarchical JSON-LD will be used. (optional)
    markup = 'markup_example' # str | The markup rendering to be used for the request (XML or standoff). (optional)
    x_knora_accept_markup = 'x_knora_accept_markup_example' # str | The markup rendering to be used for the request (XML or standoff). (optional)

    try:
        api_response = api_instance.get_v2_resourcespreview(knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9, x_knora_accept_schema=x_knora_accept_schema, var_schema=var_schema, x_knora_json_ld_rendering=x_knora_json_ld_rendering, markup=markup, x_knora_accept_markup=x_knora_accept_markup)
        print("The response of V2ResourcesApi->get_v2_resourcespreview:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling V2ResourcesApi->get_v2_resourcespreview: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9** | **str**|  | [optional] 
 **x_knora_accept_schema** | **str**| The ontology schema to be used for the request. If not specified, the default schema ApiV2Complex will be used. | [optional] 
 **var_schema** | **str**| The ontology schema to be used for the request. If not specified, the default schema ApiV2Complex will be used. | [optional] 
 **x_knora_json_ld_rendering** | **str**| The JSON-LD rendering to be used for the request (flat or hierarchical). If not specified, hierarchical JSON-LD will be used. | [optional] 
 **markup** | **str**| The markup rendering to be used for the request (XML or standoff). | [optional] 
 **x_knora_accept_markup** | **str**| The markup rendering to be used for the request (XML or standoff). | [optional] 

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

# **get_v2_tei_resourceiri**
> str get_v2_tei_resourceiri(resource_iri, text_property, knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9, mapping_iri=mapping_iri, gravsearch_template_iri=gravsearch_template_iri, header_xslt_iri=header_xslt_iri)

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
    api_instance = openapi_client.V2ResourcesApi(api_client)
    resource_iri = 'resource_iri_example' # str | 
    text_property = 'text_property_example' # str | 
    knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9 = 'knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9_example' # str |  (optional)
    mapping_iri = 'mapping_iri_example' # str |  (optional)
    gravsearch_template_iri = 'gravsearch_template_iri_example' # str |  (optional)
    header_xslt_iri = 'header_xslt_iri_example' # str |  (optional)

    try:
        api_response = api_instance.get_v2_tei_resourceiri(resource_iri, text_property, knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9, mapping_iri=mapping_iri, gravsearch_template_iri=gravsearch_template_iri, header_xslt_iri=header_xslt_iri)
        print("The response of V2ResourcesApi->get_v2_tei_resourceiri:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling V2ResourcesApi->get_v2_tei_resourceiri: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **resource_iri** | **str**|  | 
 **text_property** | **str**|  | 
 **knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9** | **str**|  | [optional] 
 **mapping_iri** | **str**|  | [optional] 
 **gravsearch_template_iri** | **str**|  | [optional] 
 **header_xslt_iri** | **str**|  | [optional] 

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

# **post_v2_resources**
> str post_v2_resources(body, knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9, x_knora_accept_schema=x_knora_accept_schema, var_schema=var_schema, x_knora_json_ld_rendering=x_knora_json_ld_rendering, markup=markup, x_knora_accept_markup=x_knora_accept_markup)

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
    api_instance = openapi_client.V2ResourcesApi(api_client)
    body = 'body_example' # str | 
    knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9 = 'knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9_example' # str |  (optional)
    x_knora_accept_schema = 'x_knora_accept_schema_example' # str | The ontology schema to be used for the request. If not specified, the default schema ApiV2Complex will be used. (optional)
    var_schema = 'var_schema_example' # str | The ontology schema to be used for the request. If not specified, the default schema ApiV2Complex will be used. (optional)
    x_knora_json_ld_rendering = 'x_knora_json_ld_rendering_example' # str | The JSON-LD rendering to be used for the request (flat or hierarchical). If not specified, hierarchical JSON-LD will be used. (optional)
    markup = 'markup_example' # str | The markup rendering to be used for the request (XML or standoff). (optional)
    x_knora_accept_markup = 'x_knora_accept_markup_example' # str | The markup rendering to be used for the request (XML or standoff). (optional)

    try:
        api_response = api_instance.post_v2_resources(body, knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9, x_knora_accept_schema=x_knora_accept_schema, var_schema=var_schema, x_knora_json_ld_rendering=x_knora_json_ld_rendering, markup=markup, x_knora_accept_markup=x_knora_accept_markup)
        print("The response of V2ResourcesApi->post_v2_resources:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling V2ResourcesApi->post_v2_resources: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | **str**|  | 
 **knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9** | **str**|  | [optional] 
 **x_knora_accept_schema** | **str**| The ontology schema to be used for the request. If not specified, the default schema ApiV2Complex will be used. | [optional] 
 **var_schema** | **str**| The ontology schema to be used for the request. If not specified, the default schema ApiV2Complex will be used. | [optional] 
 **x_knora_json_ld_rendering** | **str**| The JSON-LD rendering to be used for the request (flat or hierarchical). If not specified, hierarchical JSON-LD will be used. | [optional] 
 **markup** | **str**| The markup rendering to be used for the request (XML or standoff). | [optional] 
 **x_knora_accept_markup** | **str**| The markup rendering to be used for the request (XML or standoff). | [optional] 

### Return type

**str**

### Authorization

[httpAuth1](../README.md#httpAuth1), [httpAuth](../README.md#httpAuth)

### HTTP request headers

 - **Content-Type**: application/json
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

# **post_v2_resources_delete**
> str post_v2_resources_delete(body, knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9, x_knora_accept_schema=x_knora_accept_schema, var_schema=var_schema, x_knora_json_ld_rendering=x_knora_json_ld_rendering, markup=markup, x_knora_accept_markup=x_knora_accept_markup)

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
    api_instance = openapi_client.V2ResourcesApi(api_client)
    body = 'body_example' # str | 
    knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9 = 'knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9_example' # str |  (optional)
    x_knora_accept_schema = 'x_knora_accept_schema_example' # str | The ontology schema to be used for the request. If not specified, the default schema ApiV2Complex will be used. (optional)
    var_schema = 'var_schema_example' # str | The ontology schema to be used for the request. If not specified, the default schema ApiV2Complex will be used. (optional)
    x_knora_json_ld_rendering = 'x_knora_json_ld_rendering_example' # str | The JSON-LD rendering to be used for the request (flat or hierarchical). If not specified, hierarchical JSON-LD will be used. (optional)
    markup = 'markup_example' # str | The markup rendering to be used for the request (XML or standoff). (optional)
    x_knora_accept_markup = 'x_knora_accept_markup_example' # str | The markup rendering to be used for the request (XML or standoff). (optional)

    try:
        api_response = api_instance.post_v2_resources_delete(body, knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9, x_knora_accept_schema=x_knora_accept_schema, var_schema=var_schema, x_knora_json_ld_rendering=x_knora_json_ld_rendering, markup=markup, x_knora_accept_markup=x_knora_accept_markup)
        print("The response of V2ResourcesApi->post_v2_resources_delete:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling V2ResourcesApi->post_v2_resources_delete: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | **str**|  | 
 **knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9** | **str**|  | [optional] 
 **x_knora_accept_schema** | **str**| The ontology schema to be used for the request. If not specified, the default schema ApiV2Complex will be used. | [optional] 
 **var_schema** | **str**| The ontology schema to be used for the request. If not specified, the default schema ApiV2Complex will be used. | [optional] 
 **x_knora_json_ld_rendering** | **str**| The JSON-LD rendering to be used for the request (flat or hierarchical). If not specified, hierarchical JSON-LD will be used. | [optional] 
 **markup** | **str**| The markup rendering to be used for the request (XML or standoff). | [optional] 
 **x_knora_accept_markup** | **str**| The markup rendering to be used for the request (XML or standoff). | [optional] 

### Return type

**str**

### Authorization

[httpAuth1](../README.md#httpAuth1), [httpAuth](../README.md#httpAuth)

### HTTP request headers

 - **Content-Type**: application/json
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

# **post_v2_resources_erase**
> str post_v2_resources_erase(body, knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9, x_knora_accept_schema=x_knora_accept_schema, var_schema=var_schema, x_knora_json_ld_rendering=x_knora_json_ld_rendering, markup=markup, x_knora_accept_markup=x_knora_accept_markup)

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
    api_instance = openapi_client.V2ResourcesApi(api_client)
    body = 'body_example' # str | 
    knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9 = 'knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9_example' # str |  (optional)
    x_knora_accept_schema = 'x_knora_accept_schema_example' # str | The ontology schema to be used for the request. If not specified, the default schema ApiV2Complex will be used. (optional)
    var_schema = 'var_schema_example' # str | The ontology schema to be used for the request. If not specified, the default schema ApiV2Complex will be used. (optional)
    x_knora_json_ld_rendering = 'x_knora_json_ld_rendering_example' # str | The JSON-LD rendering to be used for the request (flat or hierarchical). If not specified, hierarchical JSON-LD will be used. (optional)
    markup = 'markup_example' # str | The markup rendering to be used for the request (XML or standoff). (optional)
    x_knora_accept_markup = 'x_knora_accept_markup_example' # str | The markup rendering to be used for the request (XML or standoff). (optional)

    try:
        api_response = api_instance.post_v2_resources_erase(body, knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9, x_knora_accept_schema=x_knora_accept_schema, var_schema=var_schema, x_knora_json_ld_rendering=x_knora_json_ld_rendering, markup=markup, x_knora_accept_markup=x_knora_accept_markup)
        print("The response of V2ResourcesApi->post_v2_resources_erase:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling V2ResourcesApi->post_v2_resources_erase: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | **str**|  | 
 **knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9** | **str**|  | [optional] 
 **x_knora_accept_schema** | **str**| The ontology schema to be used for the request. If not specified, the default schema ApiV2Complex will be used. | [optional] 
 **var_schema** | **str**| The ontology schema to be used for the request. If not specified, the default schema ApiV2Complex will be used. | [optional] 
 **x_knora_json_ld_rendering** | **str**| The JSON-LD rendering to be used for the request (flat or hierarchical). If not specified, hierarchical JSON-LD will be used. | [optional] 
 **markup** | **str**| The markup rendering to be used for the request (XML or standoff). | [optional] 
 **x_knora_accept_markup** | **str**| The markup rendering to be used for the request (XML or standoff). | [optional] 

### Return type

**str**

### Authorization

[httpAuth1](../README.md#httpAuth1), [httpAuth](../README.md#httpAuth)

### HTTP request headers

 - **Content-Type**: application/json
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

# **put_v2_resources**
> str put_v2_resources(body, knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9, x_knora_accept_schema=x_knora_accept_schema, var_schema=var_schema, x_knora_json_ld_rendering=x_knora_json_ld_rendering, markup=markup, x_knora_accept_markup=x_knora_accept_markup)

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
    api_instance = openapi_client.V2ResourcesApi(api_client)
    body = 'body_example' # str | 
    knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9 = 'knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9_example' # str |  (optional)
    x_knora_accept_schema = 'x_knora_accept_schema_example' # str | The ontology schema to be used for the request. If not specified, the default schema ApiV2Complex will be used. (optional)
    var_schema = 'var_schema_example' # str | The ontology schema to be used for the request. If not specified, the default schema ApiV2Complex will be used. (optional)
    x_knora_json_ld_rendering = 'x_knora_json_ld_rendering_example' # str | The JSON-LD rendering to be used for the request (flat or hierarchical). If not specified, hierarchical JSON-LD will be used. (optional)
    markup = 'markup_example' # str | The markup rendering to be used for the request (XML or standoff). (optional)
    x_knora_accept_markup = 'x_knora_accept_markup_example' # str | The markup rendering to be used for the request (XML or standoff). (optional)

    try:
        api_response = api_instance.put_v2_resources(body, knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9, x_knora_accept_schema=x_knora_accept_schema, var_schema=var_schema, x_knora_json_ld_rendering=x_knora_json_ld_rendering, markup=markup, x_knora_accept_markup=x_knora_accept_markup)
        print("The response of V2ResourcesApi->put_v2_resources:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling V2ResourcesApi->put_v2_resources: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | **str**|  | 
 **knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9** | **str**|  | [optional] 
 **x_knora_accept_schema** | **str**| The ontology schema to be used for the request. If not specified, the default schema ApiV2Complex will be used. | [optional] 
 **var_schema** | **str**| The ontology schema to be used for the request. If not specified, the default schema ApiV2Complex will be used. | [optional] 
 **x_knora_json_ld_rendering** | **str**| The JSON-LD rendering to be used for the request (flat or hierarchical). If not specified, hierarchical JSON-LD will be used. | [optional] 
 **markup** | **str**| The markup rendering to be used for the request (XML or standoff). | [optional] 
 **x_knora_accept_markup** | **str**| The markup rendering to be used for the request (XML or standoff). | [optional] 

### Return type

**str**

### Authorization

[httpAuth1](../README.md#httpAuth1), [httpAuth](../README.md#httpAuth)

### HTTP request headers

 - **Content-Type**: application/json
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

