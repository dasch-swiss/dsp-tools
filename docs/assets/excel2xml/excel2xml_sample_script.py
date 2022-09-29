import os
import warnings

import pandas as pd
import regex

from knora import excel2xml

# general preparation
# -------------------
path_to_json = "excel2xml_sample_onto.json"
main_df = pd.read_csv("excel2xml_sample_data.csv", dtype="str", sep=",")  # or: pd.read_excel("*.xls(x)", dtype="str")

# remove rows without usable values (prevents Errors when there are empty rows at the end of the file)
main_df = main_df.applymap(lambda x: x if pd.notna(x) and regex.search(r"[\p{L}\d_!?]", str(x), flags=regex.U) else pd.NA)
main_df.dropna(axis="index", how="all", inplace=True)

# create the root tag <knora> and append the permissions
root = excel2xml.make_root(shortcode="0123", default_ontology="migration-template")
root = excel2xml.append_permissions(root)


# create list mappings
# --------------------
# for every node of the list "category", this dictionary maps the German label to the node name
category_labels_to_names = excel2xml.create_json_list_mapping(
    path_to_json=path_to_json,
    list_name="category",
    language_label="de"
)
# for every node of the list "category", this dictionary maps similar entries of the Excel column to the node name
# when you run this script, two warnings appear that "Säugetiere" and "Kunstwerk" couldn't be matched. Luckily, these
# two are covered in category_labels_to_names!
category_excel_values_to_names = excel2xml.create_json_excel_list_mapping(
    path_to_json=path_to_json,
    list_name="category",
    excel_values=main_df["Category"],
    sep=","
)


# create resources of type ":Image2D"
# -----------------------------------
# create a dict that keeps the IDs of the created resources
image2d_labels_to_ids = dict()
# iterate through all files in the "images" folder that don't start with "~$" or "." (unusable system files)
for img in [file for file in os.scandir("images") if not regex.search(r"^~$|^\.", file.name)]:
    resource_label = img.name
    resource_id = excel2xml.make_xsd_id_compatible(resource_label)
    # keep a reference to this ID in the dict
    image2d_labels_to_ids[resource_label] = resource_id
    resource = excel2xml.make_resource(
        label=resource_label,
        restype=":Image2D",
        id=resource_id
    )
    resource.append(excel2xml.make_bitstream_prop(img.path))
    resource.append(excel2xml.make_text_prop(":hasTitle", resource_label))
    root.append(resource)


# create resources of type ":Object"
# ----------------------------------
# create a dict that keeps the IDs of the created resources
object_labels_to_ids = dict()

# iterate through all rows of your data source, in pairs of (row-number, row)
for index, row in main_df.iterrows():

    # keep a reference to this ID in the dict
    resource_label = row["Object"]
    resource_id = excel2xml.make_xsd_id_compatible(resource_label)
    object_labels_to_ids[resource_label] = resource_id

    resource = excel2xml.make_resource(
        label=resource_label,
        restype=":Object",
        id=resource_id
    )

    # check every existing ":Image2D" resource, if there is an image that belongs to this object
    for img_label, img_id in image2d_labels_to_ids.items():
        # check if the label of ":Object" is contained in the label of ":Image2D"
        if resource_label in img_label:
            # create a resptr-link to the ID of the ":Image2D" resource
            resource.append(excel2xml.make_resptr_prop(":hasImage", img_id))

    # add a text property with the simple approach
    resource.append(excel2xml.make_text_prop(":hasName", row["Title"]))

    # add a text property, overriding the default values for "permissions" and "encoding"
    resource.append(excel2xml.make_text_prop(
        ":hasDescription",
        excel2xml.PropertyElement(value=row["Description"], permissions="prop-restricted",
                                  comment="comment to 'Description'", encoding="xml")
    ))

    # get "category" list nodes: split the cell into a list of values...
    category_values_raw = [x.strip() for x in row["Category"].split(",")]
    # ...look up every value in "category_labels_to_names", and if it's not there, in "category_excel_values_to_names"...
    category_values = [category_labels_to_names.get(x, category_excel_values_to_names.get(x)) for x in category_values_raw]
    # ...create the <list-prop> with the correct names of the list nodes
    resource.append(excel2xml.make_list_prop("category", ":hasCategory", category_values))

    if excel2xml.check_notna(row["Public"]):
        resource.append(excel2xml.make_boolean_prop(":isPublic", row["Public"]))
    if excel2xml.check_notna(row["Color"]):
        resource.append(excel2xml.make_color_prop(":hasColor", row["Color"]))
    potential_date = excel2xml.find_date_in_string(row["Date"])
    if potential_date:
        resource.append(excel2xml.make_date_prop(":hasDate", potential_date))
    else:
        warnings.warn(f"Error in row {index + 2}: The column 'Date' should contain a date!")
    if excel2xml.check_notna(row["Time"]):
        resource.append(excel2xml.make_time_prop(":hasTime", row["Time"]))
    if excel2xml.check_notna(row["Weight (kg)"]):
        resource.append(excel2xml.make_decimal_prop(":hasWeight", row["Weight (kg)"]))
    if excel2xml.check_notna(row["Location"]):
        resource.append(excel2xml.make_geoname_prop(":hasLocation", row["Location"]))
    if excel2xml.check_notna(row["URL"]):
        resource.append(excel2xml.make_uri_prop(":hasExternalLink", row["URL"]))

    root.append(resource)


# Annotation, Region, Link
# ------------------------
# These special resource classes are DSP base resources, that's why they use DSP base properties without prepended colon
# See the docs for more details:
# https://docs.dasch.swiss/latest/DSP-TOOLS/dsp-tools-xmlupload/#dsp-base-resources-base-properties-to-be-used-directly-in-the-xml-file
annotation = excel2xml.make_annotation("Annotation to Anubis", "annotation_to_anubis")
annotation.append(excel2xml.make_text_prop("hasComment", "Date and time are invented, like for the other resources."))
annotation.append(excel2xml.make_resptr_prop("isAnnotationOf", object_labels_to_ids["Anubis"]))
root.append(annotation)

region = excel2xml.make_region("Region of the Meteorite image", "region_of_meteorite")
region.append(excel2xml.make_text_prop("hasComment", "This is a comment"))
region.append(excel2xml.make_color_prop("hasColor", "#5d1f1e"))
region.append(excel2xml.make_resptr_prop("isRegionOf", image2d_labels_to_ids["GibbeonMeteorite.jpg"]))
region.append(excel2xml.make_geometry_prop(
    "hasGeometry",
    '{"type": "rectangle", "lineColor": "#ff3333", "lineWidth": 2, '
    '"points": [{"x": 0.08, "y": 0.16}, {"x": 0.73, "y": 0.72}], "original_index": 0}'
))
root.append(region)

link = excel2xml.make_link("Link between BM1888-0601-716 and Horohoroto", "link_BM1888-0601-716_horohoroto")
link.append(excel2xml.make_text_prop("hasComment", "This is a comment"))
link.append(excel2xml.make_resptr_prop("hasLinkTo", [object_labels_to_ids["BM1888-0601-716"], object_labels_to_ids["Horohoroto"]]))
root.append(link)


# write file
# ----------
excel2xml.write_xml(root, "data.xml")
