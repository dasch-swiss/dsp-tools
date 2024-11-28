import pandas as pd
import pytest
import regex

from dsp_tools.models.exceptions import InputError
from dsp_tools.xmllib.models.copyright_attributions import CopyrightAttributions
from dsp_tools.xmllib.models.dsp_base_resources import AnnotationResource
from dsp_tools.xmllib.models.licenses import License
from dsp_tools.xmllib.models.licenses import Licenses
from dsp_tools.xmllib.models.resource import Resource
from dsp_tools.xmllib.models.root import XMLRoot


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
    annotation = list(serialised.iterdescendants(tag="{https://dasch.swiss/schema}annotation"))
    assert len(annotation) == 1
    general_resources = list(serialised.iterdescendants(tag="{https://dasch.swiss/schema}resource"))
    assert len(general_resources) == 2


class TestRootLicenses:
    def test_default(self) -> None:
        xml_root = XMLRoot.create_new("0000", "test")
        assert len(xml_root.licenses.licenses) == 8

    def test_add_license_success(self) -> None:
        # the default licenses are only added with the create_new method
        xml_root = XMLRoot("0000", "test", CopyrightAttributions(), Licenses())
        xml_root.add_license("id", "text", pd.NA)
        license_list = xml_root.licenses.licenses
        assert len(license_list) == 1
        assert license_list[0].id_ == "id"
        assert license_list[0].text == "text"
        assert not license_list[0].uri

    def test_add_license_raises(self) -> None:
        # the default licenses are only added with the create_new method
        xml_root = XMLRoot("0000", "test", CopyrightAttributions(), Licenses([License("id", "text", None)]))
        msg = regex.escape("A license with the ID 'id' already exists. All IDs must be unique.")
        with pytest.raises(InputError, match=msg):
            xml_root.add_license("id", "text", pd.NA)
