# InfoEndpointResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** |  | 
**version** | **str** |  | 
**scala_version** | **str** |  | 
**sbt_version** | **str** |  | 
**build_time** | **str** |  | 
**git_commit** | **str** |  | 

## Example

```python
from openapi_client.models.info_endpoint_response import InfoEndpointResponse

# TODO update the JSON string below
json = "{}"
# create an instance of InfoEndpointResponse from a JSON string
info_endpoint_response_instance = InfoEndpointResponse.from_json(json)
# print the JSON string representation of the object
print(InfoEndpointResponse.to_json())

# convert the object into a dict
info_endpoint_response_dict = info_endpoint_response_instance.to_dict()
# create an instance of InfoEndpointResponse from a dict
info_endpoint_response_from_dict = InfoEndpointResponse.from_dict(info_endpoint_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


