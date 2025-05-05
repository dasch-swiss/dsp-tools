# AssetInfoResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**internal_filename** | **str** |  | 
**original_internal_filename** | **str** |  | 
**original_filename** | **str** |  | 
**checksum_original** | **str** |  | 
**checksum_derivative** | **str** |  | 
**width** | **int** |  | [optional] 
**height** | **int** |  | [optional] 
**duration** | **float** |  | [optional] 
**fps** | **float** |  | [optional] 
**internal_mime_type** | **str** |  | [optional] 
**original_mime_type** | **str** |  | [optional] 

## Example

```python
from openapi_client.models.asset_info_response import AssetInfoResponse

# TODO update the JSON string below
json = "{}"
# create an instance of AssetInfoResponse from a JSON string
asset_info_response_instance = AssetInfoResponse.from_json(json)
# print the JSON string representation of the object
print(AssetInfoResponse.to_json())

# convert the object into a dict
asset_info_response_dict = asset_info_response_instance.to_dict()
# create an instance of AssetInfoResponse from a dict
asset_info_response_from_dict = AssetInfoResponse.from_dict(asset_info_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


