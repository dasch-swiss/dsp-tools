#!/usr/bin/env python3
"""
Validate documentation links in Python docstrings.

This script checks that all documentation links in the xmllib module
point to valid files (for internal DSP-TOOLS links) or valid URLs
(for external DSP-API links).

Usage:
    python scripts/validate_docstring_links.py
    just check-docstring-links

Exit codes:
    0: All links are valid
    1: One or more broken links found
"""

import re
import subprocess
import sys
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from urllib.parse import urlparse
from urllib.parse import urlunparse

import requests

from dsp_tools.setup.ansi_colors import BOLD_CYAN
from dsp_tools.setup.ansi_colors import BOLD_GREEN
from dsp_tools.setup.ansi_colors import BOLD_RED
from dsp_tools.setup.ansi_colors import RED
from dsp_tools.setup.ansi_colors import RESET_TO_DEFAULT


class LinkCategory(Enum):
    """Category of documentation link."""

    DSP_TOOLS_INTERNAL = "dsp-tools-internal"
    DSP_API_EXTERNAL = "dsp-api-external"
    OTHER = "other"


@dataclass
class LinkReference:
    """A documentation link found in source code."""

    file_path: Path
    line_number: int
    url: str
    category: LinkCategory


@dataclass
class ValidationResult:
    """Result of validating a link."""

    link: LinkReference
    error_type: str
    details: str


def main() -> None:
    """Main entry point for link validation."""
    # Determine repository root (script is in repo_root/scripts/)
    repo_root = Path(__file__).parent.parent
    xmllib_dir = repo_root / "src" / "dsp_tools" / "xmllib"
    docs_dir = repo_root / "docs"

    print(f"{BOLD_CYAN}Validating docstring links in xmllib...{RESET_TO_DEFAULT}\n")

    # Find all documentation links
    links = find_urls_in_docstrings(xmllib_dir)

    # Categorize links
    internal_links = [link for link in links if link.category == LinkCategory.DSP_TOOLS_INTERNAL]
    external_links = [link for link in links if link.category == LinkCategory.DSP_API_EXTERNAL]
    ignored_links = [link for link in links if link.category == LinkCategory.OTHER]

    print(f"Found {len(links)} documentation link(s):")
    print(f"  - Internal DSP-TOOLS: {len(internal_links)}")
    print(f"  - External DSP-API: {len(external_links)}")
    print(f"  - Other (ignored): {len(ignored_links)}")
    print()

    # Validate links
    errors: list[ValidationResult] = []

    print("Validating internal DSP-TOOLS links...")
    for link in internal_links:
        error = validate_internal_link(link, docs_dir)
        if error:
            errors.append(error)

    print("Validating external DSP-API links...")
    for link in external_links:
        error = validate_external_link(link)
        if error:
            errors.append(error)

    # Report results
    print()
    report_errors(errors)

    # Exit with appropriate code
    if errors:
        sys.exit(1)
    else:
        sys.exit(0)


def find_urls_in_docstrings(directory: Path) -> list[LinkReference]:
    """Use grep to find all documentation URLs with line numbers."""
    cmd = ["grep", "-rn", "https://docs.dasch.swiss", str(directory), "--include=*.py"]

    result = subprocess.run(cmd, capture_output=True, text=True)

    # Parse grep output
    url_pattern = re.compile(r"https://docs\.dasch\.swiss/[^\s\)>\]]+")
    links = []

    for line in result.stdout.splitlines():
        # Format: /path/to/file.py:123:    content with URL
        parts = line.split(":", 2)
        if len(parts) >= 3:
            file_path = Path(parts[0])
            line_number = int(parts[1])
            content = parts[2]

            # Find all URLs in this line
            for match in url_pattern.finditer(content):
                url = match.group(0)
                category = categorize_url(url)
                links.append(LinkReference(file_path, line_number, url, category))

    return links


def categorize_url(url: str) -> LinkCategory:
    """Determine category of documentation link."""
    if "docs.dasch.swiss/latest/DSP-TOOLS/" in url:
        return LinkCategory.DSP_TOOLS_INTERNAL
    elif "docs.dasch.swiss/latest/DSP-API/" in url:
        return LinkCategory.DSP_API_EXTERNAL
    else:
        return LinkCategory.OTHER


