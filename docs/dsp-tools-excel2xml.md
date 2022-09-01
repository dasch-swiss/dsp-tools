[![PyPI version](https://badge.fury.io/py/dsp-tools.svg)](https://badge.fury.io/py/dsp-tools)

# `excel2xml`: Convert a data source to XML
dsp-tools assists you in converting a data source in CSV/XLS(X) format to an XML file. Unlike the other features of 
dsp-tools, this doesn't work via command line, but via helper methods that you can import into your own Python script. 
Because every data source is different, there is no single algorithm to convert them to a DSP conform XML. Every user 
has to deal with the specialties of his/her data source, but `excel2xml`'s helper methods can help a lot. This document 
demonstrates how it works. 

## How to use the module excel2xml
At the end of this document, you find a sample Python script. In the following, it is commented and explained. 

### General preparation
Insert your ontology name, project shortcode, and the path to your data source. If necessary, activate one of the lines
that are commented out.  
Then, the `root` element is created, which represents the `<knora>` tag of the XML document. As first children of 
`<knora>`, some standard permissions are added. At the end, please carefully check the permissions of the finished XML
file if they meet your requirements, and adapt them if necessary.  
The standard permission of a resource is "res-default", and of a property "prop-default". If you don't specify it 
otherwise, all resources and properties get these permissions. With excel2xml, it is not possible to create resources/
properties that don't have permissions, because they would be invisible for all users except project admins and system
admins. Read more about permissions [here](./dsp-tools-xmlupload.md#how-to-use-the-permissions-attribute-in-resourcesproperties).

### Create list mappings
Let's assume that your data source has a column containing list values named after the "label" of the JSON project list, 
instead of the "name" which is needed for the `dsp-tools xmlupload`. You need a way to get the names from the labels.
If your data source uses the labels correctly, this is an easy task: The method `create_json_list_mapping()` creates a
dictionary that maps the labels to the names.  
If, however, your data source has spelling variants, you need the more sophisticated approach of 
`create_json_excel_list_mapping()`: This method creates a dict that maps the list values in your data source to their 
correct JSON project node name. This happens based on string similarity. Please carefully check the result if there are
no false matches!

### Create all resources
With the help of pandas, you can then iterate through the rows of your Excel/CSV, and create resources and properties. 
Some examples of useful helper methods:

 - For every property, there is a helper function that explains itself when you hover over it. It also has a link to 
   the dsp-tools documentation of this property. So you don't need to worry how to construct a certain XML value for a 
   certain property. 
 - `check_notna(cell)`: quickly check if a cell contains at least one word-character
 - `find_date_in_string(string)`: If a cell contains a date, this function converts it to the correctly formatted DSP 
   date string.
 - `make_boolean_prop(cell)`: Recognizes many boolean formats: 0/1, true/false, Yes/No, ...
 - `make_xsd_id_compatible(string)`: Make a string compatible with the constraints of xsd:ID, so that it can be used as 
   ID of a resource.


## Complete example
Save the following files into a directory, and run the Python script. The features discussed in this document are
contained therein.

 - sample data: [excel2xml_sample_data.csv](assets/templates/excel2xml_sample_data.csv)
 - sample ontology: [excel2xml_sample_onto.json](assets/templates/excel2xml_sample_onto.json)
 - sample script: [excel2xml_sample_script.py](assets/templates/excel2xml_sample_script.py)
