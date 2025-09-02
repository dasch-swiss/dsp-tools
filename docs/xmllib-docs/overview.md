# Using the `xmllib`

## Overview

The following code shows a minimal overview how you can use the `xmllib` to create an XML file for a mass import to DSP.

It does not show, nor detail all the available functions and features, 
but will give you links to the relevant and comprehensive documentation.

The core functionality that the `xmllib` provides you is as follows:

- Classes that will help you construct the resources and add values to it.
- Functions that help you clean and transform your input.
- Functions that help you validate your input.
- Configuration options such as Permissions.


We recommend you to create the import script for your data once your data model is relatively stable,
as the construction of the code is highly dependent on the data model.

## Code Example

Import the `xmllib`

```python
from dsp_tools import xmllib
```

### Creating the Root

The `XMLRoot` is the central element where you add all your resources.

See the [documentation](./xmlroot.md) for details.

```python
root = xmllib.XMLRoot.create_new(shortcode="0000", default_ontology="onto")
```

### Creating a Resource

Resources which were defined in the ontology JSON are created as follows.

See the [documentation](./resource.md) for details.

```python
resource = xmllib.Resource.create_new(
    res_id="general_resource",
    restype=":ResourceType",
    label="Title in the DSP-APP",
)
```

### Adding Values to a Resource

Once you created a `Resource` you can add values to it.
For each value type we provide three functionalities:

<!-- markdownlint-disable MD036 -->

**Adding one value**

```python
resource = resource.add_integer(prop_name=":hasInt", value=1)
```

**Adding multiple values**

```python
resource = resource.add_integer_multiple(prop_name=":hasInt", values=[1, 2, 3])
```

**Adding optional values**

With this function we check if the input is empty, if it is the resource is returned as is,
otherwise the value is added.

```python
resource = resource.add_integer_optional(prop_name=":hasInt", value=None)
```

See the [documentation](./resource.md) for all options.

<!-- markdownlint-enable MD036 -->

### Reformatting the Input With Conversion Functions

We provide a number of functions to help convert your input. For example DSP requires a special format for dates. 
[Reformat](https://docs.dasch.swiss/latest/DSP-TOOLS/xmllib-docs/value-converters/#xmllib.value_converters.reformat_date) 
your input into the correct format.

```python
formatted_date = xmllib.value_converters.reformat_date(
    date="10.1990-11.1990",
    date_precision_separator=".",
    date_range_separator="-",
    date_format=xmllib.DateFormat.DD_MM_YYYY,
)

resource = resource.add_date(prop_name=":hasDate", value=formatted_date)
```

Find further functions to convert values [here](./value-converters.md)


### Data Cleaning Functions

Oftentimes, similar data cleaning steps must be carried out again and again, before values can be added to the resource.
For example, many strings extracted from data sources represent not one value, but a list of values.
We provide the following function to clean your input:

```python
input_string = "This should be\na list\nof strings."
cleaned_list = xmllib.create_list_from_input(
    input_value=input_string,
    separator="\n"
)
```

You can find this and other functions to help you process your data [here](./general-functions.md).

Please contact us with a feature request if you need a function that doesn't exist yet in the `xmllib`, 
especially if you feel that it may be generic enough to be helpful for other users.

### Adding A File To a Resource

In the ontology you can 
[specify](../data-model/json-project/ontologies.md#resource-super) that a resource should have a file attached.

You can add a file to the resource with the following function.
Please note that only one file (or IIIF-URI, see below) is allowed per resource.

```python
image_resource = image_resource.add_file(
    filename="cat.tiff",
    license=xmllib.LicenseRecommended.CC.BY,
    copyright_holder="Mouse University",
    authorship=["Minnie Mouse"],
)
```

We require that legal information be provided for resources with files. 
While the copyright holder and authorships are free text fields,
the license must be chosen from a predefined set.
The recommended licenses are listed [here](./licenses/recommended.md),
and some others are listed [here](./licenses/other.md).

Please contact us if you required license is not available.

### Adding IIIF-URIs To a Resource

We provide the option to add a IIIF-URI to a Resource with the super-class `StillImageRepresentation`.
This way you can reference images that are hosted on other servers.

```python
resource = resource.add_iiif_uri(
    iiif_uri="https://iiif.wellcomecollection.org/image/b20432033_B0008608.JP2/full/1338%2C/0/default.jpg",
    license=xmllib.LicenseRecommended.CC.BY_NC,
    copyright_holder="Wellcome Collection",
    authorship=["Cavanagh, Annie"]
)
```

Please note that the IIIF-URI must follow the official syntax specified [here](https://iiif.io/api/image/3.0/#2-uri-syntax).

### Adding a Comment To a Value

It is possible to add a comment to individual values or files with the following parameter.

```python
resource = resource.add_integer(
    prop_name=":hasInt",
    value=1,
    comment="This text is a comment on this integer.",
)
```


### Specifying Permissions

We recommend to specify permissions on the [project level](../data-model/json-project/overview.md#default_permissions)
or on [individual classes and properties](../data-model/json-project/overview.md#default_permissions_overrule).

However, you can overrule the default permissions with the following designated parameter.

```python
image_resource = image_resource.add_simpletext(
    prop_name=":hasRemark",
    value="Text only visible for the project.",
    permissions=xmllib.Permissions.PRIVATE,
)
```

See the [documentation](permissions.md) for details.

### Adding a Resource To the Root

Once you have added all information to the resource, you can add the resource to the root.

```python
root = root.add_resource(resource)
```

Similarly to the values, we also provide the possibility to add multiple or optional resources to the root.

### Creating DSP-Base Resources

DSP has four additional resource types that can be used out of the box without defining them in the data model.

- [`AudioSegmentResource`](./dsp-base-resources/audio-segment-resource.md) and 
  [`VideoSegmentResource`](./dsp-base-resources/video-segment-resource.md) 
  are resources that can be used to annotate a segment of an audio or video file of another resource.
- [`RegionResource`](./dsp-base-resources/region-resource.md) describes a region of a resource with an image file.
- [`LinkResource`](./dsp-base-resources/link-resource.md) is a collection of links to other resources.

These four types have pre-defined properties, 
which either are added directly when the resource is created or can be added afterwards with a dedicated function.

```python
region = xmllib.RegionResource.create_new(
    res_id="region_1",
    label="Region label",
    region_of="image_resource"
)
region = region.add_rectangle(
    point1=(0.1, 0.1),
    point2=(0.2, 0.2),
)
```

Please consult the individual documentations (linked above) for details.

### Writing the File

Once you have added all data, you can write the XML file with the following function.

```python
root.write_file("data.xml")
```

## Validating Your Input

When your resources are created and data is added, the `xmllib` validates your input.
In the background we use the validation functions specified [here](./value-checkers.md), 
so there is no need to check your input manually.

Due to this, the `xmllib` may print a large amount of information on your terminal.
You can configure the warning level as described [here](./advanced-set-up.md#configure-warnings-level).

It is also possible to save the warnings into a csv file instead of the print message, 
see [here](./advanced-set-up.md#save-warnings-output-to-csv) for details.
