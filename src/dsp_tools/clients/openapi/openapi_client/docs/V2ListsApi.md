# openapi_client.V2ListsApi

All URIs are relative to *https://api.dasch.swiss:443*

Method | HTTP request | Description
------------- | ------------- | -------------
[**get_v2_lists_listiri**](V2ListsApi.md#get_v2_lists_listiri) | **GET** /v2/lists/{listIri} | 
[**get_v2_node_listiri**](V2ListsApi.md#get_v2_node_listiri) | **GET** /v2/node/{listIri} | 


# **get_v2_lists_listiri**
> str get_v2_lists_listiri(list_iri, knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9, x_knora_accept_schema=x_knora_accept_schema, var_schema=var_schema, x_knora_json_ld_rendering=x_knora_json_ld_rendering, markup=markup, x_knora_accept_markup=x_knora_accept_markup)

Returns a list (a graph with all list nodes).

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
    api_instance = openapi_client.V2ListsApi(api_client)
    list_iri = 'http://rdfh.ch/lists/0001/OF72eD8CTiqRXIOyX0zH0g' # str | The iri to a list.
    knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9 = 'knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9_example' # str |  (optional)
    x_knora_accept_schema = 'x_knora_accept_schema_example' # str | The ontology schema to be used for the request. If not specified, the default schema ApiV2Complex will be used. (optional)
    var_schema = 'var_schema_example' # str | The ontology schema to be used for the request. If not specified, the default schema ApiV2Complex will be used. (optional)
    x_knora_json_ld_rendering = 'x_knora_json_ld_rendering_example' # str | The JSON-LD rendering to be used for the request (flat or hierarchical). If not specified, hierarchical JSON-LD will be used. (optional)
    markup = 'markup_example' # str | The markup rendering to be used for the request (XML or standoff). (optional)
    x_knora_accept_markup = 'x_knora_accept_markup_example' # str | The markup rendering to be used for the request (XML or standoff). (optional)

    try:
        api_response = api_instance.get_v2_lists_listiri(list_iri, knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9, x_knora_accept_schema=x_knora_accept_schema, var_schema=var_schema, x_knora_json_ld_rendering=x_knora_json_ld_rendering, markup=markup, x_knora_accept_markup=x_knora_accept_markup)
        print("The response of V2ListsApi->get_v2_lists_listiri:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling V2ListsApi->get_v2_lists_listiri: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **list_iri** | **str**| The iri to a list. | 
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

# **get_v2_node_listiri**
> str get_v2_node_listiri(list_iri, knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9, x_knora_accept_schema=x_knora_accept_schema, var_schema=var_schema, x_knora_json_ld_rendering=x_knora_json_ld_rendering, markup=markup, x_knora_accept_markup=x_knora_accept_markup)

Returns a list node.

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
    api_instance = openapi_client.V2ListsApi(api_client)
    list_iri = 'http://rdfh.ch/lists/0001/OF72eD8CTiqRXIOyX0zH0g' # str | The iri to a list.
    knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9 = 'knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9_example' # str |  (optional)
    x_knora_accept_schema = 'x_knora_accept_schema_example' # str | The ontology schema to be used for the request. If not specified, the default schema ApiV2Complex will be used. (optional)
    var_schema = 'var_schema_example' # str | The ontology schema to be used for the request. If not specified, the default schema ApiV2Complex will be used. (optional)
    x_knora_json_ld_rendering = 'x_knora_json_ld_rendering_example' # str | The JSON-LD rendering to be used for the request (flat or hierarchical). If not specified, hierarchical JSON-LD will be used. (optional)
    markup = 'markup_example' # str | The markup rendering to be used for the request (XML or standoff). (optional)
    x_knora_accept_markup = 'x_knora_accept_markup_example' # str | The markup rendering to be used for the request (XML or standoff). (optional)

    try:
        api_response = api_instance.get_v2_node_listiri(list_iri, knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9, x_knora_accept_schema=x_knora_accept_schema, var_schema=var_schema, x_knora_json_ld_rendering=x_knora_json_ld_rendering, markup=markup, x_knora_accept_markup=x_knora_accept_markup)
        print("The response of V2ListsApi->get_v2_node_listiri:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling V2ListsApi->get_v2_node_listiri: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **list_iri** | **str**| The iri to a list. | 
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

