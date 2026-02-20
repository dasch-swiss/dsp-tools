from typing import Any

import pytest

from dsp_tools.commands.get.legacy_models.propertyclass import _extract_gui_info
from dsp_tools.commands.get.legacy_models.propertyclass import _extract_superproperties
from dsp_tools.commands.get.legacy_models.propertyclass import create_property_class_from_json
from dsp_tools.error.exceptions import BaseError


class TestExtractGuiInfo:
    """Tests for the _extract_gui_info function."""

    def test_pulldown_replaced_with_list(self) -> None:
        # GUI element transformation: Pulldown → List
        json_obj = {"salsah-gui:guiElement": {"@id": "salsah-gui:Pulldown"}}
        _, gui_element = _extract_gui_info(json_obj)
        assert gui_element == "salsah-gui:List"

    def test_radio_replaced_with_list(self) -> None:
        # GUI element transformation: Radio → List
        json_obj = {"salsah-gui:guiElement": {"@id": "salsah-gui:Radio"}}
        _, gui_element = _extract_gui_info(json_obj)
        assert gui_element == "salsah-gui:List"

    def test_other_gui_element_unchanged(self) -> None:
        json_obj = {"salsah-gui:guiElement": {"@id": "salsah-gui:Textarea"}}
        _, gui_element = _extract_gui_info(json_obj)
        assert gui_element == "salsah-gui:Textarea"

    def test_gui_attributes_key_value_parsing(self) -> None:
        # GUI attributes are parsed as key=value strings
        json_obj = {"salsah-gui:guiAttribute": ["size=80", "maxlength=255"]}
        gui_attrs, _ = _extract_gui_info(json_obj)
        assert gui_attrs is not None
        assert gui_attrs["size"] == "80"
        assert gui_attrs["maxlength"] == "255"

    def test_gui_attributes_single_value(self) -> None:
        # Single attribute (not in a list)
        json_obj = {"salsah-gui:guiAttribute": "cols=60"}
        gui_attrs, _ = _extract_gui_info(json_obj)
        assert gui_attrs is not None
        assert gui_attrs["cols"] == "60"

    def test_gui_attributes_key_without_value(self) -> None:
        # Attribute with key only (no =value)
        json_obj = {"salsah-gui:guiAttribute": ["nocolors"]}
        gui_attrs, _ = _extract_gui_info(json_obj)
        assert gui_attrs is not None
        assert gui_attrs["nocolors"] == ""

    def test_no_gui_info(self) -> None:
        json_obj: dict[str, Any] = {}
        gui_attrs, gui_element = _extract_gui_info(json_obj)
        assert gui_attrs is None
        assert gui_element is None


class TestExtractSuperproperties:
    """Tests for the _extract_superproperties function."""

    def test_single_superproperty(self) -> None:
        # Single superproperty (not in list)
        json_obj = {"rdfs:subPropertyOf": {"@id": "knora-api:hasValue"}}
        result = _extract_superproperties(json_obj)
        assert result == ("knora-api:hasValue",)

    def test_multiple_superproperties(self) -> None:
        json_obj = {
            "rdfs:subPropertyOf": [
                {"@id": "knora-api:hasValue"},
                {"@id": "knora-api:hasLinkTo"},
            ]
        }
        result = _extract_superproperties(json_obj)
        assert result is not None
        assert "knora-api:hasValue" in result
        assert "knora-api:hasLinkTo" in result

    def test_no_superproperties(self) -> None:
        json_obj: dict[str, Any] = {}
        result = _extract_superproperties(json_obj)
        assert result is None

    def test_empty_superproperty_list(self) -> None:
        json_obj: dict[str, Any] = {"rdfs:subPropertyOf": []}
        result = _extract_superproperties(json_obj)
        assert result is None


class TestCreatePropertyClassFromJson:
    """Tests for the create_property_class_from_json factory function."""

    def test_not_resource_property_raises(self) -> None:
        json_obj = {"@id": "myonto:myProp", "knora-api:isResourceProperty": False}
        with pytest.raises(BaseError, match="not a property"):
            create_property_class_from_json(json_obj)

    def test_missing_id_raises(self) -> None:
        json_obj = {"knora-api:isResourceProperty": True}
        with pytest.raises(BaseError, match='has no "@id"'):
            create_property_class_from_json(json_obj)

    def test_json_as_list_unwrapped(self) -> None:
        # JSON can come as a list with single element
        json_obj = [
            {
                "@id": "myonto:myProp",
                "knora-api:isResourceProperty": True,
            }
        ]
        prop = create_property_class_from_json(json_obj)
        assert prop.name == "myProp"

    def test_valid_property(self) -> None:
        json_obj = {
            "@id": "myonto:hasTitle",
            "knora-api:isResourceProperty": True,
            "knora-api:objectType": {"@id": "knora-api:TextValue"},
            "knora-api:subjectType": {"@id": "myonto:Resource"},
            "rdfs:label": [{"@language": "en", "@value": "Title"}],
            "salsah-gui:guiElement": {"@id": "salsah-gui:SimpleText"},
            "salsah-gui:guiAttribute": ["size=80"],
            "rdfs:subPropertyOf": {"@id": "knora-api:hasValue"},
        }
        prop = create_property_class_from_json(json_obj)
        assert prop.name == "hasTitle"
        assert prop.rdf_object == "knora-api:TextValue"
        assert prop.rdf_subject == "myonto:Resource"
        assert prop.gui_element == "salsah-gui:SimpleText"
        assert prop.gui_attributes is not None
        assert prop.gui_attributes["size"] == "80"
        assert prop.superproperties == ("knora-api:hasValue",)
