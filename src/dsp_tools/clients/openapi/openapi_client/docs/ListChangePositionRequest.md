# ListChangePositionRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**position** | [**Position**](Position.md) |  | 
**parent_node_iri** | [**ListIri**](ListIri.md) |  | 

## Example

```python
from openapi_client.models.list_change_position_request import ListChangePositionRequest

# TODO update the JSON string below
json = "{}"
# create an instance of ListChangePositionRequest from a JSON string
list_change_position_request_instance = ListChangePositionRequest.from_json(json)
# print the JSON string representation of the object
print(ListChangePositionRequest.to_json())

# convert the object into a dict
list_change_position_request_dict = list_change_position_request_instance.to_dict()
# create an instance of ListChangePositionRequest from a dict
list_change_position_request_from_dict = ListChangePositionRequest.from_dict(list_change_position_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


