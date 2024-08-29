from dataclasses import dataclass
from typing import Any

import pytest
import regex
from lxml import etree

from dsp_tools.commands.xmlupload.check_consistency_with_ontology import do_xml_consistency_check_with_ontology
from dsp_tools.commands.xmlupload.ontology_client import OntologyClientLive
from dsp_tools.models.exceptions import BaseError
from dsp_tools.models.exceptions import InputError
from dsp_tools.models.exceptions import UserError
from test.integration.commands.xmlupload.connection_mock import ConnectionMockBase


@dataclass
class ConnectionMockRaising(ConnectionMockBase):
    def get(
        self,
        route: str,  # noqa: ARG002 (unused-method-argument)
        headers: dict[str, str] | None = None,  # noqa: ARG002 (unused-method-argument)
    ) -> dict[str, Any]:
        raise BaseError("foo")


@dataclass
class ConnectionMockWithResponses(ConnectionMockBase):
    get_responses: tuple[dict[str, Any], ...] = (
        {
            "project": {
                "ontologies": ["http://0.0.0.0:3333/ontology/4123/testonto/v2"],
            }
        },
        {
            "@graph": [
                {
                    "@id": "testonto:ValidResourceClass",
                    "knora-api:isResourceClass": True,
                }
            ]
        },
        {
            "@graph": [
                {
                    "@id": "knora-api:ValidResourceClass",
                    "knora-api:isResourceClass": True,
                }
            ]
        },
    )
    counter = 0

    def get(
        self,
        route: str,  # noqa: ARG002 (unused-method-argument)
        headers: dict[str, str] | None = None,  # noqa: ARG002 (unused-method-argument)
    ) -> dict[str, Any]:
        response = self.get_responses[self.counter]
        self.counter += 1
        return response


def test_error_on_nonexistent_shortcode() -> None:
    root = etree.parse("testdata/xml-data/test-data-minimal.xml").getroot()
    con = ConnectionMockRaising()
    ontology_client = OntologyClientLive(
        con=con,
        shortcode="9999",
        default_ontology="foo",
    )
    with pytest.raises(
        UserError, match=regex.escape("A project with shortcode 9999 could not be found on the DSP server")
    ):
        do_xml_consistency_check_with_ontology(ontology_client, root)


def test_error_on_nonexistent_onto_name() -> None:
    root = etree.fromstring(
        '<knora shortcode="4124" default-ontology="notexistingfantasyonto">'
        '<resource label="The only resource" restype=":minimalResource" id="the_only_resource"/>'
        "</knora>"
    )
    con = ConnectionMockWithResponses()
    ontology_client = OntologyClientLive(
        con=con,
        shortcode="4124",
        default_ontology="notexistingfantasyonto",
    )
    expected = regex.escape(
        "\nSome property and/or class type(s) used in the XML are unknown.\n"
        "The ontologies for your project on the server are:\n"
        "    - testonto\n"
        "    - knora-api"
        "\n\n"
        "The following resource(s) have an invalid resource type:\n\n"
        "    Resource Type: ':minimalResource'\n"
        "    Problem: 'Unknown ontology prefix'\n"
        "    Resource ID(s):\n"
        "    - the_only_resource\n\n"
    )
    with pytest.raises(InputError, match=expected):
        do_xml_consistency_check_with_ontology(ontology_client, root)


if __name__ == "__main__":
    pytest.main([__file__])
