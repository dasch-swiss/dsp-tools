# ResourceInfoDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**resource_iri** | **str** |  | 
**creation_date** | **datetime** |  | 
**last_modification_date** | **datetime** |  | 
**delete_date** | **datetime** |  | [optional] 
**is_deleted** | **bool** |  | 

## Example

```python
from openapi_client.models.resource_info_dto import ResourceInfoDto

# TODO update the JSON string below
json = "{}"
# create an instance of ResourceInfoDto from a JSON string
resource_info_dto_instance = ResourceInfoDto.from_json(json)
# print the JSON string representation of the object
print(ResourceInfoDto.to_json())

# convert the object into a dict
resource_info_dto_dict = resource_info_dto_instance.to_dict()
# create an instance of ResourceInfoDto from a dict
resource_info_dto_from_dict = ResourceInfoDto.from_dict(resource_info_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


