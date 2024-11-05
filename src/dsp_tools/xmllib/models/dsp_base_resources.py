from __future__ import annotations

import warnings
from dataclasses import dataclass
from dataclasses import field
from typing import Any

from lxml import etree

from dsp_tools.models.custom_warnings import DspToolsUserWarning
from dsp_tools.models.exceptions import InputError
from dsp_tools.xmllib.models.migration_metadata import MigrationMetadata
from dsp_tools.xmllib.models.user_enums import Permissions
from dsp_tools.xmllib.models.values import ColorValue
from dsp_tools.xmllib.models.values import LinkValue
from dsp_tools.xmllib.models.values import Richtext
from dsp_tools.xmllib.value_checkers import find_geometry_problem
from dsp_tools.xmllib.value_checkers import is_color
from dsp_tools.xmllib.value_checkers import is_decimal
from dsp_tools.xmllib.value_checkers import is_nonempty_value
from dsp_tools.xmllib.value_checkers import is_string_like

XML_NAMESPACE_MAP = {None: "https://dasch.swiss/schema", "xsi": "http://www.w3.org/2001/XMLSchema-instance"}
DASCH_SCHEMA = "{https://dasch.swiss/schema}"

LIST_SEPARATOR = "\n    - "


@dataclass
class AnnotationResource:
    """Represents an annotation to another resource of any class."""

    res_id: str
    label: str
    annotation_of: str
    comments: list[str]
    permissions: Permissions = Permissions.PROJECT_SPECIFIC_PERMISSIONS
    migration_metadata: MigrationMetadata | None = None

    def __post_init__(self) -> None:
        _check_strings(string_to_check=self.res_id, res_id=self.res_id, field_name="Resource ID")
        _check_strings(string_to_check=self.label, res_id=self.res_id, field_name="Label")

    @staticmethod
    def new(
        res_id: str,
        label: str,
        annotation_of: str,
        comments: list[str],
        permissions: Permissions = Permissions.PROJECT_SPECIFIC_PERMISSIONS,
    ) -> AnnotationResource:
        """
        Creates a new annotation resource.

        Args:
            res_id: Resource ID
            label: Resource Label
            annotation_of: Resource ID of which it is an annotation of (cardinality 1)
            comments: Comment to an annotation (cardinality 1-n)
            permissions: permission of the resource, default is `PROJECT_SPECIFIC_PERMISSIONS`

        Returns:
            An annotation resource
        """
        return AnnotationResource(
            res_id=res_id,
            label=label,
            annotation_of=annotation_of,
            comments=comments,
            permissions=permissions,
        )

    def add_comment(self, comment: str) -> AnnotationResource:
        """
        Add a comment to the resource

        Args:
            comment: Comment text

        Returns:
            The resource with one comment added.
        """
        self.comments.append(comment)
        return self

    def add_comment_multiple(self, comments: list[str]) -> AnnotationResource:
        """
        Add several comments to the resource

        Args:
            comments: List of comment texts

        Returns:
            The resource with several comments added.
        """
        self.comments.extend(comments)
        return self

    def add_comment_optional(self, comment: Any) -> AnnotationResource:
        """
        Add one comment if the value is not empty.

        Args:
            comment: Comment or empty value

        Returns:
            Resource with comment added if it is non-empty, otherwise an unchanged resource.
        """
        if is_nonempty_value(comment):
            self.comments.append(comment)
        return self

    def add_migration_metadata(
        self, creation_date: str | None, iri: str | None = None, ark: str | None = None
    ) -> AnnotationResource:
        """
        Add metadata from a SALSAH migration

        Args:
            creation_date: Creation date of the resource
            iri: Original IRI
            ark: Original ARK

        Raises:
            InputError if metadata already exists

        Returns:
            Resource with metadata added
        """
        if self.migration_metadata:
            raise InputError(
                f"The resource with the ID '{self.res_id}' already contains migration metadata, "
                f"no new data can be added."
            )
        self.migration_metadata = MigrationMetadata(creation_date=creation_date, iri=iri, ark=ark, res_id=self.res_id)
        return self

    def serialise(self) -> etree._Element:
        self.comments = _transform_unexpected_input(self.comments, "comments", self.res_id)
        res_ele = self._serialise_resource_element()
        res_ele.append(self._serialise_annotation_of())
        res_ele.append(_serialise_has_comment(self.comments, self.res_id))
        return res_ele

    def _serialise_resource_element(self) -> etree._Element:
        attribs = {"label": self.label, "id": self.res_id}
        if self.permissions != Permissions.PROJECT_SPECIFIC_PERMISSIONS:
            attribs["permissions"] = self.permissions.value
        return etree.Element(f"{DASCH_SCHEMA}annotation", attrib=attribs, nsmap=XML_NAMESPACE_MAP)

    def _serialise_annotation_of(self) -> etree._Element:
        return LinkValue(value=self.annotation_of, prop_name="isAnnotationOf", resource_id=self.res_id).serialise()


