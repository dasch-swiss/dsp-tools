# RestrictedViewResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**size** | [**Size**](Size.md) |  | [optional] 
**watermark** | [**Watermark**](Watermark.md) |  | [optional] 

## Example

```python
from openapi_client.models.restricted_view_response import RestrictedViewResponse

# TODO update the JSON string below
json = "{}"
# create an instance of RestrictedViewResponse from a JSON string
restricted_view_response_instance = RestrictedViewResponse.from_json(json)
# print the JSON string representation of the object
print(RestrictedViewResponse.to_json())

# convert the object into a dict
restricted_view_response_dict = restricted_view_response_instance.to_dict()
# create an instance of RestrictedViewResponse from a dict
restricted_view_response_from_dict = RestrictedViewResponse.from_dict(restricted_view_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


