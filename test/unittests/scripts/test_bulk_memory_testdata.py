from collections import Counter
from pathlib import Path

import pytest
from lxml import etree

from dsp_tools.commands.validate_data.models.input_problems import InputProblem
from dsp_tools.commands.validate_data.models.input_problems import ProblemType
from dsp_tools.commands.validate_data.models.input_problems import Severity
from scripts.bulk_memory_testdata.combine import SourceFile
from scripts.bulk_memory_testdata.combine import combine_xml_files
from scripts.bulk_memory_testdata.mix import mix_resources
from scripts.bulk_memory_testdata.multiply import multiply_resources
from scripts.bulk_memory_testdata.problem_types import group_problems_by_resource
from scripts.bulk_memory_testdata.xml_ids import get_references
from scripts.bulk_memory_testdata.xml_ids import get_resources
from scripts.bulk_memory_testdata.xml_ids import make_files_unique
from scripts.bulk_memory_testdata.xml_ids import rename_ids

NS = "https://dasch.swiss/schema"


def _root(body: str, default_ontology: str = "onto") -> etree._Element:
    xml = f'<knora xmlns="{NS}" shortcode="9999" default-ontology="{default_ontology}">{body}</knora>'
    return etree.fromstring(xml)


def _write(tmp_path: Path, name: str, body: str, default_ontology: str = "onto") -> Path:
    path = tmp_path / name
    path.write_bytes(etree.tostring(_root(body, default_ontology)))
    return path


def _ids(root: etree._Element) -> list[str]:
    return [res.attrib["id"] for res in get_resources(root)]


def _single(root: etree._Element, xpath: str) -> etree._Element:
    found: list[etree._Element] = root.xpath(xpath, namespaces={"k": NS})
    assert len(found) == 1
    return found[0]


LINKING_BODY = """
<permissions id="public"><allow group="UnknownUser">V</allow></permissions>
<authorship id="auth_1"><author>One</author></authorship>
<resource label="t" restype=":Thing" id="target"/>
<resource label="s" restype=":Thing" id="source" permissions="public">
    <resptr-prop name=":hasLink"><resptr permissions="public">target</resptr></resptr-prop>
    <resptr-prop name=":hasLink"><resptr>dangling</resptr></resptr-prop>
    <text-prop name=":hasRichtext">
        <text encoding="xml">A <a class="salsah-link" href="IRI:target:IRI">link</a>
        <footnote content="&lt;a href=&quot;IRI:target:IRI&quot;&gt;x&lt;/a&gt;"/></text>
    </text-prop>
</resource>
<region label="r" id="region"><resptr-prop name="isRegionOf"><resptr>target</resptr></resptr-prop></region>
<video-segment label="v" id="segment"><isSegmentOf>target</isSegmentOf><relatesTo>source</relatesTo></video-segment>
<resource label="f" restype=":Image" id="file">
    <bitstream authorship-id="auth_1">path/to/file.jpg</bitstream>
</resource>
<resource label="i" restype=":Image" id="iiif">
    <iiif-uri>https://iiif.example.org/abc.jp2/full/max/0/default.jpg</iiif-uri>
</resource>
"""


class TestXmlIds:
    def test_get_resources_includes_all_resource_kinds(self) -> None:
        assert _ids(_root(LINKING_BODY)) == ["target", "source", "region", "segment", "file", "iiif"]

    def test_get_references(self) -> None:
        source = get_resources(_root(LINKING_BODY))[1]
        assert get_references(source) == {"target", "dangling"}

    def test_get_references_of_segment(self) -> None:
        segment = get_resources(_root(LINKING_BODY))[3]
        assert get_references(segment) == {"target", "source"}

    def test_rename_ids_changes_ids_and_references(self) -> None:
        root = _root(LINKING_BODY)
        rename_ids(root, {"target": "x_target", "source": "x_source"}, {"public": "x_public"}, {"auth_1": "x_auth"})
        assert _single(root, "//k:permissions").attrib["id"] == "x_public"
        assert _single(root, "//k:authorship").attrib["id"] == "x_auth"
        source = _single(root, "//k:resource[@id='x_source']")
        assert source.attrib["permissions"] == "x_public"
        assert [x.text for x in source.iter(f"{{{NS}}}resptr")] == ["x_target", "dangling"]
        assert _single(source, ".//k:a").attrib["href"] == "IRI:x_target:IRI"
        assert "IRI:x_target:IRI" in _single(source, ".//k:footnote").attrib["content"]
        assert _single(root, "//k:isSegmentOf").text == "x_target"
        assert _single(root, "//k:relatesTo").text == "x_source"
        assert _single(root, "//k:bitstream").attrib["authorship-id"] == "x_auth"

    def test_rename_ids_keeps_absolute_iris(self) -> None:
        root = _root(
            '<resource label="a" restype=":T" id="a"><resptr-prop name=":l"><resptr>http://rdfh.ch/4123/x</resptr></resptr-prop></resource>'
        )
        rename_ids(root, {"a": "b"}, {}, {})
        assert _single(root, "//k:resptr").text == "http://rdfh.ch/4123/x"

    def test_make_files_unique(self) -> None:
        root = _root(LINKING_BODY)
        for res in get_resources(root):
            make_files_unique(res, "_c000007")
        assert _single(root, "//k:bitstream").text == "path/to/file_c000007.jpg"
        expected_iiif = "https://iiif.example.org/abc_c000007.jp2/full/max/0/default.jpg"
        assert _single(root, "//k:iiif-uri").text == expected_iiif

    def test_make_files_unique_keeps_empty_bitstream(self) -> None:
        root = _root('<resource label="a" restype=":T" id="a"><bitstream>   </bitstream></resource>')
        make_files_unique(get_resources(root)[0], "_x")
        assert _single(root, "//k:bitstream").text == "   "


