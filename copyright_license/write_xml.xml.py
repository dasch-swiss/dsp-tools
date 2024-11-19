from lxml import etree

copyright_str = "Attribution-NonCommercial 4.0 International (CC BY-NC 4.0)."
license_str = "Credit: Zebrafish embryo.\nSource: Wellcome Collection."

def as_attrib() -> None:
    """
    b'<bitstream
        copyright="Attribution-NonCommercial 4.0 International (CC BY-NC 4.0)."
        license="Credit: Zebrafish embryo.&#10;Source: Wellcome Collection."
        >testdata/bitstreams/test.tif
    </bitstream>\n'
    """
    as_attrib = etree.Element("bitstream", copyright=copyright_str, license=license_str)
    as_attrib.text = "testdata/bitstreams/test.tif"

    as_attrib_str = etree.tostring(as_attrib, pretty_print=True)
    return as_attrib_str


s = """
            <license>Credit: Zebrafish embryo.
                Source: Wellcome Collection.
            </license>
"""

tree = etree.fromstring(s)
print()


