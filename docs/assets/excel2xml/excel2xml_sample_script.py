import os
import warnings

import pandas
import regex

from knora import excel2xml

# general preparation
# -------------------
path_to_json = "excel2xml_sample_onto.json"
main_df = pandas.read_csv("excel2xml_sample_data.csv", dtype="str", sep=",")
# main_df = pandas.read_excel("path to XLS(X) file", dtype="str")
# main_df.drop_duplicates(inplace = True)
main_df = main_df.applymap(lambda x: x if pandas.notna(x) and regex.search(r"[\p{L}\d_!?]", str(x), flags=regex.UNICODE) else pandas.NA)
main_df.dropna(axis="columns", how="all", inplace=True)
main_df.dropna(axis="index", how="all", inplace=True)
root = excel2xml.make_root(shortcode="0123", default_ontology="onto-name")
root = excel2xml.append_permissions(root)

# create list mappings
# --------------------
category_dict = excel2xml.create_json_list_mapping(
    path_to_json=path_to_json,
    list_name="category",
    language_label="de"
)
category_dict_fallback = excel2xml.create_json_excel_list_mapping(
    path_to_json=path_to_json,
    list_name="category",
    excel_values=main_df["Category"],
    sep=","
)

# create resources of type ":Image2D"
# -----------------------------------
image2d_names_to_ids = dict()
for img in [file for file in os.scandir("images") if not regex.search(r"^~$|^\.", file.name)]:
    resource_id = excel2xml.make_xsd_id_compatible(img.name)
    image2d_names_to_ids[img.name] = resource_id
    resource = excel2xml.make_resource(
        label=img.name,
        restype=":Image2D",
        id=resource_id
    )
    resource.append(excel2xml.make_bitstream_prop(img.path))
    resource.append(excel2xml.make_text_prop(":hasTitle", img.name))
    root.append(resource)


# create resources of type ":Object"
# ----------------------------------
object_names_to_ids = dict()
for index, row in main_df.iterrows():
    resource_id = excel2xml.make_xsd_id_compatible(row["Object"])
    object_names_to_ids[row["Object"]] = resource_id
    resource = excel2xml.make_resource(
        label=row["Object"],
        restype=":Object",
        id=resource_id
    )
    for img_name, img_id in image2d_names_to_ids.items():
        if row["Object"] in img_name:
            resource.append(excel2xml.make_resptr_prop(":hasImage", img_id))
    resource.append(excel2xml.make_text_prop(":hasName", row["Title"]))
    resource.append(excel2xml.make_text_prop(
        ":hasDescription",
        excel2xml.PropertyElement(value=row["Description"], permissions="prop-restricted",
                                  comment="comment to 'Description'", encoding="xml")
    ))

    # to get the correct category values, first split the cell, then look up the values in "category_dict",
    # and if it's not there, look in "category_dict_fallback"
    category_values = [category_dict.get(x.strip(), category_dict_fallback.get(x.strip())) for x in
                       row["Category"].split(",")]
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
annotation.append(excel2xml.make_resptr_prop("isAnnotationOf", object_names_to_ids["Anubis"]))
root.append(annotation)

region = excel2xml.make_region("Region of the Meteorite image", "region_of_meteorite")
region.append(excel2xml.make_text_prop("hasComment", "This is a comment"))
region.append(excel2xml.make_color_prop("hasColor", "#5d1f1e"))
region.append(excel2xml.make_resptr_prop("isRegionOf", image2d_names_to_ids["GibbeonMeteorite.jpg"]))
region.append(excel2xml.make_geometry_prop(
    "hasGeometry",
    '{"type": "rectangle", "lineColor": "#ff3333", "lineWidth": 2, '
    '"points": [{"x": 0.08, "y": 0.16}, {"x": 0.73, "y": 0.72}], "original_index": 0}'
))
root.append(region)

link = excel2xml.make_link("Link between BM1888-0601-716 and Horohoroto", "link_BM1888-0601-716_horohoroto")
link.append(excel2xml.make_text_prop("hasComment", "This is a comment"))
link.append(excel2xml.make_resptr_prop("hasLinkTo", [object_names_to_ids["BM1888-0601-716"], object_names_to_ids["Horohoroto"]]))
root.append(link)

# write file
# ----------
excel2xml.write_xml(root, "data.xml")
