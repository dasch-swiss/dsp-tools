from __future__ import annotations

import copy
from copy import deepcopy

from lxml import etree


def transform_into_localnames(root: etree._Element) -> etree._Element:
    """
    This function removes the namespace URIs from the elements' names

    Args:
        root: unclean tree

    Returns:
        cleaned tree
    """
    tree = deepcopy(root)
    for elem in tree.iter():
        elem.tag = etree.QName(elem).localname
    return tree


def remove_comments_from_element_tree(input_tree: etree._Element) -> etree._Element:
    """
    This function removes comments and processing instructions.
    Commented out properties break the XMLProperty constructor.

    Args:
        input_tree: etree root that will be cleaned

    Returns:
        clean xml
    """
    root = copy.deepcopy(input_tree)
    for c in root.xpath("//comment()"):
        c.getparent().remove(c)
    for c in root.xpath("//processing-instruction()"):
        c.getparent().remove(c)
    return root
