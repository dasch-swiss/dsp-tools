# ListNodeCommentsDeleteResponseADM


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**node_iri** | **str** |  | 
**comments_deleted** | **bool** |  | 

## Example

```python
from openapi_client.models.list_node_comments_delete_response_adm import ListNodeCommentsDeleteResponseADM

# TODO update the JSON string below
json = "{}"
# create an instance of ListNodeCommentsDeleteResponseADM from a JSON string
list_node_comments_delete_response_adm_instance = ListNodeCommentsDeleteResponseADM.from_json(json)
# print the JSON string representation of the object
print(ListNodeCommentsDeleteResponseADM.to_json())

# convert the object into a dict
list_node_comments_delete_response_adm_dict = list_node_comments_delete_response_adm_instance.to_dict()
# create an instance of ListNodeCommentsDeleteResponseADM from a dict
list_node_comments_delete_response_adm_from_dict = ListNodeCommentsDeleteResponseADM.from_dict(list_node_comments_delete_response_adm_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