class TestCombine:
    def test_prefixes_ids_and_merges(self, tmp_path: Path) -> None:
        first = _write(tmp_path, "a.xml", LINKING_BODY)
        second = _write(tmp_path, "b.xml", LINKING_BODY)
        root = combine_xml_files([SourceFile(first, "a"), SourceFile(second, "b")], "9999", "onto")
        assert root.attrib["default-ontology"] == "onto"
        assert root.attrib["shortcode"] == "9999"
        assert _ids(root)[:2] == ["a__target", "a__source"]
        assert _ids(root)[6:8] == ["b__target", "b__source"]
        resptrs = [x.text for x in _single(root, "//k:resource[@id='b__source']").iter(f"{{{NS}}}resptr")]
        assert resptrs == ["b__target", "dangling"]
        assert [x.attrib["id"] for x in root.iterchildren(f"{{{NS}}}permissions")] == ["a__public", "b__public"]

    def test_permissions_and_authorship_come_before_resources(self, tmp_path: Path) -> None:
        first = _write(tmp_path, "a.xml", LINKING_BODY)
        second = _write(tmp_path, "b.xml", LINKING_BODY)
        root = combine_xml_files([SourceFile(first, "a"), SourceFile(second, "b")], "9999", "onto")
        tags = [etree.QName(x).localname for x in root if isinstance(x.tag, str)]
        assert tags[:4] == ["permissions", "permissions", "authorship", "authorship"]

    def test_files_are_unique_per_source(self, tmp_path: Path) -> None:
        first = _write(tmp_path, "a.xml", LINKING_BODY)
        second = _write(tmp_path, "b.xml", LINKING_BODY)
        root = combine_xml_files([SourceFile(first, "a"), SourceFile(second, "b")], "9999", "onto")
        assert [x.text for x in root.iter(f"{{{NS}}}bitstream")] == ["path/to/file_a.jpg", "path/to/file_b.jpg"]

    def test_rewrites_other_default_ontology(self, tmp_path: Path) -> None:
        body = (
            '<resource label="a" restype=":Thing" id="a">'
            '<text-prop name=":hasText"><text>x</text></text-prop>'
            '<resptr-prop name="isPartOf"><resptr>a</resptr></resptr-prop>'
            "</resource>"
        )
        path = _write(tmp_path, "inbuilt.xml", body, default_ontology="in-built")
        root = combine_xml_files([SourceFile(path, "ib")], "9999", "onto")
        res = get_resources(root)[0]
        assert res.attrib["restype"] == "in-built:Thing"
        assert _single(res, ".//k:text-prop").attrib["name"] == "in-built:hasText"
        assert _single(res, ".//k:resptr-prop").attrib["name"] == "isPartOf"


