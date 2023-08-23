from typing import Optional, Union, cast

from lxml import etree
import regex

from dsp_tools.models.value import KnoraStandoffXml


class XMLValue:  # pylint: disable=too-few-public-methods
    """Represents a value of a resource property in the XML used for data import"""

    value: Union[str, KnoraStandoffXml]
    resrefs: Optional[list[str]]
    comment: Optional[str]
    permissions: Optional[str]

    def __init__(
        self,
        node: etree._Element,
        val_type: str,
        listname: Optional[str] = None,
    ) -> None:
        self.resrefs = None
        self.comment = node.get("comment")
        self.permissions = node.get("permissions")
        if val_type == "formatted-text":
            xmlstr_orig = etree.tostring(node, encoding="unicode", method="xml")
            xmlstr_cleaned = self._cleanup_formatted_text(xmlstr_orig)
            self.value = KnoraStandoffXml(xmlstr_cleaned)
            self.resrefs = list({x.split(":")[1] for x in self.value.get_all_iris() or []})
        elif val_type == "unformatted-text":
            str_orig = "".join(node.itertext())
            str_cleaned = self._cleanup_unformatted_text(str_orig)
            self.value = str_cleaned
        elif val_type == "list":
            listname = cast(str, listname)
            self.value = listname + ":" + "".join(node.itertext())
        else:
            self.value = "".join(node.itertext())

    def _cleanup_formatted_text(self, xmlstr_orig: str) -> str:
        """
        In a formatted text value from the XML file,
        there may be non-text characters that must be removed.
        This method:
            - removes the <text> tags
            - replaces (multiple) line breaks by spaces
            - replaces multiple spaces by a single space

        Args:
            xmlstr_orig: original string from the XML file

        Returns:
            purged string, suitable to be sent to DSP-API
        """
        # TODO: es gibt einen HTML-tag, um monospace darzustellen.
        # mehrfache leerschläge innerhalb von diesem tag müssen bestehen bleiben.
        xmlstr = regex.sub("<text.*?>", "", xmlstr_orig)
        xmlstr = regex.sub("</text>", "", xmlstr)
        xmlstr = regex.sub("\n+", " ", xmlstr)
        xmlstr = regex.sub(" +", " ", xmlstr)
        xmlstr = xmlstr.strip()
        return xmlstr

    def _cleanup_unformatted_text(self, string_orig: str) -> str:
        """
        In a unformatted text value from the XML file,
        there may be non-text characters that must be removed.
        This method:
            - removes the <text> tags
            - replaces multiple spaces or tabstops by a single space
            - replaces 3+ line breaks by 2 line breaks (=max. 1 empty line)

        Args:
            string_orig: original string from the XML file

        Returns:
            purged string, suitable to be sent to DSP-API
        """
        # remove the <text> tags
        string = regex.sub("<text.*?>", "", string_orig)
        string = regex.sub("</text>", "", string)

        # replace multiple spaces or tabstops by a single space
        string = regex.sub(r" {2,}|\t+", " ", string)

        # replace 3+ line breaks by 2 line breaks
        string = regex.sub(r"(\n ?){3,}", "\n\n", string)

        # remove leading and trailing spaces (of every line, but also of the entire string)
        string = "\n".join([s.strip() for s in string.split("\n")])
        string = string.strip()

        return string