@dataclass
class RegionResource:
    """Represents a region of interest (ROI) in an image"""

    res_id: str
    label: str
    color: str
    region_of: str
    geometry: dict[str, Any]
    comments: list[str]
    permissions: Permissions = Permissions.PROJECT_SPECIFIC_PERMISSIONS
    migration_metadata: MigrationMetadata | None = None

    def __post_init__(self) -> None:
        _check_strings(string_to_check=self.res_id, res_id=self.res_id, field_name="Resource ID")
        _check_strings(string_to_check=self.label, res_id=self.res_id, field_name="Label")
        if not is_color(self.color):
            msg = (
                f"The color value '{self.color}' for the resource with the ID: '{self.res_id}' failed validation. "
                f"Please consult the documentation for details."
            )
            warnings.warn(DspToolsUserWarning(msg))
        if fail_msg := find_geometry_problem(self.geometry):
            msg = f"The geometry of the resource with the ID '{self.res_id}' failed validation.\n" + fail_msg
            warnings.warn(DspToolsUserWarning(msg))

    @staticmethod
    def new(
        res_id: str,
        label: str,
        color: str,
        region_of: str,
        geometry: dict[str, Any],
        comments: list[str],
        permissions: Permissions = Permissions.PROJECT_SPECIFIC_PERMISSIONS,
    ) -> RegionResource:
        """
        Creates a new region resource.

        Args:
            res_id: Resource ID
            label: Resource Label
            color: color of the region (cardinality 1)
            region_of: Resource if of which it is a region of (cardinality 1)
            geometry: Geometry information of the region (cardinality 1)
            comments: Comment to an annotation (cardinality 1-n)
            permissions: permission of the resource, default is `PROJECT_SPECIFIC_PERMISSIONS`

        Returns:
            A region resource
        """
        return RegionResource(
            res_id=res_id,
            label=label,
            color=color,
            region_of=region_of,
            geometry=geometry,
            comments=comments,
            permissions=permissions,
        )

    def add_comment(self, comment: str) -> RegionResource:
        """
        Add a comment to the resource

        Args:
            comment: Comment text

        Returns:
            The resource with one comment added.
        """
        self.comments.append(comment)
        return self

    def add_comment_multiple(self, comments: list[str]) -> RegionResource:
        """
        Add several comments to the resource

        Args:
            comments: List of comment texts

        Returns:
            The resource with several comments added.
        """
        self.comments.extend(comments)
        return self

    def add_comment_optional(self, comment: Any) -> RegionResource:
        """
        Add one comment if the value is not empty.

        Args:
            comment: Comment or empty value

        Returns:
            Resource with comment added if it is non-empty, otherwise an unchanged resource.
        """
        if is_nonempty_value(comment):
            self.comments.append(comment)
        return self

    def add_migration_metadata(
        self, creation_date: str | None, iri: str | None = None, ark: str | None = None
    ) -> RegionResource:
        """
        Add metadata from a SALSAH migration

        Args:
            creation_date: Creation date of the resource
            iri: Original IRI
            ark: Original ARK

        Raises:
            InputError if metadata already exists

        Returns:
            Resource with metadata added
        """
        if self.migration_metadata:
            raise InputError(
                f"The resource with the ID '{self.res_id}' already contains migration metadata, "
                f"no new data can be added."
            )
        self.migration_metadata = MigrationMetadata(creation_date=creation_date, iri=iri, ark=ark, res_id=self.res_id)
        return self

    def serialise(self) -> etree._Element:
        self.comments = _transform_unexpected_input(self.comments, "comments", self.res_id)
        res_ele = self._serialise_resource_element()
        res_ele.append(self._serialise_geometry())
        res_ele.extend(self._serialise_values())
        if self.comments:
            res_ele.append(_serialise_has_comment(self.comments, self.res_id))
        return res_ele

    def _serialise_resource_element(self) -> etree._Element:
        attribs = {"label": self.label, "id": self.res_id}
        if self.permissions != Permissions.PROJECT_SPECIFIC_PERMISSIONS:
            attribs["permissions"] = self.permissions.value
        return etree.Element(f"{DASCH_SCHEMA}region", attrib=attribs, nsmap=XML_NAMESPACE_MAP)

    def _serialise_values(self) -> list[etree._Element]:
        return [
            ColorValue(value=self.color, prop_name="hasColor", resource_id=self.res_id).serialise(),
            LinkValue(value=self.region_of, prop_name="isRegionOf", resource_id=self.res_id).serialise(),
        ]

    def _serialise_geometry(self) -> etree._Element:
        geo_prop = etree.Element(f"{DASCH_SCHEMA}geometry-prop", name="hasGeometry", nsmap=XML_NAMESPACE_MAP)
        ele = etree.Element(f"{DASCH_SCHEMA}geometry", nsmap=XML_NAMESPACE_MAP)
        ele.text = str(self.geometry)
        geo_prop.append(ele)
        return geo_prop


