# ListChangeNameRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | [**ListName**](ListName.md) |  | 

## Example

```python
from openapi_client.models.list_change_name_request import ListChangeNameRequest

# TODO update the JSON string below
json = "{}"
# create an instance of ListChangeNameRequest from a JSON string
list_change_name_request_instance = ListChangeNameRequest.from_json(json)
# print the JSON string representation of the object
print(ListChangeNameRequest.to_json())

# convert the object into a dict
list_change_name_request_dict = list_change_name_request_instance.to_dict()
# create an instance of ListChangeNameRequest from a dict
list_change_name_request_from_dict = ListChangeNameRequest.from_dict(list_change_name_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


