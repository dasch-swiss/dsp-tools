from pathlib import Path
from types import SimpleNamespace

import pytest
import requests

from scripts import validate_xmllib_docstring_links
from scripts.validate_xmllib_docstring_links import LinkCategory
from scripts.validate_xmllib_docstring_links import LinkReference
from scripts.validate_xmllib_docstring_links import _categorize_url
from scripts.validate_xmllib_docstring_links import _find_urls_in_docstrings
from scripts.validate_xmllib_docstring_links import _header_to_anchor
from scripts.validate_xmllib_docstring_links import _validate_anchor
from scripts.validate_xmllib_docstring_links import _validate_external_link
from scripts.validate_xmllib_docstring_links import _validate_internal_link
from scripts.validate_xmllib_docstring_links import main

INTERNAL_BASE = "https://docs.dasch.swiss/DSP-TOOLS"
EXTERNAL_URL = "https://docs.dasch.swiss/DSP-API/01-introduction/legal-info/"

DATA_FILE_MD = """\
# The XML data file

## Date

Some text.

### `xmllib` Functions, explained!

Some more text.
"""


def _internal_link(url: str) -> LinkReference:
    return LinkReference(Path("src/module.py"), 1, url, LinkCategory.DSP_TOOLS_INTERNAL)


def _external_link(url: str) -> LinkReference:
    return LinkReference(Path("src/module.py"), 1, url, LinkCategory.EXTERNAL)


@pytest.fixture
def docs_dir(tmp_path: Path) -> Path:
    docs = tmp_path / "docs"
    (docs / "data-file").mkdir(parents=True)
    (docs / "data-file" / "xml-data-file.md").write_text(DATA_FILE_MD, encoding="utf-8")
    (docs / "xmllib-docs").mkdir()
    (docs / "xmllib-docs" / "general-functions.md").write_text("::: xmllib.general_functions\n", encoding="utf-8")
    return docs


class TestHeaderToAnchor:
    def test_lowercases(self) -> None:
        assert _header_to_anchor("Date") == "date"

    def test_replaces_spaces_with_hyphens(self) -> None:
        assert _header_to_anchor("The XML data file") == "the-xml-data-file"

    def test_removes_markdown_formatting(self) -> None:
        assert _header_to_anchor("`xmllib` **Functions**") == "xmllib-functions"

    def test_removes_punctuation(self) -> None:
        assert _header_to_anchor("Functions, explained!") == "functions-explained"

    def test_collapses_hyphens_and_spaces(self) -> None:
        assert _header_to_anchor("Before -- after") == "before-after"

    def test_strips_leading_and_trailing_hyphens(self) -> None:
        assert _header_to_anchor("- Item -") == "item"


class TestCategorizeUrl:
    def test_dsp_tools_url_is_internal(self) -> None:
        url = f"{INTERNAL_BASE}/data-file/xml-data-file/#date"
        assert _categorize_url(url) == LinkCategory.DSP_TOOLS_INTERNAL

    def test_dsp_api_url_is_external(self) -> None:
        assert _categorize_url(EXTERNAL_URL) == LinkCategory.EXTERNAL


class TestValidateAnchor:
    def test_existing_header_anchor(self, docs_dir: Path) -> None:
        assert _validate_anchor(docs_dir / "data-file" / "xml-data-file.md", "date")

    def test_existing_header_anchor_with_formatting(self, docs_dir: Path) -> None:
        assert _validate_anchor(docs_dir / "data-file" / "xml-data-file.md", "xmllib-functions-explained")

    def test_missing_header_anchor(self, docs_dir: Path) -> None:
        assert not _validate_anchor(docs_dir / "data-file" / "xml-data-file.md", "boolean")

    def test_text_that_is_not_a_header_is_no_anchor(self, docs_dir: Path) -> None:
        assert not _validate_anchor(docs_dir / "data-file" / "xml-data-file.md", "some-text")

    def test_api_anchor_in_xmllib_docs(self, docs_dir: Path) -> None:
        md_file = docs_dir / "xmllib-docs" / "general-functions.md"
        assert _validate_anchor(md_file, "xmllib.general_functions.reformat_date")

    def test_api_anchor_outside_xmllib_docs(self, docs_dir: Path) -> None:
        md_file = docs_dir / "data-file" / "xml-data-file.md"
        assert not _validate_anchor(md_file, "xmllib.general_functions.reformat_date")


class TestValidateInternalLink:
    def test_existing_file(self, docs_dir: Path) -> None:
        link = _internal_link(f"{INTERNAL_BASE}/data-file/xml-data-file/")
        assert _validate_internal_link(link, docs_dir) is None

    def test_existing_file_without_trailing_slash(self, docs_dir: Path) -> None:
        link = _internal_link(f"{INTERNAL_BASE}/data-file/xml-data-file")
        assert _validate_internal_link(link, docs_dir) is None

    def test_existing_file_and_anchor(self, docs_dir: Path) -> None:
        link = _internal_link(f"{INTERNAL_BASE}/data-file/xml-data-file/#date")
        assert _validate_internal_link(link, docs_dir) is None

    def test_missing_file(self, docs_dir: Path) -> None:
        link = _internal_link(f"{INTERNAL_BASE}/data-file/no-such-file/")
        result = _validate_internal_link(link, docs_dir)
        assert result
        assert result.link == link
        assert result.error_type == "missing_file"
        assert "docs/data-file/no-such-file.md" in result.details

    def test_missing_anchor(self, docs_dir: Path) -> None:
        link = _internal_link(f"{INTERNAL_BASE}/data-file/xml-data-file/#boolean")
        result = _validate_internal_link(link, docs_dir)
        assert result
        assert result.error_type == "missing_anchor"
        assert "#boolean" in result.details

    def test_url_without_dsp_tools_path(self, docs_dir: Path) -> None:
        link = _internal_link(EXTERNAL_URL)
        result = _validate_internal_link(link, docs_dir)
        assert result
        assert result.error_type == "invalid_internal_url"


