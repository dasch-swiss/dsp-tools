# mypy: disable-error-code="method-assign,no-untyped-def"

import pandas as pd
import pytest
import regex

from dsp_tools.error.xmllib_errors import XmllibInputError
from dsp_tools.error.xmllib_warnings import XmllibInputWarning
from dsp_tools.xmllib.general_functions import ListLookup
from dsp_tools.xmllib.general_functions import clean_whitespaces_from_string
from dsp_tools.xmllib.general_functions import create_footnote_string
from dsp_tools.xmllib.general_functions import create_list_from_input
from dsp_tools.xmllib.general_functions import create_list_from_string
from dsp_tools.xmllib.general_functions import create_non_empty_list_from_string
from dsp_tools.xmllib.general_functions import create_standoff_link_to_resource
from dsp_tools.xmllib.general_functions import create_standoff_link_to_uri
from dsp_tools.xmllib.general_functions import escape_reserved_xml_characters
from dsp_tools.xmllib.general_functions import find_license_in_string
from dsp_tools.xmllib.general_functions import make_xsd_compatible_id_with_uuid
from dsp_tools.xmllib.models.config_options import NewlineReplacement
from dsp_tools.xmllib.models.licenses.other import LicenseOther
from dsp_tools.xmllib.models.licenses.recommended import License
from dsp_tools.xmllib.models.licenses.recommended import LicenseRecommended

NBSP = "\u00a0"


@pytest.fixture
def list_lookup() -> ListLookup:
    return ListLookup(
        _lookup={
            "list1": {"Label 1": "list1_node1", "Label 2": "list1_node2"},
            "list2": {"Label 1": "list2_node1", "Label 2": "list2_node2"},
        },
        _prop_to_list_name={
            "default:defaultOntoHasListOne": "list1",
            ":defaultOntoHasListOne": "list1",
            "other-onto:otherOntoHasListOne": "list1",
            "other-onto:otherOntoHasListTwo": "list2",
        },
        _label_language="en",
    )


class TestFootnotes:
    @pytest.mark.parametrize(
        ("input_text", "newline_replacement", "expected"),
        [
            ("Text", NewlineReplacement.NONE, "Text"),
            ("With escape &", NewlineReplacement.NONE, "With escape &amp;"),
            ("With escape <", NewlineReplacement.NONE, "With escape &lt;"),
            ("With escape >", NewlineReplacement.NONE, "With escape &gt;"),
            ("<With escape>", NewlineReplacement.LINEBREAK, "&lt;With escape&gt;"),
            ("Already escaped &lt;&gt;", NewlineReplacement.LINEBREAK, "Already escaped &lt;&gt;"),
            (
                "Non-ASCII àéèêëôû äöüß 0123456789 _-'()+=!?| 漢が글ርبيةб中",
                NewlineReplacement.NONE,
                "Non-ASCII àéèêëôû äöüß 0123456789 _-'()+=!?| 漢が글ርبيةб中",
            ),
        ],
    )
    def test_create_footnote_string_correct(
        self, input_text: str, newline_replacement: NewlineReplacement, expected: str
    ) -> None:
        result = create_footnote_string(input_text, newline_replacement)
        expected = f'<footnote content="{expected}"/>'
        assert result == expected

    @pytest.mark.parametrize(
        ("input_text", "newline_replacement", "expected_msg"),
        [
            (
                "Text",
                NewlineReplacement.PARAGRAPH,
                "Currently the only supported newline replacement is linebreak (<br/>) or None.",
            ),
            (pd.NA, NewlineReplacement.NONE, "The input value is empty."),
        ],
    )
    def test_create_footnote_string_raises(
        self, input_text: str, newline_replacement: NewlineReplacement, expected_msg: str
    ) -> None:
        with pytest.raises(XmllibInputError, match=regex.escape(expected_msg)):
            create_footnote_string(input_text, newline_replacement)


def test_create_standoff_link_to_resource_success() -> None:
    result = create_standoff_link_to_resource("id", "Text")
    assert result == '<a class="salsah-link" href="IRI:id:IRI">Text</a>'


def test_create_standoff_link_to_resource_id_empty() -> None:
    with pytest.raises(XmllibInputError):
        create_standoff_link_to_resource("", "Text")


def test_create_standoff_link_to_resource_text_empty() -> None:
    with pytest.raises(XmllibInputError):
        create_standoff_link_to_resource("id", "")


