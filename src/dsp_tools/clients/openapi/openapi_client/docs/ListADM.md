# ListADM


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**listinfo** | [**ListRootNodeInfoADM**](ListRootNodeInfoADM.md) |  | 
**children** | [**List[ListChildNodeADM]**](ListChildNodeADM.md) |  | [optional] 

## Example

```python
from openapi_client.models.list_adm import ListADM

# TODO update the JSON string below
json = "{}"
# create an instance of ListADM from a JSON string
list_adm_instance = ListADM.from_json(json)
# print the JSON string representation of the object
print(ListADM.to_json())

# convert the object into a dict
list_adm_dict = list_adm_instance.to_dict()
# create an instance of ListADM from a dict
list_adm_from_dict = ListADM.from_dict(list_adm_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


