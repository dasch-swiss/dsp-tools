# SetRestrictedViewRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**size** | [**Size**](Size.md) |  | [optional] 
**watermark** | [**Watermark**](Watermark.md) |  | [optional] 

## Example

```python
from openapi_client.models.set_restricted_view_request import SetRestrictedViewRequest

# TODO update the JSON string below
json = "{}"
# create an instance of SetRestrictedViewRequest from a JSON string
set_restricted_view_request_instance = SetRestrictedViewRequest.from_json(json)
# print the JSON string representation of the object
print(SetRestrictedViewRequest.to_json())

# convert the object into a dict
set_restricted_view_request_dict = set_restricted_view_request_instance.to_dict()
# create an instance of SetRestrictedViewRequest from a dict
set_restricted_view_request_from_dict = SetRestrictedViewRequest.from_dict(set_restricted_view_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