class TestFindUrlsInDocstrings:
    def test_finds_links_with_location_and_category(self, tmp_path: Path) -> None:
        source = tmp_path / "module.py"
        source.write_text(
            '"""\nNo link here.\n'
            f"See [the docs]({INTERNAL_BASE}/data-file/xml-data-file/#date) and <{EXTERNAL_URL}>.\n"
            '"""\n',
            encoding="utf-8",
        )
        links = _find_urls_in_docstrings(tmp_path)
        assert links == [
            LinkReference(source, 3, f"{INTERNAL_BASE}/data-file/xml-data-file/#date", LinkCategory.DSP_TOOLS_INTERNAL),
            LinkReference(source, 3, EXTERNAL_URL, LinkCategory.EXTERNAL),
        ]

    def test_searches_subdirectories(self, tmp_path: Path) -> None:
        source = tmp_path / "models" / "resource.py"
        source.parent.mkdir()
        source.write_text(f'"""See [the license docs]({EXTERNAL_URL})."""\n', encoding="utf-8")
        links = _find_urls_in_docstrings(tmp_path)
        assert [(link.file_path, link.url) for link in links] == [(source, EXTERNAL_URL)]

    def test_ignores_files_that_are_not_python(self, tmp_path: Path) -> None:
        (tmp_path / "module.py").write_text(f'"""See [the license docs]({EXTERNAL_URL})."""\n', encoding="utf-8")
        (tmp_path / "notes.md").write_text(f"{INTERNAL_BASE}/data-file/xml-data-file/\n", encoding="utf-8")
        links = _find_urls_in_docstrings(tmp_path)
        assert [link.url for link in links] == [EXTERNAL_URL]


class TestValidateExternalLink:
    @pytest.mark.parametrize("status_code", [200, 302])
    def test_ok_status(self, monkeypatch: pytest.MonkeyPatch, status_code: int) -> None:
        requested: list[tuple[str, dict[str, object]]] = []

        def fake_head(url: str, **kwargs: object) -> SimpleNamespace:
            requested.append((url, kwargs))
            return SimpleNamespace(status_code=status_code)

        monkeypatch.setattr(requests, "head", fake_head)
        assert _validate_external_link(_external_link(f"{EXTERNAL_URL}#section")) is None
        assert requested == [(EXTERNAL_URL, {"timeout": 10, "allow_redirects": True})]

    def test_http_error(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(requests, "head", lambda *_, **__: SimpleNamespace(status_code=404))
        link = _external_link(EXTERNAL_URL)
        result = _validate_external_link(link)
        assert result
        assert result.link == link
        assert result.error_type == "http_error"
        assert "HTTP 404" in result.details

    def test_timeout(self, monkeypatch: pytest.MonkeyPatch) -> None:
        def fake_head(*_: object, **__: object) -> SimpleNamespace:
            raise requests.Timeout

        monkeypatch.setattr(requests, "head", fake_head)
        result = _validate_external_link(_external_link(EXTERNAL_URL))
        assert result
        assert result.error_type == "timeout"

    def test_network_error(self, monkeypatch: pytest.MonkeyPatch) -> None:
        def fake_head(*_: object, **__: object) -> SimpleNamespace:
            raise requests.ConnectionError("name resolution failed")

        monkeypatch.setattr(requests, "head", fake_head)
        result = _validate_external_link(_external_link(EXTERNAL_URL))
        assert result
        assert result.error_type == "network_error"
        assert "name resolution failed" in result.details


class TestMain:
    def _patch_links(self, monkeypatch: pytest.MonkeyPatch, links: list[LinkReference]) -> None:
        monkeypatch.setattr(validate_xmllib_docstring_links, "_find_urls_in_docstrings", lambda _: links)

    def test_exits_without_error_when_no_links(
        self, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
    ) -> None:
        self._patch_links(monkeypatch, [])
        with pytest.raises(SystemExit) as exc_info:
            main()
        assert exc_info.value.code == 0
        assert "All xmllib docstring links are valid" in capsys.readouterr().out

    def test_exits_without_error_when_all_links_valid(self, monkeypatch: pytest.MonkeyPatch) -> None:
        self._patch_links(monkeypatch, [_external_link(EXTERNAL_URL)])
        monkeypatch.setattr(requests, "head", lambda *_, **__: SimpleNamespace(status_code=200))
        with pytest.raises(SystemExit) as exc_info:
            main()
        assert exc_info.value.code == 0

    def test_exits_with_error_on_broken_links(
        self, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
    ) -> None:
        broken_internal = _internal_link(f"{INTERNAL_BASE}/data-file/no-such-file/")
        broken_external = _external_link(EXTERNAL_URL)
        self._patch_links(monkeypatch, [broken_internal, broken_external])
        monkeypatch.setattr(requests, "head", lambda *_, **__: SimpleNamespace(status_code=404))
        with pytest.raises(SystemExit) as exc_info:
            main()
        assert exc_info.value.code == 1
        output = capsys.readouterr().out
        assert "Total errors: 2" in output
        assert "no-such-file.md" in output
        assert "HTTP 404" in output
