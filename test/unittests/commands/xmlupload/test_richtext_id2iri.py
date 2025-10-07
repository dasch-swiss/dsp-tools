# mypy: disable-error-code="no-untyped-def"

import pytest

from dsp_tools.commands.xmlupload.iri_resolver import IriResolver
from dsp_tools.commands.xmlupload.richtext_id2iri import _replace_ids_if_found
from dsp_tools.commands.xmlupload.richtext_id2iri import _replace_one_id
from dsp_tools.commands.xmlupload.richtext_id2iri import find_internal_ids
from dsp_tools.commands.xmlupload.richtext_id2iri import prepare_richtext_string_for_upload
from dsp_tools.error.exceptions import Id2IriReplacementError

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


class TestReplaceIdForUpload:
    def test_with_iris_and_ids(self, iri_resolver):
        expected = (
            '<?xml version="1.0" encoding="UTF-8"?>\n<text>'
            'Start text <a class="salsah-link" href="r1_iri">r1_id</a>This is normal text. '
            'Next sentence <a class="salsah-link" href="r2_iri">r2_id</a> now finished. '
            f'This is with an IRI <a class="salsah-link" href="{RES_IRI}">Resource IRI</a>.</text>'
        )
        result = prepare_richtext_string_for_upload(TXT_THREE_LINKS_WITH_IRIS_AND_IDS, iri_resolver)
        assert result == expected

    def test_no_ids(self, iri_resolver):
        result = prepare_richtext_string_for_upload(TXT_NO_LINKS, iri_resolver)
        expected = f'<?xml version="1.0" encoding="UTF-8"?>\n<text>{TXT_NO_LINKS}</text>'
        assert result == expected

    def test_raises(self, iri_resolver):
        txt = 'Start Text <a class="salsah-link" href="IRI:not_in_lookup:IRI">txt</a> end text.'
        with pytest.raises(Id2IriReplacementError):
            prepare_richtext_string_for_upload(txt, iri_resolver)


class TestReplaceIdIfFound:
    def test_with_iris_and_ids(self, iri_resolver):
        expected = (
            'Start text <a class="salsah-link" href="r1_iri">r1_id</a>This is normal text. '
            'Next sentence <a class="salsah-link" href="r2_iri">r2_id</a> now finished. '
            f'This is with an IRI <a class="salsah-link" href="{RES_IRI}">Resource IRI</a>.'
        )
        result, not_found = _replace_ids_if_found(TXT_THREE_LINKS_WITH_IRIS_AND_IDS, iri_resolver)
        assert result == expected
        assert not not_found

    def test_no_ids(self, iri_resolver):
        result, not_found = _replace_ids_if_found(TXT_NO_LINKS, iri_resolver)
        assert result == TXT_NO_LINKS
        assert not not_found

    def test_not_in_lookup(self, iri_resolver):
        txt = (
            'Start Text <a class="salsah-link" href="IRI:not_in_lookup:IRI">txt</a> end text. '
            'Next sentence <a class="salsah-link" href="IRI:r1_id:IRI">r1_id</a> now finished.'
        )
        expected = (
            'Start Text <a class="salsah-link" href="IRI:not_in_lookup:IRI">txt</a> end text. '
            'Next sentence <a class="salsah-link" href="r1_iri">r1_id</a> now finished.'
        )
        result, not_found = _replace_ids_if_found(txt, iri_resolver)
        assert result == expected
        assert not_found == {"not_in_lookup"}


class TestReplaceOneId:
    def test_one_link(self, iri_resolver):
        expected = 'Start Text <a class="salsah-link" href="r1_iri">r1_id</a> end text.'
        result = _replace_one_id(TXT_ONE_ID, "r1_id", "r1_iri")
        assert result == expected

    def test_three_links_two_resources(self, iri_resolver):
        expected = (
            'Start text <a class="salsah-link" href="r1_iri">r1_id</a>This is normal text. '
            'Next sentence <a class="salsah-link" href="IRI:r3_id:IRI">r3_id</a> now finished. '
            'Last <a class="salsah-link" href="r1_iri">r1_id</a>.'
        )
        result = _replace_one_id(TXT_THREE_LINKS_TWO_RES, "r1_id", "r1_iri")
        assert result == expected

    def test_with_iris_and_ids(self, iri_resolver):
        expected = (
            'Start text <a class="salsah-link" href="r1_iri">r1_id</a>This is normal text. '
            'Next sentence <a class="salsah-link" href="IRI:r2_id:IRI">r2_id</a> now finished. '
            f'This is with an IRI <a class="salsah-link" href="{RES_IRI}">Resource IRI</a>.'
        )
        result = _replace_one_id(TXT_THREE_LINKS_WITH_IRIS_AND_IDS, "r1_id", "r1_iri")
        assert result == expected


class TestFindInternalIDs:
    def test_one_link(self):
        result = find_internal_ids(TXT_ONE_ID)
        assert result == {"r1_id"}

    def test_three_links_two_resources(self):
        result = find_internal_ids(TXT_THREE_LINKS_TWO_RES)
        assert result == {"r1_id", "r3_id"}

    def test_with_iris_and_ids(self):
        result = find_internal_ids(TXT_THREE_LINKS_WITH_IRIS_AND_IDS)
        assert result == {"r1_id", "r2_id"}

    def test_no_links(self):
        assert not find_internal_ids(TXT_NO_LINKS)