class TestMultiply:
    def test_exact_count_and_equal_distribution(self) -> None:
        root = multiply_resources(_root(LINKING_BODY), 15)
        ids = _ids(root)
        assert len(ids) == 15
        counts = Counter(x.split("__c")[0] for x in ids)
        assert set(counts.values()) == {2, 3}

    def test_partial_copy_keeps_link_targets(self) -> None:
        root = multiply_resources(_root(LINKING_BODY), 8)
        ids = set(_ids(root))
        for res in get_resources(root):
            assert get_references(res) - {"dangling"} <= ids

    def test_partial_copy_with_cycle_points_to_first_copy(self) -> None:
        body = (
            '<resource label="a" restype=":T" id="a"><resptr-prop name=":l"><resptr>b</resptr></resptr-prop></resource>'
            '<resource label="b" restype=":T" id="b"><resptr-prop name=":l"><resptr>a</resptr></resptr-prop></resource>'
        )
        root = multiply_resources(_root(body), 3)
        assert _ids(root) == ["a__c000000", "b__c000000", "a__c000001"]
        assert get_references(get_resources(root)[2]) == {"b__c000000"}

    def test_rejects_target_below_base_count(self) -> None:
        with pytest.raises(ValueError, match="at least"):
            multiply_resources(_root(LINKING_BODY), 3)

    def test_references_point_to_same_copy(self) -> None:
        root = multiply_resources(_root(LINKING_BODY), 12)
        source = _single(root, "//k:resource[@id='source__c000001']")
        assert get_references(source) == {"target__c000001", "dangling"}

    def test_files_are_unique_per_copy(self) -> None:
        root = multiply_resources(_root(LINKING_BODY), 12)
        bitstreams = [x.text for x in root.iter(f"{{{NS}}}bitstream")]
        assert len(bitstreams) == len(set(bitstreams)) == 2

    def test_permissions_are_kept_once(self) -> None:
        root = multiply_resources(_root(LINKING_BODY), 12)
        assert len(list(root.iterchildren(f"{{{NS}}}permissions"))) == 1


FAILING_BODY = """
<resource label="t" restype=":Thing" id="helper"/>
<resource label="a" restype=":Thing" id="bad_link">
    <resptr-prop name=":l"><resptr>helper</resptr></resptr-prop>
</resource>
<resource label="b" restype=":Thing" id="bad_card_1"/>
<resource label="c" restype=":Thing" id="bad_card_2"/>
"""
CORRECT_BODY = '<resource label="ok" restype=":Thing" id="ok"/>'
PROBLEM_TYPES = {"bad_link": ["LINK"], "bad_card_1": ["CARD"], "bad_card_2": ["CARD", "CARD"]}


class TestMix:
    def test_counts(self) -> None:
        root, stats = mix_resources(_root(CORRECT_BODY), _root(FAILING_BODY), PROBLEM_TYPES, 100)
        assert len(_ids(root)) == 100
        assert stats.violating_resources == 20
        assert stats.helper_resources == 10
        assert stats.correct_resources == 70

    def test_each_problem_type_gets_the_same_share(self) -> None:
        _, stats = mix_resources(_root(CORRECT_BODY), _root(FAILING_BODY), PROBLEM_TYPES, 100)
        assert stats.error_units_by_type == {"LINK": 10, "CARD": 10}

    def test_round_robin_inside_a_type(self) -> None:
        _, stats = mix_resources(_root(CORRECT_BODY), _root(FAILING_BODY), PROBLEM_TYPES, 100)
        assert stats.expected_results_by_type == {"LINK": 10, "CARD": 15}

    def test_error_units_have_their_helpers(self) -> None:
        root, _ = mix_resources(_root(CORRECT_BODY), _root(FAILING_BODY), PROBLEM_TYPES, 100)
        ids = set(_ids(root))
        for res in get_resources(root):
            assert get_references(res) <= ids

    def test_is_deterministic(self) -> None:
        first, _ = mix_resources(_root(CORRECT_BODY), _root(FAILING_BODY), PROBLEM_TYPES, 100)
        second, _ = mix_resources(_root(CORRECT_BODY), _root(FAILING_BODY), PROBLEM_TYPES, 100)
        assert _ids(first) == _ids(second)

    def test_rejects_too_small_target(self) -> None:
        with pytest.raises(ValueError, match="too few"):
            mix_resources(_root(CORRECT_BODY), _root(FAILING_BODY), PROBLEM_TYPES, 2)


def test_group_problems_by_resource() -> None:
    problems = [
        InputProblem(ProblemType.MIN_CARD, "a", None, "p", Severity.VIOLATION),
        InputProblem(ProblemType.GENERIC, "b", None, "p", Severity.VIOLATION),
        InputProblem(ProblemType.GENERIC, "b", None, "p", Severity.VIOLATION),
        InputProblem(ProblemType.FILE_DUPLICATE, None, None, "p", Severity.WARNING),
    ]
    assert group_problems_by_resource(problems) == {"a": ["MIN_CARD"], "b": ["GENERIC", "GENERIC"]}
