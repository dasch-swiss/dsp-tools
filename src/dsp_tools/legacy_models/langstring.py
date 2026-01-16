from dataclasses import dataclass
from enum import Enum
from enum import unique
from typing import Any

from dsp_tools.error.exceptions import BaseError


@unique
class Languages(Enum):
    """Languages supported by DSP"""

    EN = "en"
    DE = "de"
    FR = "fr"
    IT = "it"
    RM = "rm"


def _get_language_enum(lang_str: str) -> Languages:
    """Convert a language string to its enum, raising if invalid."""
    lang_map = {lang.value: lang for lang in Languages}
    lang_lower = lang_str.lower()
    if lang_lower not in lang_map:
        raise BaseError(f"Invalid language string '{lang_str}'")
    return lang_map[lang_lower]


@dataclass(frozen=True)
class LangString:
    """
    Holds language-dependent strings as used in JSON-LD.

    Either holds a dict mapping Languages to strings, or a simple string without language.
    """

    lang_strings: dict[Languages, str]
    simple_string: str | None

    def __getitem__(self, key: Languages | str | None = None) -> str | None:
        """Get a string by language. Falls back to any available string if not found."""
        if key is None:
            return self._get_any()
        if isinstance(key, str):
            key = _get_language_enum(key)
        if value := self.lang_strings.get(key):
            return value
        return self._get_fallback()

    def _get_any(self) -> str | None:
        """Return the simple string, or any language string if available."""
        if self.simple_string:
            return self.simple_string
        if self.lang_strings:
            return next(iter(self.lang_strings.values()))
        return None

    def _get_fallback(self) -> str | None:
        """Return any available string as fallback."""
        for value in self.lang_strings.values():
            if value is not None:
                return value
        return self.simple_string

    def items(self) -> Any:
        """Return items of the language strings dict."""
        return self.lang_strings.items()

    def is_empty(self) -> bool:
        """Check if this LangString has no content."""
        return not self.lang_strings and not self.simple_string

    def to_definition_file_obj(self) -> str | dict[str, str]:
        """Convert to format used in definition files."""
        if self.simple_string:
            return self.simple_string
        return {lang.value: value for lang, value in self.lang_strings.items()}


def create_lang_string(
    init_value: dict[Languages | str, str] | str | None = None,
) -> LangString:
    """Create a LangString from various input formats."""
    if init_value is None:
        return LangString(lang_strings={}, simple_string=None)
    if isinstance(init_value, str):
        return LangString(lang_strings={}, simple_string=init_value)
    if isinstance(init_value, dict):
        lang_strings: dict[Languages, str] = {}
        for key, value in init_value.items():
            if isinstance(key, Languages):
                lang_strings[key] = value
            elif isinstance(key, str):
                lang_strings[_get_language_enum(key)] = value
            else:
                raise BaseError("Not a valid language definition!")
        return LangString(lang_strings=lang_strings, simple_string=None)
    raise BaseError("Not a valid language definition!")


def create_lang_string_from_json_ld(
    obj: list[dict[str, str]] | dict[str, str] | str | None,
) -> LangString | None:
    """Create a LangString from JSON-LD format (uses @language/@value keys)."""
    if obj is None:
        return None
    if isinstance(obj, str):
        return LangString(lang_strings={}, simple_string=obj)
    objs = obj if isinstance(obj, list) else [obj]
    lang_strings: dict[Languages, str] = {}
    for item in objs:
        lang = item.get("@language")
        value = item.get("@value")
        if value is None:
            continue
        lang_enum = _try_get_language_enum(lang)
        if lang_enum is None:
            return LangString(lang_strings={}, simple_string=value)
        lang_strings[lang_enum] = value
    return LangString(lang_strings=lang_strings, simple_string=None)


def create_lang_string_from_json(
    obj: list[dict[str, str]] | dict[str, str] | str | None,
) -> LangString | None:
    """Create a LangString from JSON format (uses language/value keys)."""
    if obj is None:
        return None
    if isinstance(obj, str):
        return LangString(lang_strings={}, simple_string=obj)
    objs = obj if isinstance(obj, list) else [obj]
    lang_strings: dict[Languages, str] = {}
    for item in objs:
        lang = item.get("language")
        value = item.get("value")
        if value is None:
            continue
        lang_enum = _try_get_language_enum(lang)
        if lang_enum is None:
            return LangString(lang_strings={}, simple_string=value)
        lang_strings[lang_enum] = value
    return LangString(lang_strings=lang_strings, simple_string=None)


def _try_get_language_enum(lang: str | None) -> Languages | None:
    """Try to convert a language string to enum, returning None if invalid."""
    if lang is None:
        return None
    lang_map = {lang_enum.value: lang_enum for lang_enum in Languages}
    return lang_map.get(lang.lower())
