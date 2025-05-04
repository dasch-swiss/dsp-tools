# openapi_client.V2OntologiesApi

All URIs are relative to *https://api.dasch.swiss:443*

Method | HTTP request | Description
------------- | ------------- | -------------
[**delete_v2_ontologies_classes_comment_resourceclassiri**](V2OntologiesApi.md#delete_v2_ontologies_classes_comment_resourceclassiri) | **DELETE** /v2/ontologies/classes/comment/{resourceClassIri} | 
[**delete_v2_ontologies_classes_resourceclassiri**](V2OntologiesApi.md#delete_v2_ontologies_classes_resourceclassiri) | **DELETE** /v2/ontologies/classes/{resourceClassIri} | 
[**delete_v2_ontologies_comment_ontologyiri**](V2OntologiesApi.md#delete_v2_ontologies_comment_ontologyiri) | **DELETE** /v2/ontologies/comment/{ontologyIri} | 
[**delete_v2_ontologies_ontologyiri**](V2OntologiesApi.md#delete_v2_ontologies_ontologyiri) | **DELETE** /v2/ontologies/{ontologyIri} | 
[**delete_v2_ontologies_properties_comment_propertyiri**](V2OntologiesApi.md#delete_v2_ontologies_properties_comment_propertyiri) | **DELETE** /v2/ontologies/properties/comment/{propertyIri} | 
[**delete_v2_ontologies_properties_propertyiri**](V2OntologiesApi.md#delete_v2_ontologies_properties_propertyiri) | **DELETE** /v2/ontologies/properties/{propertyIri} | 
[**get_ontology**](V2OntologiesApi.md#get_ontology) | **GET** /ontology | 
[**get_v2_ontologies_allentities_ontologyiri**](V2OntologiesApi.md#get_v2_ontologies_allentities_ontologyiri) | **GET** /v2/ontologies/allentities/{ontologyIri} | 
[**get_v2_ontologies_candeleteclass_resourceclassiri**](V2OntologiesApi.md#get_v2_ontologies_candeleteclass_resourceclassiri) | **GET** /v2/ontologies/candeleteclass/{resourceClassIri} | 
[**get_v2_ontologies_candeleteontology_ontologyiri**](V2OntologiesApi.md#get_v2_ontologies_candeleteontology_ontologyiri) | **GET** /v2/ontologies/candeleteontology/{ontologyIri} | 
[**get_v2_ontologies_canreplacecardinalities_resourceclassiri**](V2OntologiesApi.md#get_v2_ontologies_canreplacecardinalities_resourceclassiri) | **GET** /v2/ontologies/canreplacecardinalities/{resourceClassIri} | 
[**get_v2_ontologies_classes**](V2OntologiesApi.md#get_v2_ontologies_classes) | **GET** /v2/ontologies/classes | 
[**get_v2_ontologies_metadata**](V2OntologiesApi.md#get_v2_ontologies_metadata) | **GET** /v2/ontologies/metadata | 
[**get_v2_ontologies_properties**](V2OntologiesApi.md#get_v2_ontologies_properties) | **GET** /v2/ontologies/properties | 
[**patch_v2_ontologies_cardinalities**](V2OntologiesApi.md#patch_v2_ontologies_cardinalities) | **PATCH** /v2/ontologies/cardinalities | 
[**post_v2_ontologies**](V2OntologiesApi.md#post_v2_ontologies) | **POST** /v2/ontologies | 
[**post_v2_ontologies_candeletecardinalities**](V2OntologiesApi.md#post_v2_ontologies_candeletecardinalities) | **POST** /v2/ontologies/candeletecardinalities | 
[**post_v2_ontologies_cardinalities**](V2OntologiesApi.md#post_v2_ontologies_cardinalities) | **POST** /v2/ontologies/cardinalities | 
[**post_v2_ontologies_classes**](V2OntologiesApi.md#post_v2_ontologies_classes) | **POST** /v2/ontologies/classes | 
[**post_v2_ontologies_properties**](V2OntologiesApi.md#post_v2_ontologies_properties) | **POST** /v2/ontologies/properties | 
[**put_v2_ontologies_cardinalities**](V2OntologiesApi.md#put_v2_ontologies_cardinalities) | **PUT** /v2/ontologies/cardinalities | 
[**put_v2_ontologies_classes**](V2OntologiesApi.md#put_v2_ontologies_classes) | **PUT** /v2/ontologies/classes | 
[**put_v2_ontologies_guiorder**](V2OntologiesApi.md#put_v2_ontologies_guiorder) | **PUT** /v2/ontologies/guiorder | 
[**put_v2_ontologies_metadata**](V2OntologiesApi.md#put_v2_ontologies_metadata) | **PUT** /v2/ontologies/metadata | 
[**put_v2_ontologies_properties**](V2OntologiesApi.md#put_v2_ontologies_properties) | **PUT** /v2/ontologies/properties | 
[**put_v2_ontologies_properties_guielement**](V2OntologiesApi.md#put_v2_ontologies_properties_guielement) | **PUT** /v2/ontologies/properties/guielement | 


# **delete_v2_ontologies_classes_comment_resourceclassiri**
> str delete_v2_ontologies_classes_comment_resourceclassiri(resource_class_iri, last_modification_date, knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9, x_knora_accept_schema=x_knora_accept_schema, var_schema=var_schema, x_knora_json_ld_rendering=x_knora_json_ld_rendering, markup=markup, x_knora_accept_markup=x_knora_accept_markup)

Delete the comment of a class definition.

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
    api_instance = openapi_client.V2OntologiesApi(api_client)
    resource_class_iri = 'resource_class_iri_example' # str | 
    last_modification_date = 'last_modification_date_example' # str | 
    knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9 = 'knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9_example' # str |  (optional)
    x_knora_accept_schema = 'x_knora_accept_schema_example' # str | The ontology schema to be used for the request. If not specified, the default schema ApiV2Complex will be used. (optional)
    var_schema = 'var_schema_example' # str | The ontology schema to be used for the request. If not specified, the default schema ApiV2Complex will be used. (optional)
    x_knora_json_ld_rendering = 'x_knora_json_ld_rendering_example' # str | The JSON-LD rendering to be used for the request (flat or hierarchical). If not specified, hierarchical JSON-LD will be used. (optional)
    markup = 'markup_example' # str | The markup rendering to be used for the request (XML or standoff). (optional)
    x_knora_accept_markup = 'x_knora_accept_markup_example' # str | The markup rendering to be used for the request (XML or standoff). (optional)

    try:
        api_response = api_instance.delete_v2_ontologies_classes_comment_resourceclassiri(resource_class_iri, last_modification_date, knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9, x_knora_accept_schema=x_knora_accept_schema, var_schema=var_schema, x_knora_json_ld_rendering=x_knora_json_ld_rendering, markup=markup, x_knora_accept_markup=x_knora_accept_markup)
        print("The response of V2OntologiesApi->delete_v2_ontologies_classes_comment_resourceclassiri:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling V2OntologiesApi->delete_v2_ontologies_classes_comment_resourceclassiri: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **resource_class_iri** | **str**|  | 
 **last_modification_date** | **str**|  | 
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

# **delete_v2_ontologies_classes_resourceclassiri**
> str delete_v2_ontologies_classes_resourceclassiri(resource_class_iri, last_modification_date, knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9, x_knora_accept_schema=x_knora_accept_schema, var_schema=var_schema, x_knora_json_ld_rendering=x_knora_json_ld_rendering, markup=markup, x_knora_accept_markup=x_knora_accept_markup)

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
    api_instance = openapi_client.V2OntologiesApi(api_client)
    resource_class_iri = 'resource_class_iri_example' # str | 
    last_modification_date = 'last_modification_date_example' # str | 
    knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9 = 'knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9_example' # str |  (optional)
    x_knora_accept_schema = 'x_knora_accept_schema_example' # str | The ontology schema to be used for the request. If not specified, the default schema ApiV2Complex will be used. (optional)
    var_schema = 'var_schema_example' # str | The ontology schema to be used for the request. If not specified, the default schema ApiV2Complex will be used. (optional)
    x_knora_json_ld_rendering = 'x_knora_json_ld_rendering_example' # str | The JSON-LD rendering to be used for the request (flat or hierarchical). If not specified, hierarchical JSON-LD will be used. (optional)
    markup = 'markup_example' # str | The markup rendering to be used for the request (XML or standoff). (optional)
    x_knora_accept_markup = 'x_knora_accept_markup_example' # str | The markup rendering to be used for the request (XML or standoff). (optional)

    try:
        api_response = api_instance.delete_v2_ontologies_classes_resourceclassiri(resource_class_iri, last_modification_date, knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9, x_knora_accept_schema=x_knora_accept_schema, var_schema=var_schema, x_knora_json_ld_rendering=x_knora_json_ld_rendering, markup=markup, x_knora_accept_markup=x_knora_accept_markup)
        print("The response of V2OntologiesApi->delete_v2_ontologies_classes_resourceclassiri:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling V2OntologiesApi->delete_v2_ontologies_classes_resourceclassiri: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **resource_class_iri** | **str**|  | 
 **last_modification_date** | **str**|  | 
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

# **delete_v2_ontologies_comment_ontologyiri**
> str delete_v2_ontologies_comment_ontologyiri(ontology_iri, last_modification_date, knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9, x_knora_accept_schema=x_knora_accept_schema, var_schema=var_schema, x_knora_json_ld_rendering=x_knora_json_ld_rendering, markup=markup, x_knora_accept_markup=x_knora_accept_markup)

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
    api_instance = openapi_client.V2OntologiesApi(api_client)
    ontology_iri = 'ontology_iri_example' # str | 
    last_modification_date = 'last_modification_date_example' # str | 
    knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9 = 'knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9_example' # str |  (optional)
    x_knora_accept_schema = 'x_knora_accept_schema_example' # str | The ontology schema to be used for the request. If not specified, the default schema ApiV2Complex will be used. (optional)
    var_schema = 'var_schema_example' # str | The ontology schema to be used for the request. If not specified, the default schema ApiV2Complex will be used. (optional)
    x_knora_json_ld_rendering = 'x_knora_json_ld_rendering_example' # str | The JSON-LD rendering to be used for the request (flat or hierarchical). If not specified, hierarchical JSON-LD will be used. (optional)
    markup = 'markup_example' # str | The markup rendering to be used for the request (XML or standoff). (optional)
    x_knora_accept_markup = 'x_knora_accept_markup_example' # str | The markup rendering to be used for the request (XML or standoff). (optional)

    try:
        api_response = api_instance.delete_v2_ontologies_comment_ontologyiri(ontology_iri, last_modification_date, knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9, x_knora_accept_schema=x_knora_accept_schema, var_schema=var_schema, x_knora_json_ld_rendering=x_knora_json_ld_rendering, markup=markup, x_knora_accept_markup=x_knora_accept_markup)
        print("The response of V2OntologiesApi->delete_v2_ontologies_comment_ontologyiri:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling V2OntologiesApi->delete_v2_ontologies_comment_ontologyiri: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **ontology_iri** | **str**|  | 
 **last_modification_date** | **str**|  | 
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

# **delete_v2_ontologies_ontologyiri**
> str delete_v2_ontologies_ontologyiri(ontology_iri, last_modification_date, knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9, x_knora_accept_schema=x_knora_accept_schema, var_schema=var_schema, x_knora_json_ld_rendering=x_knora_json_ld_rendering, markup=markup, x_knora_accept_markup=x_knora_accept_markup)

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
    api_instance = openapi_client.V2OntologiesApi(api_client)
    ontology_iri = 'ontology_iri_example' # str | 
    last_modification_date = 'last_modification_date_example' # str | 
    knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9 = 'knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9_example' # str |  (optional)
    x_knora_accept_schema = 'x_knora_accept_schema_example' # str | The ontology schema to be used for the request. If not specified, the default schema ApiV2Complex will be used. (optional)
    var_schema = 'var_schema_example' # str | The ontology schema to be used for the request. If not specified, the default schema ApiV2Complex will be used. (optional)
    x_knora_json_ld_rendering = 'x_knora_json_ld_rendering_example' # str | The JSON-LD rendering to be used for the request (flat or hierarchical). If not specified, hierarchical JSON-LD will be used. (optional)
    markup = 'markup_example' # str | The markup rendering to be used for the request (XML or standoff). (optional)
    x_knora_accept_markup = 'x_knora_accept_markup_example' # str | The markup rendering to be used for the request (XML or standoff). (optional)

    try:
        api_response = api_instance.delete_v2_ontologies_ontologyiri(ontology_iri, last_modification_date, knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9, x_knora_accept_schema=x_knora_accept_schema, var_schema=var_schema, x_knora_json_ld_rendering=x_knora_json_ld_rendering, markup=markup, x_knora_accept_markup=x_knora_accept_markup)
        print("The response of V2OntologiesApi->delete_v2_ontologies_ontologyiri:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling V2OntologiesApi->delete_v2_ontologies_ontologyiri: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **ontology_iri** | **str**|  | 
 **last_modification_date** | **str**|  | 
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

# **delete_v2_ontologies_properties_comment_propertyiri**
> str delete_v2_ontologies_properties_comment_propertyiri(property_iri, last_modification_date, knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9, x_knora_accept_schema=x_knora_accept_schema, var_schema=var_schema, x_knora_json_ld_rendering=x_knora_json_ld_rendering, markup=markup, x_knora_accept_markup=x_knora_accept_markup)

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
    api_instance = openapi_client.V2OntologiesApi(api_client)
    property_iri = 'property_iri_example' # str | 
    last_modification_date = 'last_modification_date_example' # str | 
    knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9 = 'knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9_example' # str |  (optional)
    x_knora_accept_schema = 'x_knora_accept_schema_example' # str | The ontology schema to be used for the request. If not specified, the default schema ApiV2Complex will be used. (optional)
    var_schema = 'var_schema_example' # str | The ontology schema to be used for the request. If not specified, the default schema ApiV2Complex will be used. (optional)
    x_knora_json_ld_rendering = 'x_knora_json_ld_rendering_example' # str | The JSON-LD rendering to be used for the request (flat or hierarchical). If not specified, hierarchical JSON-LD will be used. (optional)
    markup = 'markup_example' # str | The markup rendering to be used for the request (XML or standoff). (optional)
    x_knora_accept_markup = 'x_knora_accept_markup_example' # str | The markup rendering to be used for the request (XML or standoff). (optional)

    try:
        api_response = api_instance.delete_v2_ontologies_properties_comment_propertyiri(property_iri, last_modification_date, knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9, x_knora_accept_schema=x_knora_accept_schema, var_schema=var_schema, x_knora_json_ld_rendering=x_knora_json_ld_rendering, markup=markup, x_knora_accept_markup=x_knora_accept_markup)
        print("The response of V2OntologiesApi->delete_v2_ontologies_properties_comment_propertyiri:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling V2OntologiesApi->delete_v2_ontologies_properties_comment_propertyiri: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **property_iri** | **str**|  | 
 **last_modification_date** | **str**|  | 
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

# **delete_v2_ontologies_properties_propertyiri**
> str delete_v2_ontologies_properties_propertyiri(property_iri, last_modification_date, knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9, x_knora_accept_schema=x_knora_accept_schema, var_schema=var_schema, x_knora_json_ld_rendering=x_knora_json_ld_rendering, markup=markup, x_knora_accept_markup=x_knora_accept_markup)

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
    api_instance = openapi_client.V2OntologiesApi(api_client)
    property_iri = 'property_iri_example' # str | 
    last_modification_date = 'last_modification_date_example' # str | 
    knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9 = 'knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9_example' # str |  (optional)
    x_knora_accept_schema = 'x_knora_accept_schema_example' # str | The ontology schema to be used for the request. If not specified, the default schema ApiV2Complex will be used. (optional)
    var_schema = 'var_schema_example' # str | The ontology schema to be used for the request. If not specified, the default schema ApiV2Complex will be used. (optional)
    x_knora_json_ld_rendering = 'x_knora_json_ld_rendering_example' # str | The JSON-LD rendering to be used for the request (flat or hierarchical). If not specified, hierarchical JSON-LD will be used. (optional)
    markup = 'markup_example' # str | The markup rendering to be used for the request (XML or standoff). (optional)
    x_knora_accept_markup = 'x_knora_accept_markup_example' # str | The markup rendering to be used for the request (XML or standoff). (optional)

    try:
        api_response = api_instance.delete_v2_ontologies_properties_propertyiri(property_iri, last_modification_date, knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9, x_knora_accept_schema=x_knora_accept_schema, var_schema=var_schema, x_knora_json_ld_rendering=x_knora_json_ld_rendering, markup=markup, x_knora_accept_markup=x_knora_accept_markup)
        print("The response of V2OntologiesApi->delete_v2_ontologies_properties_propertyiri:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling V2OntologiesApi->delete_v2_ontologies_properties_propertyiri: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **property_iri** | **str**|  | 
 **last_modification_date** | **str**|  | 
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

# **get_ontology**
> str get_ontology(knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9, all_languages=all_languages, x_knora_accept_schema=x_knora_accept_schema, var_schema=var_schema, x_knora_json_ld_rendering=x_knora_json_ld_rendering, markup=markup, x_knora_accept_markup=x_knora_accept_markup)

This is the route used to dereference an actual ontology IRI. If the URL path looks like it belongs to a built-in API ontology (which has to contain "knora-api"), prefix it with http://api.knora.org to get the ontology IRI. Otherwise, if it looks like it belongs to a project-specific API ontology, prefix it with routeData.appConfig.externalOntologyIriHostAndPort to get the ontology IRI.

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
    api_instance = openapi_client.V2OntologiesApi(api_client)
    knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9 = 'knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9_example' # str |  (optional)
    all_languages = False # bool |  (optional) (default to False)
    x_knora_accept_schema = 'x_knora_accept_schema_example' # str | The ontology schema to be used for the request. If not specified, the default schema ApiV2Complex will be used. (optional)
    var_schema = 'var_schema_example' # str | The ontology schema to be used for the request. If not specified, the default schema ApiV2Complex will be used. (optional)
    x_knora_json_ld_rendering = 'x_knora_json_ld_rendering_example' # str | The JSON-LD rendering to be used for the request (flat or hierarchical). If not specified, hierarchical JSON-LD will be used. (optional)
    markup = 'markup_example' # str | The markup rendering to be used for the request (XML or standoff). (optional)
    x_knora_accept_markup = 'x_knora_accept_markup_example' # str | The markup rendering to be used for the request (XML or standoff). (optional)

    try:
        api_response = api_instance.get_ontology(knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9, all_languages=all_languages, x_knora_accept_schema=x_knora_accept_schema, var_schema=var_schema, x_knora_json_ld_rendering=x_knora_json_ld_rendering, markup=markup, x_knora_accept_markup=x_knora_accept_markup)
        print("The response of V2OntologiesApi->get_ontology:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling V2OntologiesApi->get_ontology: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9** | **str**|  | [optional] 
 **all_languages** | **bool**|  | [optional] [default to False]
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

# **get_v2_ontologies_allentities_ontologyiri**
> str get_v2_ontologies_allentities_ontologyiri(ontology_iri, knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9, all_languages=all_languages, x_knora_accept_schema=x_knora_accept_schema, var_schema=var_schema, x_knora_json_ld_rendering=x_knora_json_ld_rendering, markup=markup, x_knora_accept_markup=x_knora_accept_markup)

Get all entities of an ontology

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
    api_instance = openapi_client.V2OntologiesApi(api_client)
    ontology_iri = 'ontology_iri_example' # str | 
    knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9 = 'knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9_example' # str |  (optional)
    all_languages = False # bool |  (optional) (default to False)
    x_knora_accept_schema = 'x_knora_accept_schema_example' # str | The ontology schema to be used for the request. If not specified, the default schema ApiV2Complex will be used. (optional)
    var_schema = 'var_schema_example' # str | The ontology schema to be used for the request. If not specified, the default schema ApiV2Complex will be used. (optional)
    x_knora_json_ld_rendering = 'x_knora_json_ld_rendering_example' # str | The JSON-LD rendering to be used for the request (flat or hierarchical). If not specified, hierarchical JSON-LD will be used. (optional)
    markup = 'markup_example' # str | The markup rendering to be used for the request (XML or standoff). (optional)
    x_knora_accept_markup = 'x_knora_accept_markup_example' # str | The markup rendering to be used for the request (XML or standoff). (optional)

    try:
        api_response = api_instance.get_v2_ontologies_allentities_ontologyiri(ontology_iri, knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9, all_languages=all_languages, x_knora_accept_schema=x_knora_accept_schema, var_schema=var_schema, x_knora_json_ld_rendering=x_knora_json_ld_rendering, markup=markup, x_knora_accept_markup=x_knora_accept_markup)
        print("The response of V2OntologiesApi->get_v2_ontologies_allentities_ontologyiri:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling V2OntologiesApi->get_v2_ontologies_allentities_ontologyiri: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **ontology_iri** | **str**|  | 
 **knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9** | **str**|  | [optional] 
 **all_languages** | **bool**|  | [optional] [default to False]
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

# **get_v2_ontologies_candeleteclass_resourceclassiri**
> str get_v2_ontologies_candeleteclass_resourceclassiri(resource_class_iri, knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9, x_knora_accept_schema=x_knora_accept_schema, var_schema=var_schema, x_knora_json_ld_rendering=x_knora_json_ld_rendering, markup=markup, x_knora_accept_markup=x_knora_accept_markup)

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
    api_instance = openapi_client.V2OntologiesApi(api_client)
    resource_class_iri = 'resource_class_iri_example' # str | 
    knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9 = 'knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9_example' # str |  (optional)
    x_knora_accept_schema = 'x_knora_accept_schema_example' # str | The ontology schema to be used for the request. If not specified, the default schema ApiV2Complex will be used. (optional)
    var_schema = 'var_schema_example' # str | The ontology schema to be used for the request. If not specified, the default schema ApiV2Complex will be used. (optional)
    x_knora_json_ld_rendering = 'x_knora_json_ld_rendering_example' # str | The JSON-LD rendering to be used for the request (flat or hierarchical). If not specified, hierarchical JSON-LD will be used. (optional)
    markup = 'markup_example' # str | The markup rendering to be used for the request (XML or standoff). (optional)
    x_knora_accept_markup = 'x_knora_accept_markup_example' # str | The markup rendering to be used for the request (XML or standoff). (optional)

    try:
        api_response = api_instance.get_v2_ontologies_candeleteclass_resourceclassiri(resource_class_iri, knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9, x_knora_accept_schema=x_knora_accept_schema, var_schema=var_schema, x_knora_json_ld_rendering=x_knora_json_ld_rendering, markup=markup, x_knora_accept_markup=x_knora_accept_markup)
        print("The response of V2OntologiesApi->get_v2_ontologies_candeleteclass_resourceclassiri:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling V2OntologiesApi->get_v2_ontologies_candeleteclass_resourceclassiri: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **resource_class_iri** | **str**|  | 
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

# **get_v2_ontologies_candeleteontology_ontologyiri**
> str get_v2_ontologies_candeleteontology_ontologyiri(ontology_iri, knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9, x_knora_accept_schema=x_knora_accept_schema, var_schema=var_schema, x_knora_json_ld_rendering=x_knora_json_ld_rendering, markup=markup, x_knora_accept_markup=x_knora_accept_markup)

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
    api_instance = openapi_client.V2OntologiesApi(api_client)
    ontology_iri = 'ontology_iri_example' # str | 
    knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9 = 'knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9_example' # str |  (optional)
    x_knora_accept_schema = 'x_knora_accept_schema_example' # str | The ontology schema to be used for the request. If not specified, the default schema ApiV2Complex will be used. (optional)
    var_schema = 'var_schema_example' # str | The ontology schema to be used for the request. If not specified, the default schema ApiV2Complex will be used. (optional)
    x_knora_json_ld_rendering = 'x_knora_json_ld_rendering_example' # str | The JSON-LD rendering to be used for the request (flat or hierarchical). If not specified, hierarchical JSON-LD will be used. (optional)
    markup = 'markup_example' # str | The markup rendering to be used for the request (XML or standoff). (optional)
    x_knora_accept_markup = 'x_knora_accept_markup_example' # str | The markup rendering to be used for the request (XML or standoff). (optional)

    try:
        api_response = api_instance.get_v2_ontologies_candeleteontology_ontologyiri(ontology_iri, knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9, x_knora_accept_schema=x_knora_accept_schema, var_schema=var_schema, x_knora_json_ld_rendering=x_knora_json_ld_rendering, markup=markup, x_knora_accept_markup=x_knora_accept_markup)
        print("The response of V2OntologiesApi->get_v2_ontologies_candeleteontology_ontologyiri:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling V2OntologiesApi->get_v2_ontologies_candeleteontology_ontologyiri: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **ontology_iri** | **str**|  | 
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

# **get_v2_ontologies_canreplacecardinalities_resourceclassiri**
> str get_v2_ontologies_canreplacecardinalities_resourceclassiri(resource_class_iri, knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9, property_iri=property_iri, new_cardinality=new_cardinality, x_knora_accept_schema=x_knora_accept_schema, var_schema=var_schema, x_knora_json_ld_rendering=x_knora_json_ld_rendering, markup=markup, x_knora_accept_markup=x_knora_accept_markup)

If only a class IRI is provided, this endpoint checks if any cardinality of any of the class properties can be replaced. If a property IRI and a new cardinality are provided, it checks if the cardinality can be set for the property on the specific class. Fails if not both a property IRI and a new cardinality is provided. Fails if the user does not have write access to the ontology of the class.

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
    api_instance = openapi_client.V2OntologiesApi(api_client)
    resource_class_iri = 'resource_class_iri_example' # str | 
    knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9 = 'knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9_example' # str |  (optional)
    property_iri = 'property_iri_example' # str |  (optional)
    new_cardinality = '1-n' # str | The new cardinality to be set for the property, must be provided when propertyIri is given. Valid values are: 1-n, 1, 0-n, 0-1 (optional)
    x_knora_accept_schema = 'x_knora_accept_schema_example' # str | The ontology schema to be used for the request. If not specified, the default schema ApiV2Complex will be used. (optional)
    var_schema = 'var_schema_example' # str | The ontology schema to be used for the request. If not specified, the default schema ApiV2Complex will be used. (optional)
    x_knora_json_ld_rendering = 'x_knora_json_ld_rendering_example' # str | The JSON-LD rendering to be used for the request (flat or hierarchical). If not specified, hierarchical JSON-LD will be used. (optional)
    markup = 'markup_example' # str | The markup rendering to be used for the request (XML or standoff). (optional)
    x_knora_accept_markup = 'x_knora_accept_markup_example' # str | The markup rendering to be used for the request (XML or standoff). (optional)

    try:
        api_response = api_instance.get_v2_ontologies_canreplacecardinalities_resourceclassiri(resource_class_iri, knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9, property_iri=property_iri, new_cardinality=new_cardinality, x_knora_accept_schema=x_knora_accept_schema, var_schema=var_schema, x_knora_json_ld_rendering=x_knora_json_ld_rendering, markup=markup, x_knora_accept_markup=x_knora_accept_markup)
        print("The response of V2OntologiesApi->get_v2_ontologies_canreplacecardinalities_resourceclassiri:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling V2OntologiesApi->get_v2_ontologies_canreplacecardinalities_resourceclassiri: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **resource_class_iri** | **str**|  | 
 **knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9** | **str**|  | [optional] 
 **property_iri** | **str**|  | [optional] 
 **new_cardinality** | **str**| The new cardinality to be set for the property, must be provided when propertyIri is given. Valid values are: 1-n, 1, 0-n, 0-1 | [optional] 
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

# **get_v2_ontologies_classes**
> str get_v2_ontologies_classes(knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9, all_languages=all_languages, x_knora_accept_schema=x_knora_accept_schema, var_schema=var_schema, x_knora_json_ld_rendering=x_knora_json_ld_rendering, markup=markup, x_knora_accept_markup=x_knora_accept_markup)

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
    api_instance = openapi_client.V2OntologiesApi(api_client)
    knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9 = 'knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9_example' # str |  (optional)
    all_languages = False # bool |  (optional) (default to False)
    x_knora_accept_schema = 'x_knora_accept_schema_example' # str | The ontology schema to be used for the request. If not specified, the default schema ApiV2Complex will be used. (optional)
    var_schema = 'var_schema_example' # str | The ontology schema to be used for the request. If not specified, the default schema ApiV2Complex will be used. (optional)
    x_knora_json_ld_rendering = 'x_knora_json_ld_rendering_example' # str | The JSON-LD rendering to be used for the request (flat or hierarchical). If not specified, hierarchical JSON-LD will be used. (optional)
    markup = 'markup_example' # str | The markup rendering to be used for the request (XML or standoff). (optional)
    x_knora_accept_markup = 'x_knora_accept_markup_example' # str | The markup rendering to be used for the request (XML or standoff). (optional)

    try:
        api_response = api_instance.get_v2_ontologies_classes(knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9, all_languages=all_languages, x_knora_accept_schema=x_knora_accept_schema, var_schema=var_schema, x_knora_json_ld_rendering=x_knora_json_ld_rendering, markup=markup, x_knora_accept_markup=x_knora_accept_markup)
        print("The response of V2OntologiesApi->get_v2_ontologies_classes:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling V2OntologiesApi->get_v2_ontologies_classes: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9** | **str**|  | [optional] 
 **all_languages** | **bool**|  | [optional] [default to False]
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

# **get_v2_ontologies_metadata**
> str get_v2_ontologies_metadata(x_knora_accept_project=x_knora_accept_project, x_knora_accept_schema=x_knora_accept_schema, var_schema=var_schema, x_knora_json_ld_rendering=x_knora_json_ld_rendering, markup=markup, x_knora_accept_markup=x_knora_accept_markup)

Get the metadata of an ontology

### Example


```python
import openapi_client
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
    api_instance = openapi_client.V2OntologiesApi(api_client)
    x_knora_accept_project = 'x_knora_accept_project_example' # str |  (optional)
    x_knora_accept_schema = 'x_knora_accept_schema_example' # str | The ontology schema to be used for the request. If not specified, the default schema ApiV2Complex will be used. (optional)
    var_schema = 'var_schema_example' # str | The ontology schema to be used for the request. If not specified, the default schema ApiV2Complex will be used. (optional)
    x_knora_json_ld_rendering = 'x_knora_json_ld_rendering_example' # str | The JSON-LD rendering to be used for the request (flat or hierarchical). If not specified, hierarchical JSON-LD will be used. (optional)
    markup = 'markup_example' # str | The markup rendering to be used for the request (XML or standoff). (optional)
    x_knora_accept_markup = 'x_knora_accept_markup_example' # str | The markup rendering to be used for the request (XML or standoff). (optional)

    try:
        api_response = api_instance.get_v2_ontologies_metadata(x_knora_accept_project=x_knora_accept_project, x_knora_accept_schema=x_knora_accept_schema, var_schema=var_schema, x_knora_json_ld_rendering=x_knora_json_ld_rendering, markup=markup, x_knora_accept_markup=x_knora_accept_markup)
        print("The response of V2OntologiesApi->get_v2_ontologies_metadata:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling V2OntologiesApi->get_v2_ontologies_metadata: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **x_knora_accept_project** | **str**|  | [optional] 
 **x_knora_accept_schema** | **str**| The ontology schema to be used for the request. If not specified, the default schema ApiV2Complex will be used. | [optional] 
 **var_schema** | **str**| The ontology schema to be used for the request. If not specified, the default schema ApiV2Complex will be used. | [optional] 
 **x_knora_json_ld_rendering** | **str**| The JSON-LD rendering to be used for the request (flat or hierarchical). If not specified, hierarchical JSON-LD will be used. | [optional] 
 **markup** | **str**| The markup rendering to be used for the request (XML or standoff). | [optional] 
 **x_knora_accept_markup** | **str**| The markup rendering to be used for the request (XML or standoff). | [optional] 

### Return type

**str**

### Authorization

No authorization required

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

# **get_v2_ontologies_properties**
> str get_v2_ontologies_properties(knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9, all_languages=all_languages, x_knora_accept_schema=x_knora_accept_schema, var_schema=var_schema, x_knora_json_ld_rendering=x_knora_json_ld_rendering, markup=markup, x_knora_accept_markup=x_knora_accept_markup)

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
    api_instance = openapi_client.V2OntologiesApi(api_client)
    knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9 = 'knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9_example' # str |  (optional)
    all_languages = False # bool |  (optional) (default to False)
    x_knora_accept_schema = 'x_knora_accept_schema_example' # str | The ontology schema to be used for the request. If not specified, the default schema ApiV2Complex will be used. (optional)
    var_schema = 'var_schema_example' # str | The ontology schema to be used for the request. If not specified, the default schema ApiV2Complex will be used. (optional)
    x_knora_json_ld_rendering = 'x_knora_json_ld_rendering_example' # str | The JSON-LD rendering to be used for the request (flat or hierarchical). If not specified, hierarchical JSON-LD will be used. (optional)
    markup = 'markup_example' # str | The markup rendering to be used for the request (XML or standoff). (optional)
    x_knora_accept_markup = 'x_knora_accept_markup_example' # str | The markup rendering to be used for the request (XML or standoff). (optional)

    try:
        api_response = api_instance.get_v2_ontologies_properties(knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9, all_languages=all_languages, x_knora_accept_schema=x_knora_accept_schema, var_schema=var_schema, x_knora_json_ld_rendering=x_knora_json_ld_rendering, markup=markup, x_knora_accept_markup=x_knora_accept_markup)
        print("The response of V2OntologiesApi->get_v2_ontologies_properties:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling V2OntologiesApi->get_v2_ontologies_properties: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9** | **str**|  | [optional] 
 **all_languages** | **bool**|  | [optional] [default to False]
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

# **patch_v2_ontologies_cardinalities**
> str patch_v2_ontologies_cardinalities(body, knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9, x_knora_accept_schema=x_knora_accept_schema, var_schema=var_schema, x_knora_json_ld_rendering=x_knora_json_ld_rendering, markup=markup, x_knora_accept_markup=x_knora_accept_markup)

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
    api_instance = openapi_client.V2OntologiesApi(api_client)
    body = 'body_example' # str | 
    knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9 = 'knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9_example' # str |  (optional)
    x_knora_accept_schema = 'x_knora_accept_schema_example' # str | The ontology schema to be used for the request. If not specified, the default schema ApiV2Complex will be used. (optional)
    var_schema = 'var_schema_example' # str | The ontology schema to be used for the request. If not specified, the default schema ApiV2Complex will be used. (optional)
    x_knora_json_ld_rendering = 'x_knora_json_ld_rendering_example' # str | The JSON-LD rendering to be used for the request (flat or hierarchical). If not specified, hierarchical JSON-LD will be used. (optional)
    markup = 'markup_example' # str | The markup rendering to be used for the request (XML or standoff). (optional)
    x_knora_accept_markup = 'x_knora_accept_markup_example' # str | The markup rendering to be used for the request (XML or standoff). (optional)

    try:
        api_response = api_instance.patch_v2_ontologies_cardinalities(body, knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9, x_knora_accept_schema=x_knora_accept_schema, var_schema=var_schema, x_knora_json_ld_rendering=x_knora_json_ld_rendering, markup=markup, x_knora_accept_markup=x_knora_accept_markup)
        print("The response of V2OntologiesApi->patch_v2_ontologies_cardinalities:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling V2OntologiesApi->patch_v2_ontologies_cardinalities: %s\n" % e)
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

# **post_v2_ontologies**
> str post_v2_ontologies(body, knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9, x_knora_accept_schema=x_knora_accept_schema, var_schema=var_schema, x_knora_json_ld_rendering=x_knora_json_ld_rendering, markup=markup, x_knora_accept_markup=x_knora_accept_markup)

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
    api_instance = openapi_client.V2OntologiesApi(api_client)
    body = 'body_example' # str | 
    knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9 = 'knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9_example' # str |  (optional)
    x_knora_accept_schema = 'x_knora_accept_schema_example' # str | The ontology schema to be used for the request. If not specified, the default schema ApiV2Complex will be used. (optional)
    var_schema = 'var_schema_example' # str | The ontology schema to be used for the request. If not specified, the default schema ApiV2Complex will be used. (optional)
    x_knora_json_ld_rendering = 'x_knora_json_ld_rendering_example' # str | The JSON-LD rendering to be used for the request (flat or hierarchical). If not specified, hierarchical JSON-LD will be used. (optional)
    markup = 'markup_example' # str | The markup rendering to be used for the request (XML or standoff). (optional)
    x_knora_accept_markup = 'x_knora_accept_markup_example' # str | The markup rendering to be used for the request (XML or standoff). (optional)

    try:
        api_response = api_instance.post_v2_ontologies(body, knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9, x_knora_accept_schema=x_knora_accept_schema, var_schema=var_schema, x_knora_json_ld_rendering=x_knora_json_ld_rendering, markup=markup, x_knora_accept_markup=x_knora_accept_markup)
        print("The response of V2OntologiesApi->post_v2_ontologies:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling V2OntologiesApi->post_v2_ontologies: %s\n" % e)
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

# **post_v2_ontologies_candeletecardinalities**
> str post_v2_ontologies_candeletecardinalities(body, knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9, x_knora_accept_schema=x_knora_accept_schema, var_schema=var_schema, x_knora_json_ld_rendering=x_knora_json_ld_rendering, markup=markup, x_knora_accept_markup=x_knora_accept_markup)

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
    api_instance = openapi_client.V2OntologiesApi(api_client)
    body = 'body_example' # str | 
    knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9 = 'knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9_example' # str |  (optional)
    x_knora_accept_schema = 'x_knora_accept_schema_example' # str | The ontology schema to be used for the request. If not specified, the default schema ApiV2Complex will be used. (optional)
    var_schema = 'var_schema_example' # str | The ontology schema to be used for the request. If not specified, the default schema ApiV2Complex will be used. (optional)
    x_knora_json_ld_rendering = 'x_knora_json_ld_rendering_example' # str | The JSON-LD rendering to be used for the request (flat or hierarchical). If not specified, hierarchical JSON-LD will be used. (optional)
    markup = 'markup_example' # str | The markup rendering to be used for the request (XML or standoff). (optional)
    x_knora_accept_markup = 'x_knora_accept_markup_example' # str | The markup rendering to be used for the request (XML or standoff). (optional)

    try:
        api_response = api_instance.post_v2_ontologies_candeletecardinalities(body, knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9, x_knora_accept_schema=x_knora_accept_schema, var_schema=var_schema, x_knora_json_ld_rendering=x_knora_json_ld_rendering, markup=markup, x_knora_accept_markup=x_knora_accept_markup)
        print("The response of V2OntologiesApi->post_v2_ontologies_candeletecardinalities:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling V2OntologiesApi->post_v2_ontologies_candeletecardinalities: %s\n" % e)
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

# **post_v2_ontologies_cardinalities**
> str post_v2_ontologies_cardinalities(body, knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9, x_knora_accept_schema=x_knora_accept_schema, var_schema=var_schema, x_knora_json_ld_rendering=x_knora_json_ld_rendering, markup=markup, x_knora_accept_markup=x_knora_accept_markup)

Add cardinalities to a class. For more info check out the <a href="https://docs.dasch.swiss/knora-api-v2/ontologies.html#add-cardinalities-to-a-class">documentation</a>.

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
    api_instance = openapi_client.V2OntologiesApi(api_client)
    body = 'body_example' # str | 
    knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9 = 'knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9_example' # str |  (optional)
    x_knora_accept_schema = 'x_knora_accept_schema_example' # str | The ontology schema to be used for the request. If not specified, the default schema ApiV2Complex will be used. (optional)
    var_schema = 'var_schema_example' # str | The ontology schema to be used for the request. If not specified, the default schema ApiV2Complex will be used. (optional)
    x_knora_json_ld_rendering = 'x_knora_json_ld_rendering_example' # str | The JSON-LD rendering to be used for the request (flat or hierarchical). If not specified, hierarchical JSON-LD will be used. (optional)
    markup = 'markup_example' # str | The markup rendering to be used for the request (XML or standoff). (optional)
    x_knora_accept_markup = 'x_knora_accept_markup_example' # str | The markup rendering to be used for the request (XML or standoff). (optional)

    try:
        api_response = api_instance.post_v2_ontologies_cardinalities(body, knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9, x_knora_accept_schema=x_knora_accept_schema, var_schema=var_schema, x_knora_json_ld_rendering=x_knora_json_ld_rendering, markup=markup, x_knora_accept_markup=x_knora_accept_markup)
        print("The response of V2OntologiesApi->post_v2_ontologies_cardinalities:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling V2OntologiesApi->post_v2_ontologies_cardinalities: %s\n" % e)
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

# **post_v2_ontologies_classes**
> str post_v2_ontologies_classes(body, knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9, x_knora_accept_schema=x_knora_accept_schema, var_schema=var_schema, x_knora_json_ld_rendering=x_knora_json_ld_rendering, markup=markup, x_knora_accept_markup=x_knora_accept_markup)

Create a new class

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
    api_instance = openapi_client.V2OntologiesApi(api_client)
    body = 'body_example' # str | 
    knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9 = 'knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9_example' # str |  (optional)
    x_knora_accept_schema = 'x_knora_accept_schema_example' # str | The ontology schema to be used for the request. If not specified, the default schema ApiV2Complex will be used. (optional)
    var_schema = 'var_schema_example' # str | The ontology schema to be used for the request. If not specified, the default schema ApiV2Complex will be used. (optional)
    x_knora_json_ld_rendering = 'x_knora_json_ld_rendering_example' # str | The JSON-LD rendering to be used for the request (flat or hierarchical). If not specified, hierarchical JSON-LD will be used. (optional)
    markup = 'markup_example' # str | The markup rendering to be used for the request (XML or standoff). (optional)
    x_knora_accept_markup = 'x_knora_accept_markup_example' # str | The markup rendering to be used for the request (XML or standoff). (optional)

    try:
        api_response = api_instance.post_v2_ontologies_classes(body, knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9, x_knora_accept_schema=x_knora_accept_schema, var_schema=var_schema, x_knora_json_ld_rendering=x_knora_json_ld_rendering, markup=markup, x_knora_accept_markup=x_knora_accept_markup)
        print("The response of V2OntologiesApi->post_v2_ontologies_classes:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling V2OntologiesApi->post_v2_ontologies_classes: %s\n" % e)
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

# **post_v2_ontologies_properties**
> str post_v2_ontologies_properties(body, knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9, x_knora_accept_schema=x_knora_accept_schema, var_schema=var_schema, x_knora_json_ld_rendering=x_knora_json_ld_rendering, markup=markup, x_knora_accept_markup=x_knora_accept_markup)

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
    api_instance = openapi_client.V2OntologiesApi(api_client)
    body = 'body_example' # str | 
    knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9 = 'knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9_example' # str |  (optional)
    x_knora_accept_schema = 'x_knora_accept_schema_example' # str | The ontology schema to be used for the request. If not specified, the default schema ApiV2Complex will be used. (optional)
    var_schema = 'var_schema_example' # str | The ontology schema to be used for the request. If not specified, the default schema ApiV2Complex will be used. (optional)
    x_knora_json_ld_rendering = 'x_knora_json_ld_rendering_example' # str | The JSON-LD rendering to be used for the request (flat or hierarchical). If not specified, hierarchical JSON-LD will be used. (optional)
    markup = 'markup_example' # str | The markup rendering to be used for the request (XML or standoff). (optional)
    x_knora_accept_markup = 'x_knora_accept_markup_example' # str | The markup rendering to be used for the request (XML or standoff). (optional)

    try:
        api_response = api_instance.post_v2_ontologies_properties(body, knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9, x_knora_accept_schema=x_knora_accept_schema, var_schema=var_schema, x_knora_json_ld_rendering=x_knora_json_ld_rendering, markup=markup, x_knora_accept_markup=x_knora_accept_markup)
        print("The response of V2OntologiesApi->post_v2_ontologies_properties:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling V2OntologiesApi->post_v2_ontologies_properties: %s\n" % e)
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

# **put_v2_ontologies_cardinalities**
> str put_v2_ontologies_cardinalities(body, knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9, x_knora_accept_schema=x_knora_accept_schema, var_schema=var_schema, x_knora_json_ld_rendering=x_knora_json_ld_rendering, markup=markup, x_knora_accept_markup=x_knora_accept_markup)

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
    api_instance = openapi_client.V2OntologiesApi(api_client)
    body = 'body_example' # str | 
    knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9 = 'knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9_example' # str |  (optional)
    x_knora_accept_schema = 'x_knora_accept_schema_example' # str | The ontology schema to be used for the request. If not specified, the default schema ApiV2Complex will be used. (optional)
    var_schema = 'var_schema_example' # str | The ontology schema to be used for the request. If not specified, the default schema ApiV2Complex will be used. (optional)
    x_knora_json_ld_rendering = 'x_knora_json_ld_rendering_example' # str | The JSON-LD rendering to be used for the request (flat or hierarchical). If not specified, hierarchical JSON-LD will be used. (optional)
    markup = 'markup_example' # str | The markup rendering to be used for the request (XML or standoff). (optional)
    x_knora_accept_markup = 'x_knora_accept_markup_example' # str | The markup rendering to be used for the request (XML or standoff). (optional)

    try:
        api_response = api_instance.put_v2_ontologies_cardinalities(body, knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9, x_knora_accept_schema=x_knora_accept_schema, var_schema=var_schema, x_knora_json_ld_rendering=x_knora_json_ld_rendering, markup=markup, x_knora_accept_markup=x_knora_accept_markup)
        print("The response of V2OntologiesApi->put_v2_ontologies_cardinalities:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling V2OntologiesApi->put_v2_ontologies_cardinalities: %s\n" % e)
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

# **put_v2_ontologies_classes**
> str put_v2_ontologies_classes(body, knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9, x_knora_accept_schema=x_knora_accept_schema, var_schema=var_schema, x_knora_json_ld_rendering=x_knora_json_ld_rendering, markup=markup, x_knora_accept_markup=x_knora_accept_markup)

Change the labels or comments of a class

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
    api_instance = openapi_client.V2OntologiesApi(api_client)
    body = 'body_example' # str | 
    knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9 = 'knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9_example' # str |  (optional)
    x_knora_accept_schema = 'x_knora_accept_schema_example' # str | The ontology schema to be used for the request. If not specified, the default schema ApiV2Complex will be used. (optional)
    var_schema = 'var_schema_example' # str | The ontology schema to be used for the request. If not specified, the default schema ApiV2Complex will be used. (optional)
    x_knora_json_ld_rendering = 'x_knora_json_ld_rendering_example' # str | The JSON-LD rendering to be used for the request (flat or hierarchical). If not specified, hierarchical JSON-LD will be used. (optional)
    markup = 'markup_example' # str | The markup rendering to be used for the request (XML or standoff). (optional)
    x_knora_accept_markup = 'x_knora_accept_markup_example' # str | The markup rendering to be used for the request (XML or standoff). (optional)

    try:
        api_response = api_instance.put_v2_ontologies_classes(body, knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9, x_knora_accept_schema=x_knora_accept_schema, var_schema=var_schema, x_knora_json_ld_rendering=x_knora_json_ld_rendering, markup=markup, x_knora_accept_markup=x_knora_accept_markup)
        print("The response of V2OntologiesApi->put_v2_ontologies_classes:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling V2OntologiesApi->put_v2_ontologies_classes: %s\n" % e)
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

# **put_v2_ontologies_guiorder**
> str put_v2_ontologies_guiorder(body, knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9, x_knora_accept_schema=x_knora_accept_schema, var_schema=var_schema, x_knora_json_ld_rendering=x_knora_json_ld_rendering, markup=markup, x_knora_accept_markup=x_knora_accept_markup)

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
    api_instance = openapi_client.V2OntologiesApi(api_client)
    body = 'body_example' # str | 
    knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9 = 'knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9_example' # str |  (optional)
    x_knora_accept_schema = 'x_knora_accept_schema_example' # str | The ontology schema to be used for the request. If not specified, the default schema ApiV2Complex will be used. (optional)
    var_schema = 'var_schema_example' # str | The ontology schema to be used for the request. If not specified, the default schema ApiV2Complex will be used. (optional)
    x_knora_json_ld_rendering = 'x_knora_json_ld_rendering_example' # str | The JSON-LD rendering to be used for the request (flat or hierarchical). If not specified, hierarchical JSON-LD will be used. (optional)
    markup = 'markup_example' # str | The markup rendering to be used for the request (XML or standoff). (optional)
    x_knora_accept_markup = 'x_knora_accept_markup_example' # str | The markup rendering to be used for the request (XML or standoff). (optional)

    try:
        api_response = api_instance.put_v2_ontologies_guiorder(body, knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9, x_knora_accept_schema=x_knora_accept_schema, var_schema=var_schema, x_knora_json_ld_rendering=x_knora_json_ld_rendering, markup=markup, x_knora_accept_markup=x_knora_accept_markup)
        print("The response of V2OntologiesApi->put_v2_ontologies_guiorder:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling V2OntologiesApi->put_v2_ontologies_guiorder: %s\n" % e)
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

# **put_v2_ontologies_metadata**
> str put_v2_ontologies_metadata(body, knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9, x_knora_accept_schema=x_knora_accept_schema, var_schema=var_schema, x_knora_json_ld_rendering=x_knora_json_ld_rendering, markup=markup, x_knora_accept_markup=x_knora_accept_markup)

Change the metadata of an ontology

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
    api_instance = openapi_client.V2OntologiesApi(api_client)
    body = 'body_example' # str | 
    knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9 = 'knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9_example' # str |  (optional)
    x_knora_accept_schema = 'x_knora_accept_schema_example' # str | The ontology schema to be used for the request. If not specified, the default schema ApiV2Complex will be used. (optional)
    var_schema = 'var_schema_example' # str | The ontology schema to be used for the request. If not specified, the default schema ApiV2Complex will be used. (optional)
    x_knora_json_ld_rendering = 'x_knora_json_ld_rendering_example' # str | The JSON-LD rendering to be used for the request (flat or hierarchical). If not specified, hierarchical JSON-LD will be used. (optional)
    markup = 'markup_example' # str | The markup rendering to be used for the request (XML or standoff). (optional)
    x_knora_accept_markup = 'x_knora_accept_markup_example' # str | The markup rendering to be used for the request (XML or standoff). (optional)

    try:
        api_response = api_instance.put_v2_ontologies_metadata(body, knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9, x_knora_accept_schema=x_knora_accept_schema, var_schema=var_schema, x_knora_json_ld_rendering=x_knora_json_ld_rendering, markup=markup, x_knora_accept_markup=x_knora_accept_markup)
        print("The response of V2OntologiesApi->put_v2_ontologies_metadata:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling V2OntologiesApi->put_v2_ontologies_metadata: %s\n" % e)
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

# **put_v2_ontologies_properties**
> str put_v2_ontologies_properties(body, knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9, x_knora_accept_schema=x_knora_accept_schema, var_schema=var_schema, x_knora_json_ld_rendering=x_knora_json_ld_rendering, markup=markup, x_knora_accept_markup=x_knora_accept_markup)

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
    api_instance = openapi_client.V2OntologiesApi(api_client)
    body = 'body_example' # str | 
    knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9 = 'knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9_example' # str |  (optional)
    x_knora_accept_schema = 'x_knora_accept_schema_example' # str | The ontology schema to be used for the request. If not specified, the default schema ApiV2Complex will be used. (optional)
    var_schema = 'var_schema_example' # str | The ontology schema to be used for the request. If not specified, the default schema ApiV2Complex will be used. (optional)
    x_knora_json_ld_rendering = 'x_knora_json_ld_rendering_example' # str | The JSON-LD rendering to be used for the request (flat or hierarchical). If not specified, hierarchical JSON-LD will be used. (optional)
    markup = 'markup_example' # str | The markup rendering to be used for the request (XML or standoff). (optional)
    x_knora_accept_markup = 'x_knora_accept_markup_example' # str | The markup rendering to be used for the request (XML or standoff). (optional)

    try:
        api_response = api_instance.put_v2_ontologies_properties(body, knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9, x_knora_accept_schema=x_knora_accept_schema, var_schema=var_schema, x_knora_json_ld_rendering=x_knora_json_ld_rendering, markup=markup, x_knora_accept_markup=x_knora_accept_markup)
        print("The response of V2OntologiesApi->put_v2_ontologies_properties:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling V2OntologiesApi->put_v2_ontologies_properties: %s\n" % e)
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

# **put_v2_ontologies_properties_guielement**
> str put_v2_ontologies_properties_guielement(body, knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9, x_knora_accept_schema=x_knora_accept_schema, var_schema=var_schema, x_knora_json_ld_rendering=x_knora_json_ld_rendering, markup=markup, x_knora_accept_markup=x_knora_accept_markup)

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
    api_instance = openapi_client.V2OntologiesApi(api_client)
    body = 'body_example' # str | 
    knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9 = 'knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9_example' # str |  (optional)
    x_knora_accept_schema = 'x_knora_accept_schema_example' # str | The ontology schema to be used for the request. If not specified, the default schema ApiV2Complex will be used. (optional)
    var_schema = 'var_schema_example' # str | The ontology schema to be used for the request. If not specified, the default schema ApiV2Complex will be used. (optional)
    x_knora_json_ld_rendering = 'x_knora_json_ld_rendering_example' # str | The JSON-LD rendering to be used for the request (flat or hierarchical). If not specified, hierarchical JSON-LD will be used. (optional)
    markup = 'markup_example' # str | The markup rendering to be used for the request (XML or standoff). (optional)
    x_knora_accept_markup = 'x_knora_accept_markup_example' # str | The markup rendering to be used for the request (XML or standoff). (optional)

    try:
        api_response = api_instance.put_v2_ontologies_properties_guielement(body, knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9, x_knora_accept_schema=x_knora_accept_schema, var_schema=var_schema, x_knora_json_ld_rendering=x_knora_json_ld_rendering, markup=markup, x_knora_accept_markup=x_knora_accept_markup)
        print("The response of V2OntologiesApi->put_v2_ontologies_properties_guielement:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling V2OntologiesApi->put_v2_ontologies_properties_guielement: %s\n" % e)
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

