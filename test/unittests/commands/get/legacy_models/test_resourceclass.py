from typing import Any
from unittest.mock import Mock

import pytest

from dsp_tools.commands.get.legacy_models.helpers import Cardinality
from dsp_tools.commands.get.legacy_models.resourceclass import HasProperty
from dsp_tools.commands.get.legacy_models.resourceclass import Ptype
from dsp_tools.commands.get.legacy_models.resourceclass import _extract_cardinality
from dsp_tools.commands.get.legacy_models.resourceclass import _extract_property_type_iri
from dsp_tools.commands.get.legacy_models.resourceclass import create_has_property_from_json
from dsp_tools.error.exceptions import BaseError


class TestExtractCardinality:
    """Tests for the _extract_cardinality function."""

    def test_cardinality_1(self) -> None:
        # owl:cardinality → exactly 1
        jsonld_obj = {"owl:cardinality": 1}
        assert _extract_cardinality(jsonld_obj) == Cardinality.C_1

    def test_cardinality_0_1(self) -> None:
        # owl:maxCardinality → 0-1
        jsonld_obj = {"owl:maxCardinality": 1}
        assert _extract_cardinality(jsonld_obj) == Cardinality.C_0_1

    def test_cardinality_0_n(self) -> None:
        # owl:minCardinality 0 → 0-n
        jsonld_obj = {"owl:minCardinality": 0}
        assert _extract_cardinality(jsonld_obj) == Cardinality.C_0_n

    def test_cardinality_1_n(self) -> None:
        # owl:minCardinality 1 → 1-n
        jsonld_obj = {"owl:minCardinality": 1}
        assert _extract_cardinality(jsonld_obj) == Cardinality.C_1_n

    def test_invalid_min_cardinality(self) -> None:
        # minCardinality with invalid value
        jsonld_obj = {"owl:minCardinality": 5}
        with pytest.raises(BaseError, match="Problem with cardinality"):
            _extract_cardinality(jsonld_obj)

    def test_no_cardinality(self) -> None:
        # No cardinality key present
        jsonld_obj: dict[str, Any] = {}
        with pytest.raises(BaseError, match="Problem with cardinality"):
            _extract_cardinality(jsonld_obj)


class TestExtractPropertyTypeIri:
    """Tests for the _extract_property_type_iri function."""

    def test_system_property(self) -> None:
        # rdf/rdfs/owl prefixes → Ptype.system
        jsonld_obj = {"owl:onProperty": {"@id": "rdf:type"}}
        prop_id, ptype = _extract_property_type_iri(jsonld_obj)
        assert prop_id == "rdf:type"
        assert ptype == Ptype.system

    def test_knora_property(self) -> None:
        # knora-api prefix → Ptype.knora
        jsonld_obj = {"owl:onProperty": {"@id": "knora-api:hasValue"}}
        prop_id, ptype = _extract_property_type_iri(jsonld_obj)
        assert prop_id == "knora-api:hasValue"
        assert ptype == Ptype.knora

    def test_custom_property(self) -> None:
        # Custom prefix → Ptype.other
        jsonld_obj = {"owl:onProperty": {"@id": "myonto:myProperty"}}
        prop_id, ptype = _extract_property_type_iri(jsonld_obj)
        assert prop_id == "myonto:myProperty"
        assert ptype == Ptype.other

    def test_missing_on_property(self) -> None:
        jsonld_obj: dict[str, Any] = {}
        with pytest.raises(BaseError, match="No property IRI given"):
            _extract_property_type_iri(jsonld_obj)

    def test_missing_id_in_on_property(self) -> None:
        jsonld_obj: dict[str, Any] = {"owl:onProperty": {}}
        with pytest.raises(BaseError, match="No property IRI given"):
            _extract_property_type_iri(jsonld_obj)


class TestCreateHasPropertyFromJson:
    """Tests for the create_has_property_from_json factory function."""

    def test_not_restriction_raises(self) -> None:
        # Not a restriction type → error
        jsonld_obj = {"@type": "owl:Class", "owl:onProperty": {"@id": "myonto:prop"}}
        with pytest.raises(BaseError, match="Expected restriction type"):
            create_has_property_from_json(jsonld_obj)

    def test_valid_restriction(self) -> None:
        jsonld_obj = {
            "@type": "owl:Restriction",
            "owl:onProperty": {"@id": "myonto:myProp"},
            "owl:cardinality": 1,
            "salsah-gui:guiOrder": 5,
        }
        prop_id, has_prop = create_has_property_from_json(jsonld_obj)
        assert prop_id == "myonto:myProp"
        assert has_prop.cardinality == Cardinality.C_1
        assert has_prop.ptype == Ptype.other
        assert has_prop.gui_order == 5

    def test_no_gui_order(self) -> None:
        jsonld_obj = {
            "@type": "owl:Restriction",
            "owl:onProperty": {"@id": "myonto:myProp"},
            "owl:cardinality": 1,
        }
        _, has_prop = create_has_property_from_json(jsonld_obj)
        assert has_prop.gui_order is None


class TestHasPropertyToDefinitionFileObj:
    """Tests for HasProperty.to_definition_file_obj serialization."""

    def test_system_property_returns_empty(self) -> None:
        # System properties should return empty dict
        mock_context = Mock()
        has_prop = HasProperty(
            property_id="rdf:type",
            cardinality=Cardinality.C_1,
            ptype=Ptype.system,
            gui_order=None,
        )
        result = has_prop.to_definition_file_obj(mock_context, "myonto")
        assert result == {}

    def test_knora_property_not_in_allowlist_returns_empty(self) -> None:
        # Knora properties (except isPartOf/seqnum) should return empty
        mock_context = Mock()
        has_prop = HasProperty(
            property_id="knora-api:hasValue",
            cardinality=Cardinality.C_1,
            ptype=Ptype.knora,
            gui_order=None,
        )
        result = has_prop.to_definition_file_obj(mock_context, "myonto")
        assert result == {}

    def test_knora_is_part_of_included(self) -> None:
        # knora-api:isPartOf is in allowlist
        mock_context = Mock()
        mock_context.reduce_iri.return_value = "knora-api:isPartOf"
        has_prop = HasProperty(
            property_id="knora-api:isPartOf",
            cardinality=Cardinality.C_1,
            ptype=Ptype.knora,
            gui_order=None,
        )
        result = has_prop.to_definition_file_obj(mock_context, "myonto")
        assert result["propname"] == "knora-api:isPartOf"

    def test_custom_property_with_gui_order(self) -> None:
        mock_context = Mock()
        mock_context.reduce_iri.return_value = "myonto:myProp"
        has_prop = HasProperty(
            property_id="myonto:myProp",
            cardinality=Cardinality.C_0_n,
            ptype=Ptype.other,
            gui_order=3,
        )
        result = has_prop.to_definition_file_obj(mock_context, "myonto")
        assert result["propname"] == "myonto:myProp"
        assert result["cardinality"] == "0-n"
        assert result["gui_order"] == 3

    def test_custom_property_without_gui_order(self) -> None:
        mock_context = Mock()
        mock_context.reduce_iri.return_value = "myonto:myProp"
        has_prop = HasProperty(
            property_id="myonto:myProp",
            cardinality=Cardinality.C_1,
            ptype=Ptype.other,
            gui_order=None,
        )
        result = has_prop.to_definition_file_obj(mock_context, "myonto")
        assert "gui_order" not in result
