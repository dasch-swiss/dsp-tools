from __future__ import annotations

from dataclasses import dataclass


@dataclass
class FormattedTextValue:
    """Represents a formatted text value with standard standoff markup"""

    xmlstr: str
