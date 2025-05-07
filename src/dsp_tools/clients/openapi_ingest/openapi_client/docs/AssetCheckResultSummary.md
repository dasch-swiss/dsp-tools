# AssetCheckResultSummary


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**number_of_assets** | **int** |  | 
**number_of_files** | **int** |  | 
**number_of_checksum_matches** | **int** |  | 

## Example

```python
from openapi_client.models.asset_check_result_summary import AssetCheckResultSummary

# TODO update the JSON string below
json = "{}"
# create an instance of AssetCheckResultSummary from a JSON string
asset_check_result_summary_instance = AssetCheckResultSummary.from_json(json)
# print the JSON string representation of the object
print(AssetCheckResultSummary.to_json())

# convert the object into a dict
asset_check_result_summary_dict = asset_check_result_summary_instance.to_dict()
# create an instance of AssetCheckResultSummary from a dict
asset_check_result_summary_from_dict = AssetCheckResultSummary.from_dict(asset_check_result_summary_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