def test_create_standoff_link_to_uri_success() -> None:
    result = create_standoff_link_to_uri("https://uri.ch", "Text")
    assert result == '<a href="https://uri.ch">Text</a>'


def test_create_standoff_link_to_uri_empty() -> None:
    with pytest.raises(XmllibInputError):
        create_standoff_link_to_uri("", "Text")


def test_create_standoff_link_to_uri_text_empty() -> None:
    with pytest.raises(XmllibInputError):
        create_standoff_link_to_uri("https://uri.ch", "")


class TestCreateListFromString:
    def test_create_list_from_string_not_string(self) -> None:
        with pytest.raises(XmllibInputError):
            create_list_from_string("", "")

    @pytest.mark.parametrize(("input_value", "expected"), [("a, b", ["a", "b"]), ("", []), (1, ["1"])])
    def test_create_list_from_input(self, input_value, expected) -> None:
        result = create_list_from_input(input_value, ",")
        assert set(result) == set(expected)

    def test_create_non_empty_list_from_string_ok(self) -> None:
        result = create_non_empty_list_from_string("ab, cd , ", ",")
        assert set(result) == {"ab", "cd"}

    def test_create_non_empty_list_from_string_raises(self) -> None:
        msg = regex.escape(
            "The input for this function must result in a non-empty list. Your input results in an empty list."
        )
        with pytest.raises(XmllibInputError, match=msg):
            create_non_empty_list_from_string(" , ", ",")


class TestListLookup:
    def test_get_node_via_list_name(self, list_lookup):
        assert list_lookup.get_node_via_list_name("list1", "Label 1") == "list1_node1"

    def test_get_node_via_list_name_warns_wrong_list(self, list_lookup):
        msg = regex.escape("The entered list name 'inexistent' was not found. An empty string is returned.")
        with pytest.warns(XmllibInputWarning, match=msg):
            result = list_lookup.get_node_via_list_name("inexistent", "Label 1")
        assert result == ""

    def test_get_node_via_list_name_warns_wrong_node(self, list_lookup):
        msg = regex.escape(
            "'inexistent' was not recognised as label of the list 'list1'. "
            "This ListLookup is configured for 'en' labels."
        )
        with pytest.warns(XmllibInputWarning, match=msg):
            result = list_lookup.get_node_via_list_name("list1", "inexistent")
        assert result == ""

    def test_get_node_via_property(self, list_lookup):
        list_name, node_name = list_lookup.get_list_name_and_node_via_property(
            "other-onto:otherOntoHasListTwo", "Label 2"
        )
        assert list_name == "list2"
        assert node_name == "list2_node2"

    def test_get_node_via_property_warns_wrong_property(self, list_lookup):
        msg = regex.escape("The entered property ':inexistent' was not found. An empty string is returned.")
        with pytest.warns(XmllibInputWarning, match=msg):
            result = list_lookup.get_list_name_and_node_via_property(":inexistent", "Label 2")
        assert result == ("", "")


@pytest.mark.parametrize(
    ("input_val", "expected"),
    [
        ("Text no escape", "Text no escape"),
        ("known tag <strong>content</strong>", "known tag <strong>content</strong>"),
        ("Ampersand &", "Ampersand &amp;"),
        ("Unknow tags <unknown></unknown>", "Unknow tags &lt;unknown&gt;&lt;/unknown&gt;"),
        ("<text in brackets>", "&lt;text in brackets&gt;"),
    ],
)
def test_escape_reserved_xml_characters(input_val: str, expected: str) -> None:
    result = escape_reserved_xml_characters(input_val)
    assert result == expected


@pytest.mark.parametrize(
    ("input_val", "expected"),
    [
        ("Text after space", "Text after space"),
        ("\t Text\nafter newline", "Text after newline"),
        ("\n More text\r    with lots   of spaces    \n", "More text with lots of spaces"),
    ],
)
def test_clean_whitespaces_from_string(input_val: str, expected: str) -> None:
    result = clean_whitespaces_from_string(input_val)
    assert result == expected


def test_clean_whitespaces_from_string_warns() -> None:
    expected = regex.escape("The entered string is empty after all redundant whitespaces were removed.")
    with pytest.warns(XmllibInputWarning, match=expected):
        result = clean_whitespaces_from_string("   \r   \n\t ")
    assert result == ""


