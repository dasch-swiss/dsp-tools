# ListItemDeleteResponseADM


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**node** | [**ListNodeADM**](ListNodeADM.md) |  | 
**iri** | **str** |  | 
**deleted** | **bool** |  | 

## Example

```python
from openapi_client.models.list_item_delete_response_adm import ListItemDeleteResponseADM

# TODO update the JSON string below
json = "{}"
# create an instance of ListItemDeleteResponseADM from a JSON string
list_item_delete_response_adm_instance = ListItemDeleteResponseADM.from_json(json)
# print the JSON string representation of the object
print(ListItemDeleteResponseADM.to_json())

# convert the object into a dict
list_item_delete_response_adm_dict = list_item_delete_response_adm_instance.to_dict()
# create an instance of ListItemDeleteResponseADM from a dict
list_item_delete_response_adm_from_dict = ListItemDeleteResponseADM.from_dict(list_item_delete_response_adm_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


