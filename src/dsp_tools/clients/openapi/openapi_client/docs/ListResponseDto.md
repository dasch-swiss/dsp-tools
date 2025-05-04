# ListResponseDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**resources** | [**List[ResourceInfoDto]**](ResourceInfoDto.md) |  | [optional] 
**count** | **int** |  | 

## Example

```python
from openapi_client.models.list_response_dto import ListResponseDto

# TODO update the JSON string below
json = "{}"
# create an instance of ListResponseDto from a JSON string
list_response_dto_instance = ListResponseDto.from_json(json)
# print the JSON string representation of the object
print(ListResponseDto.to_json())

# convert the object into a dict
list_response_dto_dict = list_response_dto_instance.to_dict()
# create an instance of ListResponseDto from a dict
list_response_dto_from_dict = ListResponseDto.from_dict(list_response_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


