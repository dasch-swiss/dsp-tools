# Using the `xmllib`

## Overview

The following code shows a minimal overview how you can create an XML file for a mass import to DSP with the `xmllib`.

It does not show, nor detail all the available functions and features, 
but will give you links to the relevant and comprehensive documentation.

The core functionality that the `xmllib` provides you is as follows:

- Classes that will help you construct the resources and add values to it.
- Configuration options where the fields are not free text, such as Permissions
- Functions that help you validate your input.
- Functions that help you clean and transform your input.


## Code Example

```python
from dsp_tools import xmllib


# create the root with the project and ontology information
# look at: for details
root = xmllib.XMLRoot.create_new(shortcode="0000", default_ontology="onto")

# create a generic resource
resource = xmllib.Resource.create_new(
    res_id="general_resource",
    restype=":ResourceType",
    label="generic resource",
)

# look at the documentation to see all the options to add values
resource.add_integer(prop_name=":hasInt", value=1)

# find helper functions like these at:
formatted_date = xmllib.reformat_date(
    date="10.1990-11.1990",
    date_precision_separator=".",
    date_range_separator="-",
    date_format=xmllib.DateFormat.DD_MM_YYYY,
)
resource = resource.add_date(prop_name=":hasDate", value=formatted_date)

# when the resource is complete, add it to the root
root = root.add_resource(resource)

# create a resource with a file
image_resource = xmllib.Resource.create_new(
    res_id="image_resource",
    restype=":Image",
    label="Image resource",
)

# add a file with limited view
# see the options for licenses at:
image_resource = image_resource.add_file(
    filename="cat.tiff",
    license=xmllib.LicenseRecommended.CC.BY,
    copyright_holder="Mouse University",
    authorship=["Minnie Mouse"]
)

# add specific permissions to a value
image_resource = image_resource.add_simpletext(
    prop_name=":hasInternalComment",
    value="Comment not visible outside of the project",
    permissions=xmllib.Permissions.PRIVATE
)

# add the resource to the root
root.add_resource(image_resource)

# DSP-base resources are created with their designated class
region = xmllib.RegionResource.create_new(
    res_id="region_1",
    label="Region label",
    region_of="image_resource"
)
region = region.add_rectangle(
    point1=(0.1, 0.1),
    point2=(0.2, 0.2),
)

# add the resource to the root
root.add_resource(region)

# write the xml file
root.write_file("data.xml")
```