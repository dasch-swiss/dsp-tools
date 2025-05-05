# AssetCheckResultEntry


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**asset_id** | **str** |  | 
**original_filename** | **str** |  | 
**results** | [**List[SingleFileCheckResultResponse]**](SingleFileCheckResultResponse.md) |  | [optional] 

## Example

```python
from openapi_client.models.asset_check_result_entry import AssetCheckResultEntry

# TODO update the JSON string below
json = "{}"
# create an instance of AssetCheckResultEntry from a JSON string
asset_check_result_entry_instance = AssetCheckResultEntry.from_json(json)
# print the JSON string representation of the object
print(AssetCheckResultEntry.to_json())

# convert the object into a dict
asset_check_result_entry_dict = asset_check_result_entry_instance.to_dict()
# create an instance of AssetCheckResultEntry from a dict
asset_check_result_entry_from_dict = AssetCheckResultEntry.from_dict(asset_check_result_entry_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


