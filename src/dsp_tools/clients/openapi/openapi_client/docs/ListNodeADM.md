# ListNodeADM


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
**project_iri** | **str** |  | 
**is_root_node** | **bool** |  | 

## Example

```python
from openapi_client.models.list_node_adm import ListNodeADM

# TODO update the JSON string below
json = "{}"
# create an instance of ListNodeADM from a JSON string
list_node_adm_instance = ListNodeADM.from_json(json)
# print the JSON string representation of the object
print(ListNodeADM.to_json())

# convert the object into a dict
list_node_adm_dict = list_node_adm_instance.to_dict()
# create an instance of ListNodeADM from a dict
list_node_adm_from_dict = ListNodeADM.from_dict(list_node_adm_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


