# ListChangeRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**list_iri** | [**ListIri**](ListIri.md) |  | 
**project_iri** | [**ProjectIri**](ProjectIri.md) |  | 
**has_root_node** | [**ListIri**](ListIri.md) |  | [optional] 
**position** | [**Position**](Position.md) |  | [optional] 
**name** | [**ListName**](ListName.md) |  | [optional] 
**labels** | [**Labels**](Labels.md) |  | [optional] 
**comments** | [**Comments**](Comments.md) |  | [optional] 

## Example

```python
from openapi_client.models.list_change_request import ListChangeRequest

# TODO update the JSON string below
json = "{}"
# create an instance of ListChangeRequest from a JSON string
list_change_request_instance = ListChangeRequest.from_json(json)
# print the JSON string representation of the object
print(ListChangeRequest.to_json())

# convert the object into a dict
list_change_request_dict = list_change_request_instance.to_dict()
# create an instance of ListChangeRequest from a dict
list_change_request_from_dict = ListChangeRequest.from_dict(list_change_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


