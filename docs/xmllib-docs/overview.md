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
    label="generic resource",
)
```