@dataclass
class LinkResource:
    """Represents a link between several other resources of different classes."""

    res_id: str
    label: str
    link_to: list[str]
    comments: list[str]
    permissions: Permissions = Permissions.PROJECT_SPECIFIC_PERMISSIONS
    migration_metadata: MigrationMetadata | None = None

    @staticmethod
    def new(
        res_id: str,
        label: str,
        link_to: list[str],
        comments: list[str],
        permissions: Permissions = Permissions.PROJECT_SPECIFIC_PERMISSIONS,
    ) -> LinkResource:
        """
        Creates a new link resource.
        All of these fields are required.
        Use the additional functions to add non-required information.

        Args:
            res_id: Resource ID
            label: Resource Label
            link_to: Resource IDs that should be linked together (cardinality 1-n)
            comments: Comment to an annotation (cardinality 1-n)
            permissions: permission of the resource, default is `PROJECT_SPECIFIC_PERMISSIONS`

        Returns:
            A link resource
        """
        return LinkResource(
            res_id=res_id,
            label=label,
            link_to=link_to,
            comments=comments,
            permissions=permissions,
        )

    def add_comment(self, comment: str) -> LinkResource:
        """
        Add a comment to the resource

        Args:
            comment: Comment text

        Returns:
            The resource with one comment added.
        """
        self.comments.append(comment)
        return self

    def add_comment_multiple(self, comments: list[str]) -> LinkResource:
        """
        Add several comments to the resource

        Args:
            comments: List of comment texts

        Returns:
            The resource with several comments added.
        """
        self.comments.extend(comments)
        return self

    def add_comment_optional(self, comment: Any) -> LinkResource:
        """
        Add one comment if the value is not empty.

        Args:
            comment: Comment or empty value

        Returns:
            Resource with comment added if it is non-empty, otherwise an unchanged resource.
        """
        if is_nonempty_value(comment):
            self.comments.append(comment)
        return self

    def add_migration_metadata(
        self, creation_date: str | None, iri: str | None = None, ark: str | None = None
    ) -> LinkResource:
        """
        Add metadata from a SALSAH migration

        Args:
            creation_date: Creation date of the resource
            iri: Original IRI
            ark: Original ARK

        Raises:
            InputError if metadata already exists

        Returns:
            Resource with metadata added
        """
        if self.migration_metadata:
            raise InputError(
                f"The resource with the ID '{self.res_id}' already contains migration metadata, "
                f"no new data can be added."
            )
        self.migration_metadata = MigrationMetadata(creation_date=creation_date, iri=iri, ark=ark, res_id=self.res_id)
        return self

    def serialise(self) -> etree._Element:
        self._check_for_and_convert_unexpected_input()
        res_ele = self._serialise_resource_element()
        res_ele.append(_serialise_has_comment(self.comments, self.res_id))
        res_ele.append(self._serialise_links())
        return res_ele

    def _check_for_and_convert_unexpected_input(self) -> None:
        _check_strings(string_to_check=self.res_id, res_id=self.res_id, field_name="Resource ID")
        _check_strings(string_to_check=self.label, res_id=self.res_id, field_name="Label")
        self.comments = _transform_unexpected_input(self.comments, "comments", self.res_id)
        self.link_to = _transform_unexpected_input(self.link_to, "link_to", self.res_id)

    def _serialise_resource_element(self) -> etree._Element:
        attribs = {"label": self.label, "id": self.res_id}
        if self.permissions != Permissions.PROJECT_SPECIFIC_PERMISSIONS:
            attribs["permissions"] = self.permissions.value
        return etree.Element(f"{DASCH_SCHEMA}link", attrib=attribs, nsmap=XML_NAMESPACE_MAP)

    def _serialise_links(self) -> etree._Element:
        prop_ele = etree.Element(f"{DASCH_SCHEMA}resptr-prop", name="hasLinkTo", nsmap=XML_NAMESPACE_MAP)
        vals = [LinkValue(value=x, prop_name="hasLinkTo", resource_id=self.res_id) for x in self.link_to]
        prop_ele.extend([v.make_element() for v in vals])
        return prop_ele


