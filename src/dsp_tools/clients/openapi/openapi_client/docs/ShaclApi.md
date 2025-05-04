# openapi_client.ShaclApi

All URIs are relative to *https://api.dasch.swiss:443*

Method | HTTP request | Description
------------- | ------------- | -------------
[**post_shacl_validate**](ShaclApi.md#post_shacl_validate) | **POST** /shacl/validate | 


# **post_shacl_validate**
> str post_shacl_validate(data_ttl, shacl_ttl, validate_shapes=validate_shapes, report_details=report_details, add_blank_nodes=add_blank_nodes)

foo

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
    api_instance = openapi_client.ShaclApi(api_client)
    data_ttl = None # bytearray | The data to be validated.
    shacl_ttl = None # bytearray | The shapes for validation.
    validate_shapes = True # bool | Should shapes also be validated. (optional)
    report_details = True # bool | Add `sh:details` to the validation report. (optional)
    add_blank_nodes = True # bool | Add blank nodes to the validation report. (optional)

    try:
        api_response = api_instance.post_shacl_validate(data_ttl, shacl_ttl, validate_shapes=validate_shapes, report_details=report_details, add_blank_nodes=add_blank_nodes)
        print("The response of ShaclApi->post_shacl_validate:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ShaclApi->post_shacl_validate: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **data_ttl** | **bytearray**| The data to be validated. | 
 **shacl_ttl** | **bytearray**| The shapes for validation. | 
 **validate_shapes** | **bool**| Should shapes also be validated. | [optional] 
 **report_details** | **bool**| Add &#x60;sh:details&#x60; to the validation report. | [optional] 
 **add_blank_nodes** | **bool**| Add blank nodes to the validation report. | [optional] 

### Return type

**str**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: multipart/form-data
 - **Accept**: text/turtle, application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** |  The validation report in Turtle format.  &#x60;&#x60;&#x60;turtle @prefix sh:      &lt;http://www.w3.org/ns/shacl#&gt; . @prefix rdf:     &lt;http://www.w3.org/1999/02/22-rdf-syntax-ns#&gt; .  [ rdf:type     sh:ValidationReport;   sh:conforms  true ] . &#x60;&#x60;&#x60;  |  -  |
**400** |  |  -  |
**401** |  |  -  |
**403** |  |  -  |
**404** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

