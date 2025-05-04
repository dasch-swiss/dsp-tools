# openapi_client.V2ValuesApi

All URIs are relative to *https://api.dasch.swiss:443*

Method | HTTP request | Description
------------- | ------------- | -------------
[**get_v2_values_resourceiri_valueuuid**](V2ValuesApi.md#get_v2_values_resourceiri_valueuuid) | **GET** /v2/values/{resourceIri}/{valueUuid} | 
[**post_v2_values**](V2ValuesApi.md#post_v2_values) | **POST** /v2/values | 
[**post_v2_values_delete**](V2ValuesApi.md#post_v2_values_delete) | **POST** /v2/values/delete | 
[**put_v2_values**](V2ValuesApi.md#put_v2_values) | **PUT** /v2/values | 


# **get_v2_values_resourceiri_valueuuid**
> str get_v2_values_resourceiri_valueuuid(resource_iri, value_uuid, knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9, version=version, x_knora_accept_schema=x_knora_accept_schema, var_schema=var_schema, x_knora_json_ld_rendering=x_knora_json_ld_rendering, markup=markup, x_knora_accept_markup=x_knora_accept_markup)

Find detailed documentation on <a href="https://docs.dasch.swiss/latest/DSP-API/03-endpoints/api-v2/editing-values/">docs.dasch.swiss</a>.

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
    api_instance = openapi_client.V2ValuesApi(api_client)
    resource_iri = 'resource_iri_example' # str | The IRI of a Resource.
    value_uuid = 'value_uuid_example' # str | The UUID of a Value.
    knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9 = 'knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9_example' # str |  (optional)
    version = 'version_example' # str |  (optional)
    x_knora_accept_schema = 'x_knora_accept_schema_example' # str | The ontology schema to be used for the request. If not specified, the default schema ApiV2Complex will be used. (optional)
    var_schema = 'var_schema_example' # str | The ontology schema to be used for the request. If not specified, the default schema ApiV2Complex will be used. (optional)
    x_knora_json_ld_rendering = 'x_knora_json_ld_rendering_example' # str | The JSON-LD rendering to be used for the request (flat or hierarchical). If not specified, hierarchical JSON-LD will be used. (optional)
    markup = 'markup_example' # str | The markup rendering to be used for the request (XML or standoff). (optional)
    x_knora_accept_markup = 'x_knora_accept_markup_example' # str | The markup rendering to be used for the request (XML or standoff). (optional)

    try:
        api_response = api_instance.get_v2_values_resourceiri_valueuuid(resource_iri, value_uuid, knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9, version=version, x_knora_accept_schema=x_knora_accept_schema, var_schema=var_schema, x_knora_json_ld_rendering=x_knora_json_ld_rendering, markup=markup, x_knora_accept_markup=x_knora_accept_markup)
        print("The response of V2ValuesApi->get_v2_values_resourceiri_valueuuid:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling V2ValuesApi->get_v2_values_resourceiri_valueuuid: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **resource_iri** | **str**| The IRI of a Resource. | 
 **value_uuid** | **str**| The UUID of a Value. | 
 **knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9** | **str**|  | [optional] 
 **version** | **str**|  | [optional] 
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
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** |  |  * Content-Type -  <br>  |
**400** |  |  -  |
**401** |  |  -  |
**403** |  |  -  |
**404** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **post_v2_values**
> str post_v2_values(body, knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9)

Find detailed documentation on <a href="https://docs.dasch.swiss/latest/DSP-API/03-endpoints/api-v2/editing-values/">docs.dasch.swiss</a>.

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
    api_instance = openapi_client.V2ValuesApi(api_client)
    body = {"@id":"http://rdfh.ch/0001/a-thing","@type":"anything:Thing","anything:hasInteger":{"@type":"knora-api:IntValue","knora-api:intValueAsInt":4},"@context":{"knora-api":"http://api.knora.org/ontology/knora-api/v2#","anything":"http://0.0.0.0:3333/ontology/0001/anything/v2#"}} # str | 
    knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9 = 'knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9_example' # str |  (optional)

    try:
        api_response = api_instance.post_v2_values(body, knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9)
        print("The response of V2ValuesApi->post_v2_values:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling V2ValuesApi->post_v2_values: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | **str**|  | 
 **knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9** | **str**|  | [optional] 

### Return type

**str**

### Authorization

[httpAuth1](../README.md#httpAuth1), [httpAuth](../README.md#httpAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** |  |  * Content-Type -  <br>  |
**400** |  |  -  |
**401** |  |  -  |
**403** |  |  -  |
**404** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **post_v2_values_delete**
> str post_v2_values_delete(body, knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9)

Find detailed documentation on <a href="https://docs.dasch.swiss/latest/DSP-API/03-endpoints/api-v2/editing-values/">docs.dasch.swiss</a>.

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
    api_instance = openapi_client.V2ValuesApi(api_client)
    body = {"@id":"http://rdfh.ch/0001/a-thing","@type":"anything:Thing","anything:hasInteger":{"@id":"http://rdfh.ch/0001/a-thing/values/vp96riPIRnmQcbMhgpv_Rg","@type":"knora-api:IntValue","knora-api:deleteComment":"This value was created by mistake."},"@context":{"knora-api":"http://api.knora.org/ontology/knora-api/v2#","anything":"http://0.0.0.0:3333/ontology/0001/anything/v2#"}} # str | 
    knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9 = 'knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9_example' # str |  (optional)

    try:
        api_response = api_instance.post_v2_values_delete(body, knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9)
        print("The response of V2ValuesApi->post_v2_values_delete:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling V2ValuesApi->post_v2_values_delete: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | **str**|  | 
 **knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9** | **str**|  | [optional] 

### Return type

**str**

### Authorization

[httpAuth1](../README.md#httpAuth1), [httpAuth](../README.md#httpAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** |  |  * Content-Type -  <br>  |
**400** |  |  -  |
**401** |  |  -  |
**403** |  |  -  |
**404** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **put_v2_values**
> str put_v2_values(body, knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9)

Find detailed documentation on <a href="https://docs.dasch.swiss/latest/DSP-API/03-endpoints/api-v2/editing-values/">docs.dasch.swiss</a>.

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
    api_instance = openapi_client.V2ValuesApi(api_client)
    body = {"@id":"http://rdfh.ch/0001/a-thing","@type":"anything:Thing","anything:hasInteger":{"@id":"http://rdfh.ch/0001/a-thing/values/vp96riPIRnmQcbMhgpv_Rg","@type":"knora-api:IntValue","knora-api:intValueAsInt":5},"@context":{"knora-api":"http://api.knora.org/ontology/knora-api/v2#","anything":"http://0.0.0.0:3333/ontology/0001/anything/v2#"}} # str | 
    knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9 = 'knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9_example' # str |  (optional)

    try:
        api_response = api_instance.put_v2_values(body, knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9)
        print("The response of V2ValuesApi->put_v2_values:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling V2ValuesApi->put_v2_values: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | **str**|  | 
 **knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9** | **str**|  | [optional] 

### Return type

**str**

### Authorization

[httpAuth1](../README.md#httpAuth1), [httpAuth](../README.md#httpAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** |  |  * Content-Type -  <br>  |
**400** |  |  -  |
**401** |  |  -  |
**403** |  |  -  |
**404** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