@dataclass
class SegmentBounds:
    segment_start: float | int | str
    segment_end: float | int | str
    res_id: str

    def __post_init__(self) -> None:
        msg: list[str] = []
        if not is_decimal(self.segment_start):
            msg.append(f"Segment Start Value: {self.segment_start} | Type: {type(self.segment_start)}")
        if not is_decimal(self.segment_end):
            msg.append(f"Segment End Value: {self.segment_end} | Type: {type(self.segment_start)}")
        if msg:
            title = (
                f"The resource with the ID: '{self.res_id}' expects a float or integer for segment bounds. "
                f"The following places have an unexpected type:"
            )
            wrng = f"{title}{LIST_SEPARATOR}{LIST_SEPARATOR.join(msg)}"
            warnings.warn(DspToolsUserWarning(wrng))


@dataclass
class VideoSegmentResource:
    """Represent sections of a video file."""

    res_id: str
    label: str
    segment_of: str
    segment_bounds: SegmentBounds
    title: str | None = None
    comments: list[str] = field(default_factory=list)
    descriptions: list[str] = field(default_factory=list)
    keywords: list[str] = field(default_factory=list)
    relates_to: list[str] = field(default_factory=list)
    permissions: Permissions = Permissions.PROJECT_SPECIFIC_PERMISSIONS
    migration_metadata: MigrationMetadata | None = None

    @staticmethod
    def new(
        res_id: str,
        label: str,
        segment_of: str,
        segment_start: float,
        segment_end: float,
        title: str | None = None,
        permissions: Permissions = Permissions.PROJECT_SPECIFIC_PERMISSIONS,
    ) -> VideoSegmentResource:
        """
        Creates a new video segment resource.
        All except title are required.
        Use the additional functions to add non-required information.

        Args:
            res_id: Resource ID
            label: Resource Label
            segment_of: Resource ID of which this is segment of (cardinality 1)
            segment_start: Start of the segment in seconds (cardinality 1)
            segment_end: End of the segment in seconds (cardinality 1)
            title: title of the segment, default `None` (cardinality 0-1)
            permissions: permission of the resource, default is `PROJECT_SPECIFIC_PERMISSIONS`

        Returns:
            A video segment resource
        """
        return VideoSegmentResource(
            res_id=res_id,
            label=label,
            segment_of=segment_of,
            segment_bounds=SegmentBounds(segment_start, segment_end, res_id),
            title=title,
            permissions=permissions,
        )

    def add_title(self, title: str) -> VideoSegmentResource:
        """
        Add a title to the resource.

        Args:
            title: Title text

        Warnings:
            If the resource already has a title.
            In that case, the title will be replaced.

        Returns:
            Resource
        """
        if self.title:
            _warn_value_exists(old_value=self.title, new_value=title, value_field="title", res_id=self.res_id)
        self.title = title
        return self

    def add_title_optional(self, title: Any) -> VideoSegmentResource:
        """
        Add a title if the value is non-empty.

        Args:
            title: Title

        Warnings:
            If the resource already has a title.
            In that case, the title will be replaced.

        Returns:
            Resource
        """
        if is_nonempty_value(title):
            if self.title:
                _warn_value_exists(old_value=self.title, new_value=title, value_field="title", res_id=self.res_id)
            self.title = title
        return self

    def add_comment(self, comment: str) -> VideoSegmentResource:
        """
        Add a comment to the resource

        Args:
            comment: Comment text

        Returns:
            The resource with one comment added.
        """
        self.comments.append(comment)
        return self

    def add_comment_multiple(self, comments: list[str]) -> VideoSegmentResource:
        """
        Add several comments to the resource

        Args:
            comments: List of comment texts

        Returns:
            The resource with several comments added.
        """
        self.comments.extend(comments)
        return self

    def add_comment_optional(self, comment: Any) -> VideoSegmentResource:
        """
        Add one comment if the value is not empty.

        Args:
            comment: Comment or empty value

        Returns:
            Resource with comment added if it is non-empty, otherwise an unchanged resource.
        """
        if is_nonempty_value(comment):
            self.comments.append(comment)
        return self

    def add_description(self, description: str) -> VideoSegmentResource:
        """
        Add a description to the resource

        Args:
            description: text

        Returns:
            Resource
        """
        self.descriptions.append(description)
        return self

    def add_description_multiple(self, descriptions: list[str]) -> VideoSegmentResource:
        self.descriptions.extend(descriptions)
        return self

    def add_description_optional(self, description: Any) -> VideoSegmentResource:
        if is_nonempty_value(description):
            self.descriptions.append(description)
        return self

    def add_keyword(self, keyword: str) -> VideoSegmentResource:
        """
        Add a keyword to the resource

        Args:
            keyword: text

        Returns:
            Resource
        """
        self.keywords.append(keyword)
        return self

    def add_keyword_multiple(self, keywords: list[str]) -> VideoSegmentResource:
        self.keywords.extend(keywords)
        return self

    def add_keyword_optional(self, keyword: Any) -> VideoSegmentResource:
        if is_nonempty_value(keyword):
            self.keywords.append(keyword)
        return self

    def add_relates_to(self, relates_to: str) -> VideoSegmentResource:
        """
        Add a link to a resource to which it relates to

        Args:
            relates_to: Resource ID to which it relates to

        Returns:
            Resource
        """
        self.relates_to.append(relates_to)
        return self

    def add_relates_to_multiple(self, relates_to: list[str]) -> VideoSegmentResource:
        self.relates_to.extend(relates_to)
        return self

    def add_relates_to_optional(self, relates_to: Any) -> VideoSegmentResource:
        if is_nonempty_value(relates_to):
            self.relates_to.append(relates_to)
        return self

    def add_migration_metadata(
        self, creation_date: str | None, iri: str | None = None, ark: str | None = None
    ) -> VideoSegmentResource:
        """
        Add metadata from a SALSAH migration

        Args:
            creation_date: Creation date of the resource
            iri: Original IRI
            ark: Original ARK

        Raises:
            InputError if metadata already exists

        Returns:
            Resource with metadata added
        """
        if self.migration_metadata:
            raise InputError(
                f"The resource with the ID '{self.res_id}' already contains migration metadata, "
                f"no new data can be added."
            )
        self.migration_metadata = MigrationMetadata(creation_date=creation_date, iri=iri, ark=ark, res_id=self.res_id)
        return self

    def serialise(self) -> etree._Element:
        self._check_for_and_convert_unexpected_input()
        res_ele = self._serialise_resource_element()
        res_ele.extend(_serialise_segment_children(self))
        return res_ele

    def _check_for_and_convert_unexpected_input(self) -> None:
        self.comments = _transform_unexpected_input(self.comments, "comments", self.res_id)
        self.descriptions = _transform_unexpected_input(self.descriptions, "descriptions", self.res_id)
        self.keywords = _transform_unexpected_input(self.keywords, "keywords", self.res_id)
        self.relates_to = _transform_unexpected_input(self.relates_to, "relates_to", self.res_id)
        _validate_segment(self)

    def _serialise_resource_element(self) -> etree._Element:
        attribs = {"label": self.label, "id": self.res_id}
        if self.permissions != Permissions.PROJECT_SPECIFIC_PERMISSIONS:
            attribs["permissions"] = self.permissions.value
        return etree.Element(f"{DASCH_SCHEMA}video-segment", attrib=attribs, nsmap=XML_NAMESPACE_MAP)


