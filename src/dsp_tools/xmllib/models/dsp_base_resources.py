from __future__ import annotations

import warnings
from collections.abc import Collection
from dataclasses import dataclass
from dataclasses import field
from typing import Any

from lxml import etree

from dsp_tools.models.custom_warnings import DspToolsUserWarning
from dsp_tools.models.exceptions import InputError
from dsp_tools.xmllib.models.config_options import Permissions
from dsp_tools.xmllib.models.geometry import Circle
from dsp_tools.xmllib.models.geometry import GeometryPoint
from dsp_tools.xmllib.models.geometry import GeometryShape
from dsp_tools.xmllib.models.geometry import Polygon
from dsp_tools.xmllib.models.geometry import Rectangle
from dsp_tools.xmllib.models.geometry import Vector
from dsp_tools.xmllib.models.migration_metadata import MigrationMetadata
from dsp_tools.xmllib.models.values import ColorValue
from dsp_tools.xmllib.models.values import LinkValue
from dsp_tools.xmllib.models.values import Richtext
from dsp_tools.xmllib.value_checkers import is_decimal
from dsp_tools.xmllib.value_checkers import is_nonempty_value
from dsp_tools.xmllib.value_checkers import is_string_like

# ruff: noqa: D101, D102

XML_NAMESPACE_MAP = {None: "https://dasch.swiss/schema", "xsi": "http://www.w3.org/2001/XMLSchema-instance"}
DASCH_SCHEMA = "{https://dasch.swiss/schema}"

LIST_SEPARATOR = "\n    - "


