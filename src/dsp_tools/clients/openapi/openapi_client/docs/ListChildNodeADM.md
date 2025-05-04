# ListChildNodeADM


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** |  | 
**name** | **str** |  | [optional] 
**labels** | [**StringLiteralSequenceV2**](StringLiteralSequenceV2.md) |  | 
**comments** | [**StringLiteralSequenceV2**](StringLiteralSequenceV2.md) |  | 
**position** | **int** |  | 
**has_root_node** | **str** |  | 
**children** | [**List[ListChildNodeADM]**](ListChildNodeADM.md) |  | [optional] 

## Example

```python
from openapi_client.models.list_child_node_adm import ListChildNodeADM

# TODO update the JSON string below
json = "{}"
# create an instance of ListChildNodeADM from a JSON string
list_child_node_adm_instance = ListChildNodeADM.from_json(json)
# print the JSON string representation of the object
print(ListChildNodeADM.to_json())

# convert the object into a dict
list_child_node_adm_dict = list_child_node_adm_instance.to_dict()
# create an instance of ListChildNodeADM from a dict
list_child_node_adm_from_dict = ListChildNodeADM.from_dict(list_child_node_adm_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


