import re

import pytest

from dsp_tools.commands.xmlupload.upload_config import UploadConfig
from dsp_tools.commands.xmlupload.xmlupload import xmlupload
from dsp_tools.models.exceptions import BaseError, UserError

server = "http://0.0.0.0:3333"
user = "root@example.com"
password = "test"
imgdir = "."
sipi = "http://0.0.0.0:1024"


def test_error_on_nonexistent_shortcode() -> None:
    expected = "A project with shortcode 9999 could not be found on the DSP server"
    with pytest.raises(BaseError, match=expected):
        xmlupload(
            input_file="testdata/invalid-testdata/xml-data/inexistent-shortcode.xml",
            server=server,
            user=user,
            password=password,
            imgdir=imgdir,
            sipi=sipi,
            config=UploadConfig(),
        )


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
