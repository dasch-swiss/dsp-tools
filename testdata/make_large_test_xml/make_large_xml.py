from pathlib import Path

from lxml import etree

from dsp_tools import excel2xml

# ruff: noqa: D103 (Missing docstring in public function)


def main(resource_count: int) -> None:
    root = excel2xml.make_root(shortcode="0123", default_ontology="large")
    root = excel2xml.append_permissions(root)

    img_id = "ImageFile_ID"
    root.append(_make_stillimage_representation(img_id, Path("testdata/bitstreams/test.jpeg")))

    _make_all_image_resources(root, resource_count, img_id)

    excel2xml.write_xml(root, Path(f"testdata/make_large_test_xml/{resource_count}_resources.xml"))


def _make_stillimage_representation(res_id: str, fielpath: Path) -> etree._Element:
    res = excel2xml.make_resource(label="Image File", restype=":ImageFile", id=res_id)
    img = excel2xml.make_bitstream_prop(fielpath)
    res.append(img)
    return res


def _make_all_image_resources(root: etree._Element, resource_count: int, linked_img_id: str) -> None:
    for count in range(resource_count):
        root.append(_make_one_resource_(count, linked_img_id))


def _make_one_resource_(id_counter: int, linked_img_id: str) -> etree._Element:
    res = excel2xml.make_resource(label=f"Image {id_counter}", restype=":Image", id=f"Image_ID_{id_counter}")
    text = excel2xml.make_text_prop(":hasText", value="Text")
    res.append(text)
    link_prop = excel2xml.make_resptr_prop(":hasImage", value=linked_img_id)
    res.append(link_prop)
    return res


if __name__ == "__main__":
    main(resource_count=50000)
