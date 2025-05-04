# ListCreateRootNodeRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | [**ListIri**](ListIri.md) |  | [optional] 
**comments** | [**Comments**](Comments.md) |  | 
**labels** | [**Labels**](Labels.md) |  | 
**name** | [**ListName**](ListName.md) |  | [optional] 
**project_iri** | [**ProjectIri**](ProjectIri.md) |  | 

## Example

```python
from openapi_client.models.list_create_root_node_request import ListCreateRootNodeRequest

# TODO update the JSON string below
json = "{}"
# create an instance of ListCreateRootNodeRequest from a JSON string
list_create_root_node_request_instance = ListCreateRootNodeRequest.from_json(json)
# print the JSON string representation of the object
print(ListCreateRootNodeRequest.to_json())

# convert the object into a dict
list_create_root_node_request_dict = list_create_root_node_request_instance.to_dict()
# create an instance of ListCreateRootNodeRequest from a dict
list_create_root_node_request_from_dict = ListCreateRootNodeRequest.from_dict(list_create_root_node_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