@dataclass
class AudioSegmentResource:
    """Represent sections of an audio file."""

    res_id: str
    label: str
    segment_of: str
    segment_bounds: SegmentBounds
    title: str | None = None
    comments: list[str] = field(default_factory=list)
    descriptions: list[str] = field(default_factory=list)
    keywords: list[str] = field(default_factory=list)
    relates_to: list[str] = field(default_factory=list)
    permissions: Permissions = Permissions.PROJECT_SPECIFIC_PERMISSIONS
    migration_metadata: MigrationMetadata | None = None

    @staticmethod
    def new(
        res_id: str,
        label: str,
        segment_of: str,
        segment_start: float,
        segment_end: float,
        title: str | None = None,
        permissions: Permissions = Permissions.PROJECT_SPECIFIC_PERMISSIONS,
    ) -> AudioSegmentResource:
        """
        Creates a new audio segment resource.
        All except title are required.
        Use the additional functions to add non-required information.

        Args:
            res_id: Resource ID
            label: Resource Label
            segment_of: Resource ID of which this is segment of (cardinality 1)
            segment_start: Start of the segment in seconds (cardinality 1)
            segment_end: End of the segment in seconds (cardinality 1)
            title: title of the segment, default `None` (cardinality 0-1)
            permissions: permission of the resource, default is `PROJECT_SPECIFIC_PERMISSIONS`

        Returns:
            A audio segment resource
        """
        return AudioSegmentResource(
            res_id=res_id,
            label=label,
            segment_of=segment_of,
            segment_bounds=SegmentBounds(segment_start, segment_end, res_id),
            title=title,
            permissions=permissions,
        )

    def add_title(self, title: str) -> AudioSegmentResource:
        """
        Add a title to the resource

        Args:
            title: text

        Returns:
            Resource
        """
        if self.title:
            _warn_value_exists(old_value=self.title, new_value=title, value_field="title", res_id=self.res_id)
        self.title = title
        return self

    def add_title_optional(self, title: Any) -> AudioSegmentResource:
        if is_nonempty_value(title):
            if self.title:
                _warn_value_exists(old_value=self.title, new_value=title, value_field="title", res_id=self.res_id)
            self.title = title
        return self

    def add_comment(self, comment: str) -> AudioSegmentResource:
        """
        Add a comment to the resource

        Args:
            comment: Comment text

        Returns:
            The resource with one comment added.
        """
        self.comments.append(comment)
        return self

    def add_comment_multiple(self, comments: list[str]) -> AudioSegmentResource:
        """
        Add several comments to the resource

        Args:
            comments: List of comment texts

        Returns:
            The resource with several comments added.
        """
        self.comments.extend(comments)
        return self

    def add_comment_optional(self, comment: Any) -> AudioSegmentResource:
        """
        Add one comment if the value is not empty.

        Args:
            comment: Comment or empty value

        Returns:
            Resource with comment added if it is non-empty, otherwise an unchanged resource.
        """
        if is_nonempty_value(comment):
            self.comments.append(comment)
        return self

    def add_description(self, description: str) -> AudioSegmentResource:
        """
        Add a description to the resource

        Args:
            description: text

        Returns:
            Resource
        """
        self.descriptions.append(description)
        return self

    def add_description_multiple(self, descriptions: list[str]) -> AudioSegmentResource:
        self.descriptions.extend(descriptions)
        return self

    def add_description_optional(self, description: Any) -> AudioSegmentResource:
        if is_nonempty_value(description):
            self.descriptions.append(description)
        return self

    def add_keyword(self, keyword: str) -> AudioSegmentResource:
        """
        Add a keyword to the resource

        Args:
            keyword: text

        Returns:
            Resource
        """
        self.keywords.append(keyword)
        return self

    def add_keyword_multiple(self, keywords: list[str]) -> AudioSegmentResource:
        self.keywords.extend(keywords)
        return self

    def add_keyword_optional(self, keyword: Any) -> AudioSegmentResource:
        if is_nonempty_value(keyword):
            self.keywords.append(keyword)
        return self

    def add_relates_to(self, relates_to: str) -> AudioSegmentResource:
        """
        Add a link to a resource to which it relates to

        Args:
            relates_to: Resource ID to which it relates to

        Returns:
            Resource
        """
        self.relates_to.append(relates_to)
        return self

    def add_relates_to_multiple(self, relates_to: list[str]) -> AudioSegmentResource:
        self.relates_to.extend(relates_to)
        return self

    def add_relates_to_optional(self, relates_to: Any) -> AudioSegmentResource:
        if is_nonempty_value(relates_to):
            self.relates_to.append(relates_to)
        return self

    def add_migration_metadata(
        self, creation_date: str | None, iri: str | None = None, ark: str | None = None
    ) -> AudioSegmentResource:
        """
        Add metadata from a SALSAH migration

        Args:
            creation_date: Creation date of the resource
            iri: Original IRI
            ark: Original ARK

        Raises:
            InputError if metadata already exists

        Returns:
            Resource with metadata added
        """
        if self.migration_metadata:
            raise InputError(
                f"The resource with the ID '{self.res_id}' already contains migration metadata, "
                f"no new data can be added."
            )
        self.migration_metadata = MigrationMetadata(creation_date=creation_date, iri=iri, ark=ark, res_id=self.res_id)
        return self

    def serialise(self) -> etree._Element:
        self._check_for_and_convert_unexpected_input()
        res_ele = self._serialise_resource_element()
        res_ele.extend(_serialise_segment_children(self))
        return res_ele

    def _check_for_and_convert_unexpected_input(self) -> None:
        self.comments = _transform_unexpected_input(self.comments, "comments", self.res_id)
        self.descriptions = _transform_unexpected_input(self.descriptions, "descriptions", self.res_id)
        self.keywords = _transform_unexpected_input(self.keywords, "keywords", self.res_id)
        self.relates_to = _transform_unexpected_input(self.relates_to, "relates_to", self.res_id)
        _validate_segment(self)

    def _serialise_resource_element(self) -> etree._Element:
        attribs = {"label": self.label, "id": self.res_id}
        if self.permissions != Permissions.PROJECT_SPECIFIC_PERMISSIONS:
            attribs["permissions"] = self.permissions.value
        return etree.Element(f"{DASCH_SCHEMA}audio-segment", attrib=attribs, nsmap=XML_NAMESPACE_MAP)


