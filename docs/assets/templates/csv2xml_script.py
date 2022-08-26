import pandas as pd
from knora import csv2xml

# general preparation
# -------------------
path_to_json = "rosetta.json"
main_df = pd.read_csv("csv2xml_sample.csv", dtype="str", sep=",")
# main_df = pd.read_excel("path-to-your-data-source", dtype="str")
# main_df.drop_duplicates(inplace = True)
# main_df.dropna(how = "all", inplace = True)
root = csv2xml.make_root(shortcode="0123", default_ontology="onto-name")
root = csv2xml.append_permissions(root)

# create list mappings
# --------------------
category_dict = csv2xml.create_json_list_mapping(
   path_to_json=path_to_json,
   list_name="category",
   language_label="en"
)
category_dict_fallback = csv2xml.create_json_excel_list_mapping(
   path_to_json=path_to_json,
   list_name="category",
   excel_values=main_df["Category"],
   sep=","
)

# create all resources
# --------------------
for index, row in main_df.iterrows():
   resource = csv2xml.make_resource(
      label=row["Resource name"],
      restype=":MyResource",
      id=csv2xml.make_xsd_id_compatible(row["Resource identifier"])
   )
   if csv2xml.check_notna(row["Image"]):
      resource.append(csv2xml.make_bitstream_prop(row["Image"], permissions="prop-default"))
   resource.append(csv2xml.make_text_prop(":name", row["Resource name"]))
   resource.append(csv2xml.make_text_prop(
      ":longtext",
      csv2xml.PropertyElement(value=row["Long text"], permissions="prop-restricted", comment="long text", encoding="xml")
   ))

   # to get the correct category values, first split the cell, then look up the values in "category_dict",
   # and if it's not there, look in "category_dict_fallback"
   category_values = [category_dict.get(x.strip(), category_dict_fallback[x.strip()]) for x in
                      row["Category"].split(",")]
   resource.append(csv2xml.make_list_prop("category", ":hasCategory", values=category_values))
   if csv2xml.check_notna(row["Complete?"]):
      resource.append(csv2xml.make_boolean_prop(name=":isComplete", value=row["Complete?"]))
   if csv2xml.check_notna(row["Color"]):
      resource.append(csv2xml.make_color_prop(":colorprop", row["Color"]))
   if pd.notna(row["Date discovered"]):
      potential_date = csv2xml.find_date_in_string(row["Date discovered"])
      if potential_date:
         resource.append(csv2xml.make_date_prop(":date", potential_date))
      else:
         csv2xml.handle_warnings('The column "Date discovered" should contain a date, but no date was detected!')
   if csv2xml.check_notna(row["Exact time"]):
      resource.append(csv2xml.make_time_prop(":timeprop", row["Exact time"]))
   if csv2xml.check_notna(row["Weight (kg)"]):
      resource.append(csv2xml.make_decimal_prop(":weight", row["Weight (kg)"]))
   if csv2xml.check_notna(row["Find location"]):
      resource.append(csv2xml.make_geoname_prop(":location", row["Find location"]))
   resource.append(csv2xml.make_integer_prop(":descendantsCount", row["Number of descendants"]))
   if csv2xml.check_notna(row["Similar to"]):
      resource.append(csv2xml.make_resptr_prop(":similarTo", row["Similar to"]))
   if csv2xml.check_notna(row["See also"]):
      resource.append(csv2xml.make_uri_prop(":url", row["See also"]))

   root.append(resource)

# Annotation, Region, Link
# ------------------------
annotation = csv2xml.make_annotation("Annotation of Resource 0", "annotation_of_res_0")
annotation.append(csv2xml.make_text_prop("hasComment", "This is a comment"))
annotation.append(csv2xml.make_resptr_prop("isAnnotationOf", "res_0"))
root.append(annotation)

region = csv2xml.make_region("Region of Image 0", "region_of_image_0")
region.append(csv2xml.make_text_prop("hasComment", "This is a comment"))
region.append(csv2xml.make_color_prop("hasColor", "#5d1f1e"))
region.append(csv2xml.make_resptr_prop("isRegionOf", "image_0"))
region.append(csv2xml.make_geometry_prop(
   "hasGeometry",
   '{"type": "rectangle", "lineColor": "#ff3333", "lineWidth": 2, "points": [{"x": 0.08, "y": 0.16}, {"x": 0.73, '
   '"y": 0.72}], "original_index": 0}'
))
root.append(region)

link = csv2xml.make_link("Link between Resource 0 and 1", "link_res_0_res_1")
link.append(csv2xml.make_text_prop("hasComment", "This is a comment"))
link.append(csv2xml.make_resptr_prop("hasLinkTo", values=["res_0", "res_1"]))
root.append(link)

# write file
# ----------
csv2xml.write_xml(root, "data.xml")