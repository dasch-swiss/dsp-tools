import pandas as pd

from dsp_tools import excel2xml

df = pd.read_csv("example_data.csv")

root = excel2xml.make_root(shortcode="0001", default_ontology="onto")
root = excel2xml.append_permissions(root)

for _, row in df.iterrows():
    # Make Resource
    res = excel2xml.make_resource(id=row["id"], restype=row["restype"], label=row["label"])

    # Check if there are files or iiif-links
    if not pd.isna(row["file"]):
        bitstream = excel2xml.make_bitstream_prop(path=row["file"])
        res.append(bitstream)

    if not pd.isna(row["iiif-uri"]):
        iiif = excel2xml.make_iiif_uri_prop(iiif_uri=row["iiif-uri"])
        res.append(iiif)

    # A list for all the dog names
    dog_names = []

    # Make the public name property
    public_name = excel2xml.PropertyElement(value=row["hasName_public"], encoding="utf8")
    dog_names.append(public_name)

    # Check if there is a private name
    if not pd.isna(row["hasName_private"]):
        private_name = excel2xml.PropertyElement(
            value=row["hasName_private"],
            permissions="prop-restricted",
            encoding="utf8",
            comment="This is the private name of the dog.",
        )
        dog_names.append(private_name)

    # Make and append the <text-prop>
    name_prop = excel2xml.make_text_prop(name=":hasName", value=dog_names)
    res.append(name_prop)

    # Add street address and keep the linebreaks
    street_prop = excel2xml.PropertyElement(value=row["hasStreetAddress"], encoding="xml")
    street_address = excel2xml.make_text_prop(name=":hasStreetAddress", value=street_prop)
    res.append(street_address)

    # Append the finished resource
    root.append(res)


excel2xml.write_xml(root, "output-excel2xml.xml")