class TestFindLicense:
    @pytest.mark.parametrize(
        ("string", "expected"),
        [
            ("text Creative Commons BY 4.0 text", LicenseRecommended.CC.BY),
            ("text Creative Commons BY text", LicenseRecommended.CC.BY),
            ("text CC BY 4.0 text", LicenseRecommended.CC.BY),
            (f"text CC{NBSP}BY{NBSP}4.0 text", LicenseRecommended.CC.BY),
            ("text CC-BY-4.0 text", LicenseRecommended.CC.BY),
            ("text CC_BY_4.0 text", LicenseRecommended.CC.BY),
            ("text CC BY text", LicenseRecommended.CC.BY),
            ("text CC-BY text", LicenseRecommended.CC.BY),
            ("text CC_BY text", LicenseRecommended.CC.BY),
            ("CC BY 4.0", LicenseRecommended.CC.BY),
            ("CC BY", LicenseRecommended.CC.BY),
            ("CC-BY", LicenseRecommended.CC.BY),
        ],
    )
    def test_find_license_different_syntax(self, string: str, expected: License) -> None:
        assert find_license_in_string(string) == expected

    @pytest.mark.parametrize(
        ("string", "expected"),
        [
            ("text, CC BY, text", LicenseRecommended.CC.BY),
            (f"text, CC{NBSP}BY, text", LicenseRecommended.CC.BY),
            ("text. CC-BY. text", LicenseRecommended.CC.BY),
            ("text-CC BY-text", LicenseRecommended.CC.BY),
            ("text-CC-BY-text", LicenseRecommended.CC.BY),
            ("text (CC BY) text", LicenseRecommended.CC.BY),
        ],
    )
    def test_find_license_punctuation(self, string: str, expected: License) -> None:
        assert find_license_in_string(string) == expected

    @pytest.mark.parametrize(
        ("string", "expected"),
        [
            ("text CC BY text", LicenseRecommended.CC.BY),
            ("text CC BY ND text", LicenseRecommended.CC.BY_ND),
            ("text CC BY SA text", LicenseRecommended.CC.BY_SA),
            ("text CC BY NC text", LicenseRecommended.CC.BY_NC),
            ("text CC BY NC ND text", LicenseRecommended.CC.BY_NC_ND),
            ("text CC BY NC SA text", LicenseRecommended.CC.BY_NC_SA),
            (f"text CC{NBSP}BY{NBSP}NC{NBSP}SA text", LicenseRecommended.CC.BY_NC_SA),
        ],
    )
    def test_find_license_different_licenses(self, string: str, expected: License) -> None:
        assert find_license_in_string(string) == expected

    @pytest.mark.parametrize(
        ("string", "expected"),
        [
            ("text cc by text", LicenseRecommended.CC.BY),
            ("text cc by nd text", LicenseRecommended.CC.BY_ND),
            ("text cc by sa text", LicenseRecommended.CC.BY_SA),
            ("text cc by nc text", LicenseRecommended.CC.BY_NC),
            ("text cc by nc nd text", LicenseRecommended.CC.BY_NC_ND),
            ("text cc by nc sa text", LicenseRecommended.CC.BY_NC_SA),
        ],
    )
    def test_find_license_lowercase(self, string: str, expected: License) -> None:
        assert find_license_in_string(string) == expected

    @pytest.mark.parametrize(
        ("string", "expected"),
        [
            ("CC BY NC SA 1.0", LicenseRecommended.CC.BY_NC_SA),
            ("CC BY NC SA 2.0", LicenseRecommended.CC.BY_NC_SA),
            ("CC BY NC SA 3.1", LicenseRecommended.CC.BY_NC_SA),
            ("CC BY NC SA 10.20", LicenseRecommended.CC.BY_NC_SA),
        ],
    )
    def test_find_license_different_versions(self, string: str, expected: License) -> None:
        assert find_license_in_string(string) == expected

    def test_find_license_ignore_subsequent(self) -> None:
        assert find_license_in_string("CC BY and CC BY SA") == LicenseRecommended.CC.BY

    @pytest.mark.parametrize(
        ("string", "expected"),
        [
            ("CC SA BY 4.0", LicenseRecommended.CC.BY_SA),
            ("CC BY SA NC", LicenseRecommended.CC.BY_NC_SA),
            ("CC BY-ND-NC", LicenseRecommended.CC.BY_NC_ND),
        ],
    )
    def test_find_license_wrong_order(self, string: str, expected: License) -> None:
        assert find_license_in_string(string) == expected

    @pytest.mark.parametrize(
        "string",
        [
            "CC",
            "CC/BY/SA",
            "CC,BY,SA",
            "CC.BY.SA",
            "textCC-BY-SAtext",
            "CC BY BY",
            "CC BY NC NC",
        ],
    )
    def test_find_license_wrong_format(self, string: str) -> None:
        assert not find_license_in_string(string)

    @pytest.mark.parametrize("string", ["CC ND SA"])
    def test_find_license_non_existent(self, string: str) -> None:
        assert not find_license_in_string(string)

    @pytest.mark.parametrize(
        ("string", "expected"),
        [
            ("text AI Generated text", LicenseRecommended.DSP.AI_GENERATED),
            ("text ai generated text", LicenseRecommended.DSP.AI_GENERATED),
            ("text AI text", LicenseRecommended.DSP.AI_GENERATED),
            ("text ai text", LicenseRecommended.DSP.AI_GENERATED),
            ("text IA text", LicenseRecommended.DSP.AI_GENERATED),
            ("text ia text", LicenseRecommended.DSP.AI_GENERATED),
            ("text KI text", LicenseRecommended.DSP.AI_GENERATED),
            ("text ki text", LicenseRecommended.DSP.AI_GENERATED),
            ("textkitext", None),
            ("textKItext", None),
            ("textaitext", None),
            ("textAItext", None),
            ("textiatext", None),
            ("textIAtext", None),
        ],
    )
    def test_find_license_ai_generated(self, string: str, expected: License | None) -> None:
        assert find_license_in_string(string) == expected

    @pytest.mark.parametrize(
        ("string", "expected"),
        [
            ("text PUBLIC DOMAIN text", LicenseRecommended.DSP.PUBLIC_DOMAIN),
            ("text public domain text", LicenseRecommended.DSP.PUBLIC_DOMAIN),
            (f"text public{NBSP}domain text", LicenseRecommended.DSP.PUBLIC_DOMAIN),
            ("text GEMEINFREI text", LicenseRecommended.DSP.PUBLIC_DOMAIN),
            ("text gemeinfrei text", LicenseRecommended.DSP.PUBLIC_DOMAIN),
            ("text frei von Urheberrechten text", LicenseRecommended.DSP.PUBLIC_DOMAIN),
            ("text urheberrechtsbefreit text", LicenseRecommended.DSP.PUBLIC_DOMAIN),
            ("text libre de droits text", LicenseRecommended.DSP.PUBLIC_DOMAIN),
            ("text domaine public text", LicenseRecommended.DSP.PUBLIC_DOMAIN),
        ],
    )
    def test_find_public_domain(self, string: str, expected: License) -> None:
        assert find_license_in_string(string) == expected

    @pytest.mark.parametrize(
        ("string", "expected"),
        [
            ("text UNKNOWN text", LicenseRecommended.DSP.UNKNOWN),
            ("text unknown text", LicenseRecommended.DSP.UNKNOWN),
            ("text UNBEKANNT text", LicenseRecommended.DSP.UNKNOWN),
            ("text unbekannt text", LicenseRecommended.DSP.UNKNOWN),
            ("text INCONNU text", LicenseRecommended.DSP.UNKNOWN),
            ("text inconnu text", LicenseRecommended.DSP.UNKNOWN),
        ],
    )
    def test_find_unknown(self, string: str, expected: License) -> None:
        assert find_license_in_string(string) == expected

    @pytest.mark.parametrize(
        "string",
        [
            "text Creative Commons 0 1.0 text",
            "text CC 0 1.0 text",
            "text CC-0-1.0 text",
            "text CC-0 text",
            "text CC 0 text",
            "text CC_0_1.0 text",
            f"text CC{NBSP}0 text",
            f"text CC{NBSP}0{NBSP}1.0 text",
        ],
    )
    def test_find_cc_0(self, string: str) -> None:
        assert find_license_in_string(string) == LicenseOther.Public.CC_0_1_0

    @pytest.mark.parametrize(
        "string",
        [
            "text Creative Commons PDM 1.0 text",
            "text CC PDM 1.0 text",
            "text CC-PDM-1.0 text",
            "text CC-PDM text",
            "text CC PDM text",
            "text CC_PDM_1.0 text",
            f"text CC{NBSP}PDM text",
            f"text CC{NBSP}PDM{NBSP}1.0 text",
        ],
    )
    def test_find_public_domain_mark(self, string: str) -> None:
        assert find_license_in_string(string) == LicenseOther.Public.CC_PDM_1_0

    @pytest.mark.parametrize(
        "string",
        [
            "text BORIS Standard License text",
            f"text BORIS{NBSP}Standard{NBSP}License text",
            "text BORIS-Standard-License text",
            "text BORIS_Standard_License text",
            "text Bern Open Repository and Information System Standard License text",
        ],
    )
    def test_find_boris(self, string: str) -> None:
        assert find_license_in_string(string) == LicenseOther.Various.BORIS_STANDARD

    @pytest.mark.parametrize(
        "string",
        [
            "text LICENCE OUVERTE 2.0 text",
            "text licence ouverte text",
            f"text{NBSP}licence{NBSP}ouverte{NBSP}text",
            "text France-licence-ouverte text",
            "text Etalab Licence ouverte text",
        ],
    )
    def test_find_france_ouverte(self, string: str) -> None:
        assert find_license_in_string(string) == LicenseOther.Various.FRANCE_OUVERTE

    @pytest.mark.parametrize(
        ("iri", "lic"),
        [
            ("http://rdfh.ch/licenses/cc-by-4.0", LicenseRecommended.CC.BY),
            ("http://rdfh.ch/licenses/cc-by-nd-4.0", LicenseRecommended.CC.BY_ND),
            ("http://rdfh.ch/licenses/cc-by-nc-4.0", LicenseRecommended.CC.BY_NC),
            ("http://rdfh.ch/licenses/cc-by-nc-nd-4.0", LicenseRecommended.CC.BY_NC_ND),
            ("http://rdfh.ch/licenses/cc-by-nc-sa-4.0", LicenseRecommended.CC.BY_NC_SA),
            ("http://rdfh.ch/licenses/cc-by-sa-4.0", LicenseRecommended.CC.BY_SA),
            ("http://rdfh.ch/licenses/ai-generated", LicenseRecommended.DSP.AI_GENERATED),
            ("http://rdfh.ch/licenses/unknown", LicenseRecommended.DSP.UNKNOWN),
            ("http://rdfh.ch/licenses/public-domain", LicenseRecommended.DSP.PUBLIC_DOMAIN),
            ("http://rdfh.ch/licenses/cc-0-1.0", LicenseOther.Public.CC_0_1_0),
            ("http://rdfh.ch/licenses/cc-pdm-1.0", LicenseOther.Public.CC_PDM_1_0),
            ("http://rdfh.ch/licenses/boris", LicenseOther.Various.BORIS_STANDARD),
            ("http://rdfh.ch/licenses/open-licence-2.0", LicenseOther.Various.FRANCE_OUVERTE),
        ],
    )
    def test_find_license_already_parsed(self, iri: str, lic: License) -> None:
        assert find_license_in_string(iri) == lic

    def test_find_license_edge_cases(self) -> None:
        assert not find_license_in_string("BORIS")  # BORIS alone is not enough; must be followed by "Standard License"


def test_make_xsd_compatible_id() -> None:
    teststring = "0aüZ/_-äöü1234567890?`^':.;+*ç%&/()=±“#Ç[]|{}≠₂₃āṇśṣr̥ṁñἄ𝝺𝝲𝛆’الشعرُאדםПопрыгуньяşğ"  # noqa: RUF001
    _expected = "_0a_Z__-___1234567890_____.__________________________r______________________________"

    result_1 = make_xsd_compatible_id_with_uuid(teststring)
    result_2 = make_xsd_compatible_id_with_uuid(teststring)
    assert result_1 != result_2
    assert result_1.startswith(_expected)
    assert result_2.startswith(_expected)
    assert bool(regex.search(r"^[a-zA-Z_][\w.-]*$", result_1))
    assert bool(regex.search(r"^[a-zA-Z_][\w.-]*$", result_2))

    # test that invalid inputs lead to an error
    with pytest.raises(XmllibInputError):
        make_xsd_compatible_id_with_uuid(None)  # type: ignore[arg-type]

    with pytest.raises(XmllibInputError):
        make_xsd_compatible_id_with_uuid("")

    with pytest.raises(XmllibInputError):
        make_xsd_compatible_id_with_uuid(" ")