def _check_strings(string_to_check: str, res_id: str, field_name: str) -> None:
    if not is_string_like(string_to_check):
        msg = (
            f"The resource with the ID '{res_id}' has an invalid string at the following location:\n"
            f"Field: {field_name} | Value: {string_to_check}"
        )
        warnings.warn(DspToolsUserWarning(msg))


def _serialise_has_comment(comments: list[str], res_id: str) -> etree._Element:
    cmts = [Richtext(value=x, prop_name="hasComment", resource_id=res_id) for x in comments]
    cmt_prop = cmts[0].make_prop()
    cmt_prop.extend([cmt.make_element() for cmt in cmts])
    return cmt_prop


def _validate_segment(segment: AudioSegmentResource | VideoSegmentResource) -> None:
    problems = []
    if not is_string_like(segment.res_id):
        problems.append(f"Field: Resource ID | Value: {segment.res_id}")
    if not is_string_like(segment.label):
        problems.append(f"Field: label | Value: {segment.label}")
    if not is_string_like(segment.segment_of):
        problems.append(f"Field: segment_of | Value: {segment.segment_of}")
    if segment.title and not is_string_like(segment.title):
        problems.append(f"Field: title | Value: {segment.title}")
    if fails := [x for x in segment.comments if not is_string_like(x)]:
        problems.extend([f"Field: comment | Value: {x}" for x in fails])
    if fails := [x for x in segment.descriptions if not is_string_like(x)]:
        problems.extend([f"Field: description | Value: {x}" for x in fails])
    if fails := [x for x in segment.keywords if not is_string_like(x)]:
        problems.extend([f"Field: keywords | Value: {x}" for x in fails])
    if fails := [x for x in segment.relates_to if not is_string_like(x)]:
        problems.extend([f"Field: relates_to | Value: {x}" for x in fails])
    if problems:
        msg = f"The resource with the ID '{segment.res_id}' has the following problem(s):{'\n- '.join(problems)}"
        warnings.warn(DspToolsUserWarning(msg))


