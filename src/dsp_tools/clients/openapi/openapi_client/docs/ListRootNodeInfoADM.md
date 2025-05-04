# ListRootNodeInfoADM


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** |  | 
**project_iri** | **str** |  | 
**name** | **str** |  | [optional] 
**labels** | [**StringLiteralSequenceV2**](StringLiteralSequenceV2.md) |  | 
**comments** | [**StringLiteralSequenceV2**](StringLiteralSequenceV2.md) |  | 
**is_root_node** | **bool** |  | 

## Example

```python
from openapi_client.models.list_root_node_info_adm import ListRootNodeInfoADM

# TODO update the JSON string below
json = "{}"
# create an instance of ListRootNodeInfoADM from a JSON string
list_root_node_info_adm_instance = ListRootNodeInfoADM.from_json(json)
# print the JSON string representation of the object
print(ListRootNodeInfoADM.to_json())

# convert the object into a dict
list_root_node_info_adm_dict = list_root_node_info_adm_instance.to_dict()
# create an instance of ListRootNodeInfoADM from a dict
list_root_node_info_adm_from_dict = ListRootNodeInfoADM.from_dict(list_root_node_info_adm_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


