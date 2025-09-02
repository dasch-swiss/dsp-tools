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

Import the `xmllib`

```python
from dsp_tools import xmllib
```

### Creating the Root

The `XMLRoot` is the central element where you add all your resources and provides serialisation functionality.

[See the documentation for details.](xmlroot.md)

```python
root = xmllib.XMLRoot.create_new(shortcode="0000", default_ontology="onto")
```

### Creating a Resource

Generic resources, that is any resources but the DSP-Base Resources are created as follows.

[See the documentation for details.](resource.md)

```python
resource = xmllib.Resource.create_new(
    res_id="general_resource",
    restype=":ResourceType",
    label="Title in the DSP-APP",
)
```

### Adding Values to a Resource

Once you created a `Resource` you can add values to it.
For each value type (apart from the boolean which has no multiple option) we provide three functionalities: 
adding the value, adding multiple values and adding optional values.

**Adding a value**

```python
resource = resource.add_integer(prop_name=":hasInt", value=1)
```

**Adding multiple values**

```python
resource = resource.add_integer_multiple(prop_name=":hasInt", values=[1, 2, 3])
```

**Adding optional values**

With this function we check if the input is empty, if it is the resource is returned as is otherwise the value is added.

```python
resource = resource.add_integer_optional(prop_name=":hasInt", value=None)
```

[See the documentation for details.](resource.md)


### Reformatting the Input With Conversion Functions

We provide a number of functions to help convert your input, for example DSP requires a special format for dates.
With a helper function you can [extract](https://docs.dasch.swiss/latest/DSP-TOOLS/xmllib-docs/general-functions/#xmllib.general_functions.find_dates_in_string) 
or [reformat](https://docs.dasch.swiss/latest/DSP-TOOLS/xmllib-docs/#xmllib.general_functions.reformat_date) your input into the correct format.

```python
import dsp_tools.xmllib.value_converters

formatted_date = dsp_tools.xmllib.value_converters.reformat_date(
    date="10.1990-11.1990",
    date_precision_separator=".",
    date_range_separator="-",
    date_format=xmllib.DateFormat.DD_MM_YYYY,
)

resource = resource.add_date(prop_name=":hasDate", value=formatted_date)
```

Find other functions to help you transform your input [here](value-converters.md) and [here](value-converters.md).

### Creating DSP-Base Resources

DSP has four additional resource types that can be used.

- [`AudioSegmentResource`](./dsp-base-resources/audio-segment-resource.md) and [`VideoSegmentResource`](./dsp-base-resources/video-segment-resource.md) are resources that can be used to annotate a segment of a Resource with an audio or video file.
- [`RegionResource`](./dsp-base-resources/region-resource.md) describes a region of a resource with a video file.
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


