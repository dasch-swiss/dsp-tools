import pandas as pd

from dsp_tools import excel2xml

df = pd.read_csv("example_data.csv")

root = excel2xml.XMLRoot(shortcode="0001", default_ontology="onto")

for _, row in df.iterrows():
    # Make Resource
    res = excel2xml.Resource(res_id=row["id"], restype=row["restype"], label=row["label"])

    # Check if there are files or iiif-links
    if not pd.isna(row["file"]):
        res.filepath = row["file"]
    if not pd.isna(row["iiif-uri"]):
        res.iiif_uri = row["iiif-uri"]

    # Make the public name property
    dog_name = excel2xml.SimpleText(value=row["hasName_public"], property=":hasName")
    res.values.append(dog_name)

    # Check if there is a private name
    if not pd.isna(row["hasName_private"]):
        private_name = excel2xml.SimpleText(
            value=row["hasName_private"],
            property=":hasName",
            permissions="prop-restricted",
            comment="This is the private name of the dog.",
        )
        res.values.append(private_name)

    # Add street address and keep the linebreaks
    street_address = excel2xml.Richtext(
        value=row["hasStreetAddress"], property=":hasStreetAddress", preserve_linebreaks=True
    )
    res.values.append(street_address)

    # Append the finished resource
    root.resources.append(res)


root.write_file(filepath="demo-xmllib.xml")
