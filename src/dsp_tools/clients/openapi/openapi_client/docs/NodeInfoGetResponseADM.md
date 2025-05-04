# NodeInfoGetResponseADM


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**nodeinfo** | [**ListChildNodeInfoADM**](ListChildNodeInfoADM.md) |  | 
**listinfo** | [**ListRootNodeInfoADM**](ListRootNodeInfoADM.md) |  | 

## Example

```python
from openapi_client.models.node_info_get_response_adm import NodeInfoGetResponseADM

# TODO update the JSON string below
json = "{}"
# create an instance of NodeInfoGetResponseADM from a JSON string
node_info_get_response_adm_instance = NodeInfoGetResponseADM.from_json(json)
# print the JSON string representation of the object
print(NodeInfoGetResponseADM.to_json())

# convert the object into a dict
node_info_get_response_adm_dict = node_info_get_response_adm_instance.to_dict()
# create an instance of NodeInfoGetResponseADM from a dict
node_info_get_response_adm_from_dict = NodeInfoGetResponseADM.from_dict(node_info_get_response_adm_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