def validate_internal_link(link: LinkReference, docs_dir: Path) -> ValidationResult | None:
    """Validate internal DSP-TOOLS link against local file structure."""
    parsed = urlparse(link.url)
    path = parsed.path
    fragment = parsed.fragment

    # Extract relative path after /DSP-TOOLS/
    if "/DSP-TOOLS/" not in path:
        return ValidationResult(
            link=link, error_type="invalid_internal_url", details="URL doesn't contain /DSP-TOOLS/ path"
        )

    relative_path = path.split("/DSP-TOOLS/", 1)[1]
    relative_path = relative_path.rstrip("/")

    # Convert to markdown file path
    md_file_path = docs_dir / f"{relative_path}.md"

    # Check if file exists
    if not md_file_path.exists():
        return ValidationResult(
            link=link,
            error_type="missing_file",
            details=f"File not found: {md_file_path.relative_to(docs_dir.parent)}",
        )

    # Validate anchor if present
    if fragment:
        if not validate_anchor(md_file_path, fragment):
            return ValidationResult(
                link=link,
                error_type="missing_anchor",
                details=f"Anchor '#{fragment}' not found in {md_file_path.relative_to(docs_dir.parent)}",
            )

    return None


def validate_anchor(md_file: Path, anchor: str) -> bool:
    """Check if anchor exists in markdown file."""
    content = md_file.read_text(encoding="utf-8")

    # API reference anchors (contain dots) - trust mkdocstrings
    if "." in anchor:
        return "xmllib-docs" in str(md_file)

    # Header anchors - validate against actual headers
    header_pattern = re.compile(r"^#+\s+(.+)$", re.MULTILINE)
    headers = header_pattern.findall(content)

    def header_to_anchor(header: str) -> str:
        """Convert markdown header to anchor format."""
        clean = re.sub(r"[*`_]", "", header)
        anchor_text = clean.lower()
        anchor_text = re.sub(r"[^\w\s-]", "", anchor_text)
        anchor_text = re.sub(r"[-\s]+", "-", anchor_text)
        return anchor_text.strip("-")

    generated_anchors = {header_to_anchor(h) for h in headers}
    return anchor in generated_anchors


def validate_external_link(link: LinkReference) -> ValidationResult | None:
    """Validate external DSP-API link via HTTP request."""
    parsed = urlparse(link.url)
    url_without_anchor = urlunparse((parsed.scheme, parsed.netloc, parsed.path, parsed.params, parsed.query, ""))

    try:
        response = requests.head(
            url_without_anchor, timeout=10, allow_redirects=True, headers={"User-Agent": "dsp-tools-link-validator/1.0"}
        )

        if response.status_code in (200, 301, 302):
            return None
        else:
            return ValidationResult(
                link=link, error_type="http_error", details=f"HTTP {response.status_code} for {url_without_anchor}"
            )

    except requests.Timeout:
        return ValidationResult(
            link=link, error_type="timeout", details=f"Request timeout (10s) for {url_without_anchor}"
        )

    except requests.RequestException as e:
        return ValidationResult(link=link, error_type="network_error", details=f"Network error: {str(e)}")


def report_errors(errors: list[ValidationResult]) -> None:
    """Print formatted error messages."""
    if not errors:
        msg = "All docstring links are valid!"
        print(f"{BOLD_GREEN}{msg}{RESET_TO_DEFAULT}")
        return

    print(f"{BOLD_RED}Found {len(errors)} broken link(s):{RESET_TO_DEFAULT}\n")

    for idx, error in enumerate(errors, 1):
        print(f"{RED}[{idx}] {error.link.file_path}:{error.link.line_number}{RESET_TO_DEFAULT}")
        print(f"{RED}    URL: {error.link.url}{RESET_TO_DEFAULT}")
        print(f"{RED}    Error: {error.details}{RESET_TO_DEFAULT}")
        print()

    print(f"{BOLD_RED}Total errors: {len(errors)}{RESET_TO_DEFAULT}")
    msg = "Run 'just check-docstring-links' to validate links"
    print(f"{BOLD_RED}{msg}{RESET_TO_DEFAULT}")


if __name__ == "__main__":
    main()
