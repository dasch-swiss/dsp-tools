import pandas as pd
import pytest
import regex

from dsp_tools.models.exceptions import InputError
from dsp_tools.xmllib.models.copyright_attributions import CopyrightAttribution
from dsp_tools.xmllib.models.copyright_attributions import CopyrightAttributions
from dsp_tools.xmllib.models.dsp_base_resources import AnnotationResource
from dsp_tools.xmllib.models.licenses import License
from dsp_tools.xmllib.models.licenses import Licenses
from dsp_tools.xmllib.models.resource import Resource
from dsp_tools.xmllib.models.root import XMLRoot
from dsp_tools.xmllib.constants import DASCH_SCHEMA


def test_root_add_resources() -> None:
    xml_root = XMLRoot.create_new("0000", "test")

    # add_resource
    anno_res = AnnotationResource("annoID", "label", "id1", ["comment"])
    xml_root.add_resource(anno_res)
    assert len(xml_root.resources) == 1

    # add_resource_multiple
    many_resources = [Resource.create_new("id1", ":Restype", "label"), Resource.create_new("id2", ":Restype", "label")]
    xml_root.add_resource_multiple(many_resources)
    assert len(xml_root.resources) == 3

    xml_root.add_resource_multiple([])
    assert len(xml_root.resources) == 3

    # add_resource_optional
    no_resource = None
    xml_root.add_resource_optional(no_resource)
    assert len(xml_root.resources) == 3

    serialised = xml_root.serialise()
    annotation = list(serialised.iterdescendants(tag=f"{DASCH_SCHEMA}annotation"))
    assert len(annotation) == 1
    general_resources = list(serialised.iterdescendants(tag=f"{DASCH_SCHEMA}resource"))
    assert len(general_resources) == 2


class TestRootLicenses:
    def test_default(self) -> None:
        xml_root = XMLRoot.create_new("0000", "test")
        assert len(xml_root.licenses.licenses) == 8

    def test_add_license_success(self) -> None:
        xml_root = XMLRoot("0000", "test", CopyrightAttributions(), Licenses())
        xml_root.add_license("id", "text", pd.NA)
        license_list = xml_root.licenses.licenses
        assert len(license_list) == 1
        assert license_list[0].id_ == "id"
        assert license_list[0].text == "text"
        assert not license_list[0].uri

    def test_add_license_raises(self) -> None:
        xml_root = XMLRoot("0000", "test", CopyrightAttributions(), Licenses([License("id", "text", None)]))
        msg = regex.escape("A license with the ID 'id' already exists. All IDs must be unique.")
        with pytest.raises(InputError, match=msg):
            xml_root.add_license("id", "text", pd.NA)

    def test_add_license_with_dict(self) -> None:
        xml_root = XMLRoot("0000", "test", CopyrightAttributions(), Licenses())
        license_dict = {"id1": ("text1", "https://dasch.com/"), "id2": ("text2", None)}
        xml_root.add_license_with_dict(license_dict)
        assert xml_root.licenses.get_license_ids() == set(license_dict.keys())


class TestRootCopyrightAttributions:
    def test_default(self) -> None:
        xml_root = XMLRoot.create_new("0000", "test")
        assert len(xml_root.copyright_attributions.copyright_attributions) == 0

    def test_add_copyright_attribution_success(self) -> None:
        xml_root = XMLRoot("0000", "test", CopyrightAttributions(), Licenses())
        xml_root.add_copyright_attribution("id", "text")
        copyrights = xml_root.copyright_attributions.copyright_attributions
        assert len(copyrights) == 1
        assert copyrights[0].id_ == "id"
        assert copyrights[0].text == "text"

    def test_add_copyright_attribution_raises(self) -> None:
        xml_root = XMLRoot("0000", "test", CopyrightAttributions([CopyrightAttribution("id", "text")]), Licenses())
        msg = regex.escape("A copyright attribution with the ID 'id' already exists. All IDs must be unique.")
        with pytest.raises(InputError, match=msg):
            xml_root.add_copyright_attribution("id", "text")

    def test_add_copyright_attribution_with_dict(self) -> None:
        xml_root = XMLRoot("0000", "test", CopyrightAttributions(), Licenses())
        copy_dict = {"id1": "text1", "id2": "text2"}
        xml_root.add_copyright_attribution_with_dict(copy_dict)
        assert xml_root.copyright_attributions.get_copyright_attribution_ids() == set(copy_dict.keys())
