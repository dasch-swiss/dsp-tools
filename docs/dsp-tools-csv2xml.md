[![PyPI version](https://badge.fury.io/py/dsp-tools.svg)](https://badge.fury.io/py/dsp-tools)

# Convert a data source to XML
dsp-tools assists you in converting a data source like CSV/XLSX to an XML file. Unlike the other features of dsp-tools,
this doesn't work via command line, but via helper methods that you can import into your own Python script. Because
every data source is different, there is no single algorithm to convert them to XML. Every user has to deal with the 
specialties of his/her data source, but dsp-tool's helper methods can help a lot. This document demonstrates how it 
works. 

## How to use it
At the end of this document, you find a sample Python script that needs to be adapted by you. In the following, the main
steps are explained. 

### General preparation
Insert your ontology name, project shortcode, and the path to your data source. If necessary, activate one of the lines
that are commented out.  
Then, the `root` element is created, which represents the `<knora>` tag of the XML document. As first children of 
`<knora>`, some standard permissions are added. At the end, please carefully check the permissions of the finished XML
file if they meet your requirements. Adapt them in the finished XML file, if necessary.

### Create list mappings
Let's assume that your data source has a column containing list values named after the "label" of the onto list, 
instead of the "name" which is needed for the `dsp-tools xmlupload`. You need a way to get from the labels to the names.
If your data sources uses the labels correctly, this is an easy task: The method `create_onto_list_mapping()` creates a
dictionary that maps the labels to the names.  
If, however, your data source has spelling variants, you need the more sophisticated approach of 
`create_onto_excel_list_mapping()`: This method creates a dict that maps the list values in your data source to their 
correct JSON ontology node name. This happens based on string similarity. Please carefully check the result if there are
no false matches!

### Create all resources
With the help of pandas, you can then iterate through the rows of your Excel/CSV, and create resources and properties.  
Some examples of useful helper methods:

 - For every property, there is a helper function that explains itself when you hoover over it. It also has a link to 
   the dsp-tools documentation of this property. So you don't need to worry how to construct a certain XML value for a 
   certain property. 
 - `check_notna(cell)`:
    - quickly check if a cell contains at least one word-character
 - `find_date_in_string(string)`
    - If a cell contains a date, this function converts it to the correctly formatted DSP date string.
 - `make_boolean_prop(cell)`:
    - Recognizes many boolean formats: NaN, empty cell, 0/1, true/false, Yes/No, ...
 - `make_xsd_id_compatible(string)`:
    - Make a string compatible with the constraints of xsd:ID, so that it can be used as ID of a resource.


## Complete example

Save the script below into a file, download [csv2xml_sample.csv](assets/templates/csv2xml_sample.csv) and 
[rosetta.json](assets/templates/rosetta.json), and then you're ready to go!

```python
import pandas as pd
from knora import csv2xml as c2x

# general preparation
# -------------------
path_to_onto = 'rosetta.json'
main_df = pd.read_csv('csv2xml_sample.csv', dtype='str', sep=',')
# main_df = pd.read_excel('path-to-your-data-source', dtype='str')
# main_df.drop_duplicates(inplace = True)
# main_df.dropna(how = 'all', inplace = True)
root = c2x.make_root(shortcode='0123', default_ontology='onto-name')
root = c2x.append_permissions(root)


# create list mappings
# --------------------
category_dict = c2x.create_onto_list_mapping(
    path_to_onto = path_to_onto, 
    list_name = 'category',
    language_label='en'
)
category_dict_fallback = c2x.create_onto_excel_list_mapping(
    path_to_onto = path_to_onto, 
    list_name = 'category',
    excel_values=main_df['Category'],
    sep=','
)


# create all resources
# --------------------
for index, row in main_df.iterrows():
    resource = c2x.make_resource(
        label=row['Resource name'], 
        restype=':MyResource',
        id=c2x.make_xsd_id_compatible(row['Resource identifier'])
    )
    if c2x.check_notna(row['Image']):
        resource.append(c2x.make_bitstream_prop(row['Image'], permissions='prop-default'))
    resource.append(c2x.make_text_prop(':name', row['Resource name']))
    resource.append(c2x.make_text_prop(
        ':longtext', 
        c2x.PropertyElement(value=row['Long text'], permissions='prop-restricted', comment='long text', encoding='xml')
    ))

    # to get the correct category values, first split the cell, then look up the values in "category_dict", 
    # and if it's not there, look in "category_dict_fallback"
    category_values = [category_dict.get(x.strip(), category_dict_fallback[x.strip()]) for x in row['Category'].split(',')]
    resource.append(c2x.make_list_prop('category', ':hasCategory', values=category_values))
    resource.append(c2x.make_boolean_prop(name=':isComplete', value=row['Complete?']))
    if c2x.check_notna(row['Color']):
        resource.append(c2x.make_color_prop(':colorprop', row['Color']))
    if pd.notna(row['Date discovered']):
        potential_date = c2x.find_date_in_string(row['Date discovered'])
        if potential_date:
            resource.append(c2x.make_date_prop(':date', potential_date))
        else:
            c2x.handle_warnings('The column "Date discovered" should contain a date, but no date was detected!')
    if c2x.check_notna(row['Exact time']):
        resource.append(c2x.make_time_prop(':timeprop', row['Exact time']))
    if c2x.check_notna(row['Weight (kg)']):
        resource.append(c2x.make_decimal_prop(':weight', row['Weight (kg)']))
    if c2x.check_notna(row['Find location']):
        resource.append(c2x.make_geoname_prop(':location', row['Find location']))
    resource.append(c2x.make_integer_prop(':descendantsCount', row['Number of descendants']))
    if c2x.check_notna(row['Similar to']):
        resource.append(c2x.make_resptr_prop(':similarTo', row['Similar to']))
    if c2x.check_notna(row['See also']):
        resource.append(c2x.make_uri_prop(':url', row['See also']))

    root.append(resource)


# Annotation, Region, Link
# ------------------------
annotation = c2x.make_annotation('Annotation of Resource 0', 'annotation_of_res_0')
annotation.append(c2x.make_text_prop('hasComment', 'This is a comment'))
annotation.append(c2x.make_resptr_prop('isAnnotationOf', 'res_0'))
root.append(annotation)

region = c2x.make_region('Region of Image 0', 'region_of_image_0')
region.append(c2x.make_text_prop('hasComment', 'This is a comment'))
region.append(c2x.make_color_prop('hasColor', '#5d1f1e'))
region.append(c2x.make_resptr_prop('isRegionOf', 'image_0'))
region.append(c2x.make_geometry_prop('hasGeometry', '{"dummy": "dummy"}', calling_resource='Region of Image 0'))
    # the above method call will trigger a warning, because the JSON string is invalid
root.append(region)

link = c2x.make_link('Link between Resource 0 and 1', 'link_res_0_res_1')
link.append(c2x.make_text_prop('hasComment', 'This is a comment'))
link.append(c2x.make_resptr_prop('hasLinkTo', values=['res_0', 'res_1']))
root.append(link)


# write file
# ----------
c2x.write_xml(root, 'data.xml')
```
