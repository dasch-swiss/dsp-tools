# mypy: disable-error-code="no-untyped-def"

import pytest

from dsp_tools.commands.xmlupload.iri_resolver import IriResolver
from dsp_tools.commands.xmlupload.richtext_id2iri import _find_internal_ids

RES_IRI = "http://rdfh.ch/4123/DiAmYQzQSzC7cdTo6OJMYA"

TXT_ONE_ID = 'Start Text <a class="salsah-link" href="IRI:r1_id:IRI">r1_id</a> end text.'


TXT_THREE_LINKS_TWO_RES = (
    'Start text <a class="salsah-link" href="IRI:r1_id:IRI">r1_id</a>This is normal text. '
    'Next sentence <a class="salsah-link" href="IRI:r3_id:IRI">r3_id</a> now finished. '
    'Last <a class="salsah-link" href="IRI:r1_id:IRI">r1_id</a>.'
)

TXT_THREE_LINKS_WITH_IRIS_AND_IDS = (
    'Start text <a class="salsah-link" href="IRI:r1_id:IRI">r1_id</a>This is normal text. '
    'Next sentence <a class="salsah-link" href="IRI:r2_id:IRI">r2_id</a> now finished. '
    f'This is with an IRI <a class="salsah-link" href="{RES_IRI}">Resource IRI</a>.'
)

TXT_NO_LINKS = "Normal text, no links."


@pytest.fixture
def iri_resolver() -> IriResolver:
    return IriResolver({"r1_id": "r1_iri", "r2_id": "r2_iri", "r3_id": "r3_iri"})


class TestFindInternalIDs:
    def test_one_link(self):
        returned_set = _find_internal_ids(TXT_ONE_ID)
        assert returned_set == {"r2_id"}

    def test_three_links_two_resources(self):
        returned_set = _find_internal_ids(TXT_THREE_LINKS_TWO_RES)
        assert returned_set == {"r1_id", "r3_id"}

    def test_with_iris_and_ids(self):
        returned_set = _find_internal_ids(TXT_THREE_LINKS_WITH_IRIS_AND_IDS)
        assert returned_set == {"r1_id", "r2_id"}

    def test_no_links(self):
        assert not _find_internal_ids(TXT_NO_LINKS)
