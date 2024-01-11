import re
from dataclasses import dataclass
from pathlib import Path
from test.unittests.commands.xmlupload.connection_mock import ConnectionMockBase
from typing import Any

import pytest
from lxml import etree

from dsp_tools.commands.xmlupload.check_consistency_with_ontology import do_xml_consistency_check
from dsp_tools.commands.xmlupload.ontology_client import OntologyClientLive
from dsp_tools.commands.xmlupload.upload_config import UploadConfig
from dsp_tools.commands.xmlupload.xmlupload import xmlupload
from dsp_tools.models.exceptions import BaseError, UserError

server = "http://0.0.0.0:3333"
user = "root@example.com"
password = "test"
imgdir = "."
sipi = "http://0.0.0.0:1024"


@dataclass
class ConnectionMock(ConnectionMockBase):
    def get(
        self,
        route: str,  # noqa: ARG002 (unused-method-argument)
        headers: dict[str, str] | None = None,  # noqa: ARG002 (unused-method-argument)
    ) -> dict[str, Any]:
        raise BaseError("foo")


def test_error_on_nonexistent_shortcode() -> None:
    root = etree.parse("testdata/xml-data/test-data-minimal.xml").getroot()
    con = ConnectionMock()
    ontology_client = OntologyClientLive(
        con=con,
        shortcode="9999",
        default_ontology="foo",
        save_location=Path("bar"),
    )
    with pytest.raises(UserError, match="A project with shortcode 9999 could not be found on the DSP server"):
        do_xml_consistency_check(ontology_client, root)


def test_error_on_nonexistent_onto_name() -> None:
    expected = re.escape(
        "\nSome property and/or class type(s) used in the XML are unknown.\n"
        "The ontologies for your project on the server are:\n"
        "    - testonto\n"
        "    - knora-api\n\n"
        "---------------------------------------\n\n"
        "The following resource(s) have an invalid resource type:\n\n"
        "    Resource Type: ':minimalResource'\n"
        "    Problem: 'Unknown ontology prefix'\n"
        "    Resource ID(s):\n"
        "    - the_only_resource\n\n"
        "---------------------------------------\n\n"
    )
    with pytest.raises(UserError, match=expected):
        xmlupload(
            input_file="testdata/invalid-testdata/xml-data/inexistent-ontoname.xml",
            server=server,
            user=user,
            password=password,
            imgdir=imgdir,
            sipi=sipi,
            config=UploadConfig(),
        )


if __name__ == "__main__":
    pytest.main([__file__])
