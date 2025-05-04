# NodeADM


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**nodeinfo** | [**ListChildNodeInfoADM**](ListChildNodeInfoADM.md) |  | 
**children** | [**List[ListChildNodeADM]**](ListChildNodeADM.md) |  | [optional] 

## Example

```python
from openapi_client.models.node_adm import NodeADM

# TODO update the JSON string below
json = "{}"
# create an instance of NodeADM from a JSON string
node_adm_instance = NodeADM.from_json(json)
# print the JSON string representation of the object
print(NodeADM.to_json())

# convert the object into a dict
node_adm_dict = node_adm_instance.to_dict()
# create an instance of NodeADM from a dict
node_adm_from_dict = NodeADM.from_dict(node_adm_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


