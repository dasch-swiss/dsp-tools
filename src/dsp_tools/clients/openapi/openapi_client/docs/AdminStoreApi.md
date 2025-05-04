# openapi_client.AdminStoreApi

All URIs are relative to *https://api.dasch.swiss:443*

Method | HTTP request | Description
------------- | ------------- | -------------
[**get_admin_store_resettriplestorecontent**](AdminStoreApi.md#get_admin_store_resettriplestorecontent) | **GET** /admin/store/ResetTriplestoreContent | 


# **get_admin_store_resettriplestorecontent**
> MessageResponse get_admin_store_resettriplestorecontent(prepend_defaults=prepend_defaults, rdf_data_object=rdf_data_object)

Resets the content of the triplestore, only available if configuration `allowReloadOverHttp` is set to `true`.

### Example


```python
import openapi_client
from openapi_client.models.message_response import MessageResponse
from openapi_client.models.rdf_data_object import RdfDataObject
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
    api_instance = openapi_client.AdminStoreApi(api_client)
    prepend_defaults = True # bool | Prepend defaults to the data objects. (optional) (default to True)
    rdf_data_object = [openapi_client.RdfDataObject()] # List[RdfDataObject] | RDF data objects to load into the triplestore, uses defaults if not present. (optional)

    try:
        api_response = api_instance.get_admin_store_resettriplestorecontent(prepend_defaults=prepend_defaults, rdf_data_object=rdf_data_object)
        print("The response of AdminStoreApi->get_admin_store_resettriplestorecontent:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AdminStoreApi->get_admin_store_resettriplestorecontent: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **prepend_defaults** | **bool**| Prepend defaults to the data objects. | [optional] [default to True]
 **rdf_data_object** | [**List[RdfDataObject]**](RdfDataObject.md)| RDF data objects to load into the triplestore, uses defaults if not present. | [optional] 

### Return type

[**MessageResponse**](MessageResponse.md)

### Authorization

No authorization required

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