@dataclass
class RegionResource:
    res_id: str
    label: str
    region_of: str
    geometry: GeometryShape | None
    comments: list[str] = field(default_factory=list)
    permissions: Permissions = Permissions.PROJECT_SPECIFIC_PERMISSIONS
    migration_metadata: MigrationMetadata | None = None

    def __post_init__(self) -> None:
        _check_strings(string_to_check=self.res_id, res_id=self.res_id, field_name="Resource ID")
        _check_strings(string_to_check=self.label, res_id=self.res_id, field_name="Label")

    @staticmethod
    def create_new(
        res_id: str,
        label: str,
        region_of: str,
        permissions: Permissions = Permissions.PROJECT_SPECIFIC_PERMISSIONS,
    ) -> RegionResource:
        """
        Creates a new region resource.
        A region is a region of interest (ROI) in a StillImageRepresentation.

        Exactly one geometry shape has to be added to the resource with one of the following methods:
        `add_rectangle`, `add_polygon`, `add_circle` (see documentation below for more information).

        [See XML documentation for details](https://docs.dasch.swiss/latest/DSP-TOOLS/file-formats/xml-data-file/#region)

        Args:
            res_id: ID of this region resource
            label: label of this region resource
            region_of: ID of the image resource that this region refers to (cardinality 1)
            permissions: permissions of this region resource

        Returns:
            A region resource

        Examples:
            ```python
            region = xmllib.RegionResource.create_new(
                res_id="ID",
                label="label",
                region_of="image_id",
            )
            ```
        """
        return RegionResource(
            res_id=res_id,
            label=label,
            region_of=region_of,
            geometry=None,
            permissions=permissions,
        )

    def add_rectangle(
        self,
        point1: tuple[float, float],
        point2: tuple[float, float],
        line_width: float = 2,
        color: str = "#5b24bf",
        active: bool = True,
    ) -> RegionResource:
        """
        Add a rectangle shape to the region.

        [For a visual example see the XML documentation](https://docs.dasch.swiss/latest/DSP-TOOLS/file-formats/xml-data-file/#geometry)

        Args:
            point1: first point of the rectangle represented as two numbers between 0 and 1 in the format (x, y)
            point2: second point of the rectangle represented as two numbers between 0 and 1 in the format (x, y)
            line_width: A number in pixels between 1 - 5
            color: A hexadecimal color value which starts with a `#` followed by 3 or 6 numerals.
                The default value was chosen as it is distinguishable for most color-blind people.
            active: If set to `False`, the region is marked as 'deleted'

        Returns:
            Region with added rectangle

        Examples:
            ```python
            region = region.add_rectangle(
                point1=(0.1, 0.1),
                point2=(0.2, 0.2),
            )
            ```

            ```python
            # with custom display values
            region = region.add_rectangle(
                point1=(0.1, 0.1),
                point2=(0.2, 0.2),
                line_width=3,
                color="#32a873",
            )
            ```
        """
        self.geometry = Rectangle(
            point1=GeometryPoint(point1[0], point1[1], self.res_id),
            point2=GeometryPoint(point2[0], point2[1], self.res_id),
            line_width=line_width,
            color=color,
            active=active,
            resource_id=self.res_id,
        )
        return self

    def add_polygon(
        self,
        points: list[tuple[float, float]],
        line_width: float = 2,
        color: str = "#5b24bf",
        active: bool = True,
    ) -> RegionResource:
        """
        Add a polygon shape to the region.
        A polygon should have at least three points.
        If you wish to create a rectangle, please use the designated `add_rectangle` method.

        [For a visual example see the XML documentation](https://docs.dasch.swiss/latest/DSP-TOOLS/file-formats/xml-data-file/#geometry)

        **Please note that this cannot currently be displayed in the dsp-app.**

        Args:
            points: list of tuples containing two numbers between 0 and 1 in the format (x, y)
            line_width: A number in pixels between 1 - 5
            color: A hexadecimal color value which starts with a `#` followed by 3 or 6 numerals.
                The default value was chosen as it is distinguishable for most color-blind people.
            active: If set to `False` the region is marked as 'deleted'

        Returns:
            Region with added polygon

        Examples:
            ```python
            region = region.add_polygon(
                points=[(0.1, 0.1), (0.2, 0.2), (0.3, 0.3)],
            )
            ```

            ```python
            # with custom display values
            region = region.add_polygon(
                points=[(0.1, 0.1), (0.2, 0.2), (0.3, 0.3)],
                line_width=3,
                color="#32a873",
            )
            ```
        """
        geom_points = [GeometryPoint(val[0], val[1], self.res_id) for val in points]
        self.geometry = Polygon(
            points=geom_points, line_width=line_width, color=color, active=active, resource_id=self.res_id
        )
        return self

    def add_circle(
        self,
        center: tuple[float, float],
        radius: tuple[float, float],
        line_width: float = 2,
        color: str = "#5b24bf",
        active: bool = True,
    ) -> RegionResource:
        """
        Add a circle shape to the region.

        [For a visual example see the XML documentation](https://docs.dasch.swiss/latest/DSP-TOOLS/file-formats/xml-data-file/#geometry)

        **Please note that this cannot currently be displayed in the dsp-app.**

        Args:
            center: center of the circle, represented as two numbers between 0 and 1 in the format (x, y)
            radius: radius of the circle, represented as a 2-dimensional vector,
                i.e. two numbers between 0 and 1 in the format (x, y)
            line_width: A number in pixels between 1 - 5
            color: A hexadecimal color value which starts with a `#` followed by 3 or 6 numerals.
                The default value was chosen as it is distinguishable for most color-blind people.
            active: If set to `False` the region is marked as 'deleted'

        Returns:
            Region with added circle

        Examples:
            ```python
            region = region.add_circle(
                center=(0.1, 0.1),
                radius=(0.2, 0.2),
            )
            ```

            ```python
            # with custom display values
            region = region.add_circle(
                center=(0.1, 0.1),
                radius=(0.2, 0.2),
                line_width=3,
                color="#32a873",
            )
            ```
        """
        self.geometry = Circle(
            center=GeometryPoint(center[0], center[1], self.res_id),
            radius=Vector(radius[0], radius[1], self.res_id),
            line_width=line_width,
            color=color,
            active=active,
            resource_id=self.res_id,
        )
        return self

    def add_comment(self, comment: str) -> RegionResource:
        """
        Add a comment to the region

        Args:
            comment: text

        Returns:
            The original region, with the added comment

        Examples:
            ```python
            region = region.add_comment("comment text")
            ```
        """
        self.comments.append(comment)
        return self

    def add_comment_multiple(self, comments: Collection[str]) -> RegionResource:
        """
        Add several comments to the region

        Args:
            comments: list of texts

        Returns:
            The original region, with the added comments

        Examples:
            ```python
            region = region.add_comment_multiple(["comment 1", "comment 2"])
            ```
        """
        self.comments.extend(comments)
        return self

    def add_comment_optional(self, comment: Any) -> RegionResource:
        """
        If the value is not empty, add it as comment, otherwise return the region unchanged.

        Args:
            comment: text or empty value

        Returns:
            The original region, with the added comment

        Examples:
            ```python
            region = region.add_comment_optional("comment text")
            ```

            ```python
            region = region.add_comment_optional(None)
            ```
        """
        if is_nonempty_value(comment):
            self.comments.append(comment)
        return self

    def add_migration_metadata(
        self, creation_date: str | None, iri: str | None = None, ark: str | None = None
    ) -> RegionResource:
        """
        Add metadata from a SALSAH migration.

        Args:
            creation_date: creation date of the region in SALSAH
            iri: Original IRI in SALSAH
            ark: Original ARK in SALSAH

        Raises:
            InputError: if metadata already exists

        Returns:
            The original region, with the added metadata

        Examples:
            ```python
            region = region.add_migration_metadata(
                iri="http://rdfh.ch/4123/DiAmYQzQSzC7cdTo6OJMYA",
                creation_date="1999-12-31T23:59:59.9999999+01:00"
            )
            ```
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
        res_ele.extend(self._serialise_geometry_shape())
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
            LinkValue(value=self.region_of, prop_name="isRegionOf", resource_id=self.res_id).serialise(),
        ]

    def _serialise_geometry_shape(self) -> list[etree._Element]:
        prop_list: list[etree._Element] = []
        if not self.geometry:
            msg = (
                f"The region resource with the ID '{self.res_id}' does not have a geometry, "
                f"please note that an xmlupload will fail."
            )
            warnings.warn(DspToolsUserWarning(msg))

            return prop_list
        geo_prop = etree.Element(f"{DASCH_SCHEMA}geometry-prop", name="hasGeometry", nsmap=XML_NAMESPACE_MAP)
        ele = etree.Element(f"{DASCH_SCHEMA}geometry", nsmap=XML_NAMESPACE_MAP)
        ele.text = self.geometry.to_json_string()
        geo_prop.append(ele)
        prop_list.append(geo_prop)
        prop_list.append(
            ColorValue(value=self.geometry.color, prop_name="hasColor", resource_id=self.res_id).serialise(),
        )
        return prop_list


@dataclass
class LinkResource:
    res_id: str
    label: str
    link_to: list[str]
    comments: list[str] = field(default_factory=list)
    permissions: Permissions = Permissions.PROJECT_SPECIFIC_PERMISSIONS
    migration_metadata: MigrationMetadata | None = None

    @staticmethod
    def create_new(
        res_id: str,
        label: str,
        link_to: Collection[str],
        permissions: Permissions = Permissions.PROJECT_SPECIFIC_PERMISSIONS,
    ) -> LinkResource:
        """
        Creates a new link resource.
        A link resource is like a container that groups together several other resources of different classes.

        [See XML documentation for details](https://docs.dasch.swiss/latest/DSP-TOOLS/file-formats/xml-data-file/#link)

        Args:
            res_id: ID of this link resource
            label: label of this link resource
            link_to: IDs of the resources that should be linked together (cardinality 1-n)
            permissions: permissions of this link resource

        Returns:
            A link resource

        Examples:
            ```python
            link_resource = xmllib.LinkResource.create_new(
                res_id="ID",
                label="label",
                link_to=["target_resource_id_1", "target_resource_id_2"],
            )
            ```
        """
        return LinkResource(
            res_id=res_id,
            label=label,
            link_to=list(link_to),
            permissions=permissions,
        )

    def add_comment(self, comment: str) -> LinkResource:
        """
        Add a comment to the resource

        Args:
            comment: text

        Returns:
            The original resource, with the added comment

        Examples:
            ```python
            link_resource = link_resource.add_comment("comment text")
            ```
        """
        self.comments.append(comment)
        return self

    def add_comment_multiple(self, comments: Collection[str]) -> LinkResource:
        """
        Add several comments to the resource

        Args:
            comments: list of texts

        Returns:
            The original resource, with the added comments

        Examples:
            ```python
            link_resource = link_resource.add_comment_multiple(["comment 1", "comment 2"])
            ```
        """
        self.comments.extend(comments)
        return self

    def add_comment_optional(self, comment: Any) -> LinkResource:
        """
        If the value is not empty, add it as comment, otherwise return the resource unchanged.

        Args:
            comment: text or empty value

        Returns:
            The original resource, with the added comment

        Examples:
            ```python
            link_resource = link_resource.add_comment_optional("comment text")
            ```

            ```python
            link_resource = link_resource.add_comment_optional(None)
            ```
        """
        if is_nonempty_value(comment):
            self.comments.append(comment)
        return self

    def add_migration_metadata(
        self, creation_date: str | None, iri: str | None = None, ark: str | None = None
    ) -> LinkResource:
        """
        Add metadata from a SALSAH migration.

        Args:
            creation_date: creation date of the resource in SALSAH
            iri: Original IRI in SALSAH
            ark: Original ARK in SALSAH

        Raises:
            InputError: if metadata already exists

        Returns:
            The original resource, with the added metadata

        Examples:
            ```python
            link_resource = link_resource.add_migration_metadata(
                iri="http://rdfh.ch/4123/DiAmYQzQSzC7cdTo6OJMYA",
                creation_date="1999-12-31T23:59:59.9999999+01:00"
            )
            ```
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
        if self.comments:
            res_ele.append(_serialise_has_comment(self.comments, self.res_id))
        else:
            msg = (
                f"The link object with the ID '{self.res_id}' does not have any comments. "
                f"At least one comment must be provided, please note that an xmlupload will fail."
            )
            warnings.warn(DspToolsUserWarning(msg))
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
    def create_new(
        res_id: str,
        label: str,
        segment_of: str,
        segment_start: float,
        segment_end: float,
        permissions: Permissions = Permissions.PROJECT_SPECIFIC_PERMISSIONS,
    ) -> VideoSegmentResource:
        """
        Creates a new video segment resource, i.e. a time span of a MovingImageRepresentation.

        [See XML documentation for details](https://docs.dasch.swiss/latest/DSP-TOOLS/file-formats/xml-data-file/#video-segment-and-audio-segment)

        Args:
            res_id: ID of this video segment resource
            label: label of this video segment resource
            segment_of: ID of the video resource that this segment refers to (cardinality 1)
            segment_start: start of the segment in seconds (cardinality 1)
            segment_end: end of the segment in seconds (cardinality 1)
            permissions: permissions of this resource

        Returns:
            A video segment resource

        Examples:
            ```python
            video_segment = xmllib.VideoSegmentResource.create_new(
                res_id="ID",
                label="label",
                segment_of="video_resource_id",
                segment_start=1.2,
                segment_end=3.4,
            )
            ```
        """
        return VideoSegmentResource(
            res_id=res_id,
            label=label,
            segment_of=segment_of,
            segment_bounds=SegmentBounds(segment_start, segment_end, res_id),
            permissions=permissions,
        )

    def add_title(self, title: str) -> VideoSegmentResource:
        """
        Add a title to the resource.

        Args:
            title: text

        Returns:
            The original resource, with the added title

        Examples:
            ```python
            video_segment = video_segment.add_title("segment title")
            ```
        """
        if self.title:
            _warn_value_exists(old_value=self.title, new_value=title, value_field="title", res_id=self.res_id)
        self.title = title
        return self

    def add_title_optional(self, title: Any) -> VideoSegmentResource:
        """
        If the value is not empty, add it as title, otherwise return the resource unchanged.

        Args:
            title: text or empty value

        Returns:
            The original resource, with the added title

        Examples:
            ```python
            video_segment = video_segment.add_title("segment title")
            ```

            ```python
            video_segment = video_segment.add_title(None)
            ```
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
            comment: text

        Returns:
            The original resource, with the added comment

        Examples:
            ```python
            video_segment = video_segment.add_comment("comment text")
            ```
        """
        self.comments.append(comment)
        return self

    def add_comment_multiple(self, comments: Collection[str]) -> VideoSegmentResource:
        """
        Add several comments to the resource

        Args:
            comments: list of texts

        Returns:
            The original resource, with the added comments

        Examples:
            ```python
            video_segment = video_segment.add_comment_multiple(["comment 1", "comment 2"])
            ```
        """
        self.comments.extend(comments)
        return self

    def add_comment_optional(self, comment: Any) -> VideoSegmentResource:
        """
        If the value is not empty, add it as comment, otherwise return the resource unchanged.

        Args:
            comment: text or empty value

        Returns:
            The original resource, with the added comment

        Examples:
            ```python
            video_segment = video_segment.add_comment_optional("comment text")
            ```

            ```python
            video_segment = video_segment.add_comment_optional(None)
            ```
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
            The original resource, with the added description

        Examples:
            ```python
            video_segment = video_segment.add_description("description text")
            ```
        """
        self.descriptions.append(description)
        return self

    def add_description_multiple(self, descriptions: Collection[str]) -> VideoSegmentResource:
        """
        Add several descriptions to the resource

        Args:
            descriptions: list of texts

        Returns:
            The original resource, with the added descriptions

        Examples:
            ```python
            video_segment = video_segment.add_description_multiple(["description 1", "description 2"])
            ```
        """
        self.descriptions.extend(descriptions)
        return self

    def add_description_optional(self, description: Any) -> VideoSegmentResource:
        """
        If the value is not empty, add it as description, otherwise return the resource unchanged.

        Args:
            description: text or empty value

        Returns:
            The original resource, with the added description

        Examples:
            ```python
            video_segment = video_segment.add_description_optional("description text")
            ```

            ```python
            video_segment = video_segment.add_description_optional(None)
            ```
        """
        if is_nonempty_value(description):
            self.descriptions.append(description)
        return self

    def add_keyword(self, keyword: str) -> VideoSegmentResource:
        """
        Add a keyword to the resource

        Args:
            keyword: text

        Returns:
            The original resource, with the added keyword

        Examples:
            ```python
            video_segment = video_segment.add_keyword("keyword")
            ```
        """
        self.keywords.append(keyword)
        return self

    def add_keyword_multiple(self, keywords: Collection[str]) -> VideoSegmentResource:
        """
        Add several keywords to the resource

        Args:
            keywords: list of texts

        Returns:
            The original resource, with the added keywords

        Examples:
            ```python
            video_segment = video_segment.add_keyword_multiple(["keyword 1", "keyword 2"])
            ```
        """
        self.keywords.extend(keywords)
        return self

    def add_keyword_optional(self, keyword: Any) -> VideoSegmentResource:
        """
        If the value is not empty, add it as keyword, otherwise return the resource unchanged.

        Args:
            keyword: text or empty value

        Returns:
            The original resource, with the added keyword

        Examples:
            ```python
            video_segment = video_segment.add_keyword_optional("keyword")
            ```

            ```python
            video_segment = video_segment.add_keyword_optional(None)
            ```
        """
        if is_nonempty_value(keyword):
            self.keywords.append(keyword)
        return self

    def add_relates_to(self, relates_to: str) -> VideoSegmentResource:
        """
        Add a link to a related resource

        Args:
            relates_to: ID of the related resource

        Returns:
            The original resource, with the added related resource

        Examples:
            ```python
            video_segment = video_segment.add_relates_to("target_resource_id")
            ```
        """
        self.relates_to.append(relates_to)
        return self

    def add_relates_to_multiple(self, relates_to: Collection[str]) -> VideoSegmentResource:
        """
        Add several links to related resources

        Args:
            relates_to: list of IDs of the related resources

        Returns:
            The original resource, with the added related resources

        Examples:
            ```python
            video_segment = video_segment.add_relates_to_multiple(["target_resource_id_1", "target_resource_id_2"])
            ```
        """
        self.relates_to.extend(relates_to)
        return self

    def add_relates_to_optional(self, relates_to: Any) -> VideoSegmentResource:
        """
        If the value is not empty, add it as related resource, otherwise return the resource unchanged.

        Args:
            relates_to: ID or the related resource or empty value

        Returns:
            The original resource, with the added related resources

        Examples:
            ```python
            video_segment = video_segment.add_relates_to_optional("target_resource_id")
            ```

            ```python
            video_segment = video_segment.add_relates_to_optional(None)
            ```
        """
        if is_nonempty_value(relates_to):
            self.relates_to.append(relates_to)
        return self

    def add_migration_metadata(
        self, creation_date: str | None, iri: str | None = None, ark: str | None = None
    ) -> VideoSegmentResource:
        """
        Add metadata from a SALSAH migration.

        Args:
            creation_date: creation date of the resource in SALSAH
            iri: Original IRI in SALSAH
            ark: Original ARK in SALSAH

        Raises:
            InputError: if metadata already exists

        Returns:
            The original resource, with the added metadata

        Examples:
            ```python
            video_segment = video_segment.add_migration_metadata(
                iri="http://rdfh.ch/4123/DiAmYQzQSzC7cdTo6OJMYA",
                creation_date="1999-12-31T23:59:59.9999999+01:00"
            )
            ```
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
    def create_new(
        res_id: str,
        label: str,
        segment_of: str,
        segment_start: float,
        segment_end: float,
        permissions: Permissions = Permissions.PROJECT_SPECIFIC_PERMISSIONS,
    ) -> AudioSegmentResource:
        """
        Creates a new audio segment resource, i.e. a time span of an AudioRepresentation.

        [See XML documentation for details](https://docs.dasch.swiss/latest/DSP-TOOLS/file-formats/xml-data-file/#video-segment-and-audio-segment)

        Args:
            res_id: ID of this audio segment resource
            label: label of this audio segment resource
            segment_of: ID of the audio resource that this segment refers to (cardinality 1)
            segment_start: start of the segment in seconds (cardinality 1)
            segment_end: end of the segment in seconds (cardinality 1)
            permissions: permissions of this resource

        Returns:
            An audio segment resource
        """
        return AudioSegmentResource(
            res_id=res_id,
            label=label,
            segment_of=segment_of,
            segment_bounds=SegmentBounds(segment_start, segment_end, res_id),
            permissions=permissions,
        )

    def add_title(self, title: str) -> AudioSegmentResource:
        """
        Add a title to the resource.

        Args:
            title: text

        Returns:
            The original resource, with the added title

        Examples:
            ```python
            audio_segment = audio_segment.add_title("segment title")
            ```
        """
        if self.title:
            _warn_value_exists(old_value=self.title, new_value=title, value_field="title", res_id=self.res_id)
        self.title = title
        return self

    def add_title_optional(self, title: Any) -> AudioSegmentResource:
        """
        If the value is not empty, add it as title, otherwise return the resource unchanged.

        Args:
            title: text or empty value

        Returns:
            The original resource, with the added title

        Examples:
            ```python
            audio_segment = audio_segment.add_title("segment title")
            ```

            ```python
            audio_segment = audio_segment.add_title(None)
            ```
        """
        if is_nonempty_value(title):
            if self.title:
                _warn_value_exists(old_value=self.title, new_value=title, value_field="title", res_id=self.res_id)
            self.title = title
        return self

    def add_comment(self, comment: str) -> AudioSegmentResource:
        """
        Add a comment to the resource

        Args:
            comment: text

        Returns:
            The original resource, with the added comment

        Examples:
            ```python
            audio_segment = audio_segment.add_comment("comment text")
            ```
        """
        self.comments.append(comment)
        return self

    def add_comment_multiple(self, comments: Collection[str]) -> AudioSegmentResource:
        """
        Add several comments to the resource

        Args:
            comments: list of texts

        Returns:
            The original resource, with the added comments

        Examples:
            ```python
            audio_segment = audio_segment.add_comment_multiple(["comment 1", "comment 2"])
            ```
        """
        self.comments.extend(comments)
        return self

    def add_comment_optional(self, comment: Any) -> AudioSegmentResource:
        """
        If the value is not empty, add it as comment, otherwise return the resource unchanged.

        Args:
            comment: text or empty value

        Returns:
            The original resource, with the added comment

        Examples:
            ```python
            audio_segment = audio_segment.add_comment_optional("comment text")
            ```

            ```python
            audio_segment = audio_segment.add_comment_optional(None)
            ```
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
            The original resource, with the added description

        Examples:
            ```python
            audio_segment = audio_segment.add_description("description text")
            ```
        """
        self.descriptions.append(description)
        return self

    def add_description_multiple(self, descriptions: Collection[str]) -> AudioSegmentResource:
        """
        Add several descriptions to the resource

        Args:
            descriptions: list of texts

        Returns:
            The original resource, with the added descriptions

        Examples:
            ```python
            audio_segment = audio_segment.add_description_multiple(["description 1", "description 2"])
            ```
        """
        self.descriptions.extend(descriptions)
        return self

    def add_description_optional(self, description: Any) -> AudioSegmentResource:
        """
        If the value is not empty, add it as description, otherwise return the resource unchanged.

        Args:
            description: text or empty value

        Returns:
            The original resource, with the added description

        Examples:
            ```python
            audio_segment = audio_segment.add_description_optional("description text")
            ```

            ```python
            audio_segment = audio_segment.add_description_optional(None)
            ```
        """
        if is_nonempty_value(description):
            self.descriptions.append(description)
        return self

    def add_keyword(self, keyword: str) -> AudioSegmentResource:
        """
        Add a keyword to the resource

        Args:
            keyword: text

        Returns:
            The original resource, with the added keyword

        Examples:
            ```python
            audio_segment = audio_segment.add_keyword("keyword")
            ```
        """
        self.keywords.append(keyword)
        return self

    def add_keyword_multiple(self, keywords: Collection[str]) -> AudioSegmentResource:
        """
        Add several keywords to the resource

        Args:
            keywords: list of texts

        Returns:
            The original resource, with the added keywords

        Examples:
            ```python
            audio_segment = audio_segment.add_keyword_multiple(["keyword 1", "keyword 2"])
            ```
        """
        self.keywords.extend(keywords)
        return self

    def add_keyword_optional(self, keyword: Any) -> AudioSegmentResource:
        """
        If the value is not empty, add it as keyword, otherwise return the resource unchanged.

        Args:
            keyword: text or empty value

        Returns:
            The original resource, with the added keyword

        Examples:
            ```python
            audio_segment = audio_segment.add_keyword_optional("keyword")
            ```

            ```python
            audio_segment = audio_segment.add_keyword_optional(None)
            ```
        """
        if is_nonempty_value(keyword):
            self.keywords.append(keyword)
        return self

    def add_relates_to(self, relates_to: str) -> AudioSegmentResource:
        """
        Add a link to a related resource

        Args:
            relates_to: ID of the related resource

        Returns:
            The original resource, with the added related resource

        Examples:
            ```python
            audio_segment = audio_segment.add_relates_to("target_resource_id")
            ```
        """
        self.relates_to.append(relates_to)
        return self

    def add_relates_to_multiple(self, relates_to: Collection[str]) -> AudioSegmentResource:
        """
        Add several links to related resources

        Args:
            relates_to: list of IDs of the related resources

        Returns:
            The original resource, with the added related resources

        Examples:
            ```python
            audio_segment = audio_segment.add_relates_to_multiple(["target_resource_id_1", "target_resource_id_2"])
            ```
        """
        self.relates_to.extend(relates_to)
        return self

    def add_relates_to_optional(self, relates_to: Any) -> AudioSegmentResource:
        """
        If the value is not empty, add it as related resource, otherwise return the resource unchanged.

        Args:
            relates_to: ID of the related resource or empty value

        Returns:
            The original resource, with the added related resources

        Examples:
            ```python
            audio_segment = audio_segment.add_relates_to_optional("target_resource_id")
            ```

            ```python
            audio_segment = audio_segment.add_relates_to_optional(None)
            ```
        """
        if is_nonempty_value(relates_to):
            self.relates_to.append(relates_to)
        return self

    def add_migration_metadata(
        self, creation_date: str | None, iri: str | None = None, ark: str | None = None
    ) -> AudioSegmentResource:
        """
        Add metadata from a SALSAH migration.

        Args:
            creation_date: creation date of the resource in SALSAH
            iri: Original IRI in SALSAH
            ark: Original ARK in SALSAH

        Raises:
            InputError: if metadata already exists

        Returns:
            The original resource, with the added metadata

        Examples:
            ```python
            audio_segment = audio_segment.add_migration_metadata(
                iri="http://rdfh.ch/4123/DiAmYQzQSzC7cdTo6OJMYA",
                creation_date="1999-12-31T23:59:59.9999999+01:00"
            )
            ```
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
            attrib={
                "segment_start": str(segment.segment_bounds.segment_start),
                "segment_end": str(segment.segment_bounds.segment_end),
            },
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
