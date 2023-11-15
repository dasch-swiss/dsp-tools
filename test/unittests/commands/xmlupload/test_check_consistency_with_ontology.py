from typing import Any

from lxml import etree
from pytest_unordered import unordered

from dsp_tools.commands.xmlupload.check_consistency_with_ontology import (
    _get_all_properties_from_one_resource,
    _get_all_properties_from_root,
    _get_resource_class_from_root,
)
from dsp_tools.commands.xmlupload.ontology_client import Ontology, OntologyClient


def test_get_resource_class_from_one_resource() -> None:
    test_ele = etree.fromstring(
        """<knora shortcode="0700" default-ontology="simcir">
                <resource label="res_A_19" restype=":TestThing1" id="res_B" permissions="res-default">
                    <resptr-prop name=":hasResource1">
                        <resptr permissions="prop-default">res_B</resptr>
                    </resptr-prop>
                </resource>
                <resource label="Res" restype=":TestThing2" id="res_A" permissions="res-default">
                    <resptr-prop name=":hasResource2">
                        <resptr permissions="prop-default">res_B</resptr>
                    </resptr-prop>
                </resource>
                <resource label="Res" restype=":TestThing2" id="res_C" permissions="res-default">
                    <resptr-prop name=":hasResource2">
                        <resptr permissions="prop-default">res_B</resptr>
                    </resptr-prop>
                </resource>
        </knora>"""
    )
    result = _get_resource_class_from_root(test_ele)
    assert result == {":TestThing1", ":TestThing2"}


def test_get_all_properties_from_one_resource() -> None:
    test_ele = etree.fromstring(
        """<resource label="res_A_19" restype=":TestThing1" id="res_B" permissions="res-default">
                <integer-prop name=":hasInteger">
                    <integer permissions="prop-default">4711</integer>
                </integer-prop>
                <decimal-prop name=":hasDecimal">
                    <decimal permissions="prop-default" comment="Eulersche Zahl">2.718281828459</decimal>
                </decimal-prop>
                <decimal-prop name=":hasDecimal">
                    <decimal permissions="prop-default" comment="Eulersche Zahl">2.718281828459</decimal>
                </decimal-prop>
                <geoname-prop name=":hasGeoname">
                    <geoname permissions="prop-default" comment="A sacred place for railroad fans">5416656</geoname>
                </geoname-prop>
                <color-prop name=":hasColor">
                    <color permissions="prop-default">#00ff00</color>
                </color-prop>
                <list-prop list="testlist" name=":hasListItem">
                    <list permissions="prop-default">first subnode</list>
                </list-prop>
        </resource>"""
    )
    result = _get_all_properties_from_one_resource(test_ele)
    assert result == {":hasInteger", ":hasDecimal", ":hasGeoname", ":hasColor", ":hasListItem"}


def test_get_all_properties_from_root() -> None:
    test_ele = etree.fromstring(
        """<knora shortcode="0700" default-ontology="simcir">
                <resource label="Imagething-tiff" restype=":ImageThing" id="image_thing_1" permissions="res-default">
                    <bitstream>testdata/bitstreams/test.tiff</bitstream>
                    <text-prop name=":hasSimpleText">
                        <text permissions="prop-default" encoding="utf8">This is a Imagething as TIFF</text>
                    </text-prop>
                </resource>
                <resource label="Partofthing-1" restype=":PartOfThing" id="partof_thing_1" permissions="res-default">
                    <bitstream>testdata/bitstreams/test.jpg</bitstream>
                    <resptr-prop name="knora-api:isPartOf">
                        <resptr permissions="prop-default">compound_thing_0</resptr>
                    </resptr-prop>
                <text-prop name="hasComment">
                    <text encoding="xml" permissions="prop-default">
                        This is a rectangle-formed region of interest of an image. It is also displayed as Annotation.
                    </text>
                    <text encoding="xml" permissions="prop-restricted">
                        This is a second comment.
                    </text>
                </text-prop>
                </resource>
        </knora>"""
    )
    result = _get_all_properties_from_root(test_ele)
    assert result == {":hasSimpleText", "knora-api:isPartOf", "hasComment"}