def _serialise_segment_children(segment: AudioSegmentResource | VideoSegmentResource) -> list[etree._Element]:
    segment_elements = []
    segment_of = etree.Element(f"{DASCH_SCHEMA}isSegmentOf", nsmap=XML_NAMESPACE_MAP)
    segment_of.text = segment.segment_of
    segment_elements.append(segment_of)
    segment_elements.append(
        etree.Element(
            f"{DASCH_SCHEMA}hasSegmentBounds",
            attrib={"start": str(segment.segment_bounds.segment_start), "end": str(segment.segment_bounds.segment_end)},
            nsmap=XML_NAMESPACE_MAP,
        )
    )
    if segment.title:
        segment_elements.append(_make_element_with_text("hasTitle", segment.title))
    segment_elements.extend([_make_element_with_text("hasComment", x) for x in segment.comments])
    segment_elements.extend([_make_element_with_text("hasDescription", x) for x in segment.descriptions])
    segment_elements.extend([_make_element_with_text("hasKeyword", x) for x in segment.keywords])
    segment_elements.extend([_make_element_with_text("relatesTo", x) for x in segment.relates_to])
    return segment_elements


def _make_element_with_text(tag_name: str, text_content: str) -> etree._Element:
    ele = etree.Element(f"{DASCH_SCHEMA}{tag_name}", nsmap=XML_NAMESPACE_MAP)
    ele.text = text_content
    return ele


def _transform_unexpected_input(value: Any, prop_name: str, res_id: str) -> list[str]:
    match value:
        case list():
            return value
        case set() | tuple():
            return list(value)
        case str():
            return [value]
        case _:
            _warn_unexpected_value(value=value, prop_name=prop_name, res_id=res_id)
            return [str(value)]


def _warn_unexpected_value(*, value: Any, prop_name: str, res_id: str | None) -> None:
    msg = (
        f"The resource: {res_id} should have a list of strings for the field '{prop_name}'. "
        f"Your input: '{value}' is of type {type(value)}."
    )
    warnings.warn(DspToolsUserWarning(msg))


def _warn_value_exists(*, old_value: Any, new_value: Any, value_field: str, res_id: str | None) -> None:
    """Emits a warning if a values is not in the expected format."""
    msg = (
        f"The resource with the ID '{res_id}' already has a value in the field '{value_field}'. "
        f"The old value '{old_value}' is being replace with '{new_value}'."
    )
    warnings.warn(DspToolsUserWarning(msg))
