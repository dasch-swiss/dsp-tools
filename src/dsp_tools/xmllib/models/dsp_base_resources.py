from __future__ import annotations

from collections.abc import Collection
from dataclasses import dataclass
from dataclasses import field
from typing import Any

from dsp_tools.error.xmllib_warnings import MessageInfo
from dsp_tools.error.xmllib_warnings_util import emit_xmllib_input_warning
from dsp_tools.error.xmllib_warnings_util import raise_input_error
from dsp_tools.xmllib.internal.checkers import check_and_warn_potentially_empty_string
from dsp_tools.xmllib.internal.input_converters import check_and_fix_collection_input
from dsp_tools.xmllib.models.config_options import NewlineReplacement
from dsp_tools.xmllib.models.config_options import Permissions
from dsp_tools.xmllib.models.internal.geometry import Circle
from dsp_tools.xmllib.models.internal.geometry import GeometryPoint
from dsp_tools.xmllib.models.internal.geometry import GeometryShape
from dsp_tools.xmllib.models.internal.geometry import Polygon
from dsp_tools.xmllib.models.internal.geometry import Rectangle
from dsp_tools.xmllib.models.internal.geometry import Vector
from dsp_tools.xmllib.models.internal.migration_metadata import MigrationMetadata
from dsp_tools.xmllib.models.internal.values import LinkValue
from dsp_tools.xmllib.models.internal.values import Richtext
from dsp_tools.xmllib.value_checkers import is_decimal
from dsp_tools.xmllib.value_checkers import is_nonempty_value

# ruff: noqa: D101, D102

LIST_SEPARATOR = "\n    - "


@dataclass
class RegionResource:
    res_id: str
    label: str
    region_of: LinkValue
    geometry: GeometryShape | None
    comments: list[Richtext] = field(default_factory=list)
    permissions: Permissions = Permissions.PROJECT_SPECIFIC_PERMISSIONS
    migration_metadata: MigrationMetadata | None = None

    def __post_init__(self) -> None:
        _check_strings(string_to_check=self.res_id, res_id=self.res_id, field_name="Resource ID")
        check_and_warn_potentially_empty_string(value=self.label, res_id=self.res_id, expected="string", field="label")

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
            region_of=LinkValue.new(
                value=region_of, prop_name="isRegionOf", resource_id=res_id, comment=None, permissions=permissions
            ),
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

    def add_comment(
        self,
        text: str,
        permissions: Permissions = Permissions.PROJECT_SPECIFIC_PERMISSIONS,
        comment: str | None = None,
        newline_replacement: NewlineReplacement = NewlineReplacement.LINEBREAK,
    ) -> RegionResource:
        """
        Add a comment to the region

        Args:
            text: text of the comment
            permissions: optional permissions of this value
            comment: optional comment about this comment
            newline_replacement: options how to deal with `\\n` inside the text value. Default: replace with `<br/>`

        Returns:
            The original region, with the added comment

        Examples:
            ```python
            region = region.add_comment("comment text")
            ```

            ```python
            region = region.add_comment(text="comment text", comment="Comment about the comment.")
            ```
        """
        self.comments.append(
            Richtext.new(
                value=text,
                prop_name="hasComment",
                permissions=permissions,
                comment=comment,
                resource_id=self.res_id,
                newline_replacement=newline_replacement,
            )
        )
        return self

    def add_comment_multiple(
        self,
        texts: Collection[str],
        permissions: Permissions = Permissions.PROJECT_SPECIFIC_PERMISSIONS,
        comment: str | None = None,
        newline_replacement: NewlineReplacement = NewlineReplacement.LINEBREAK,
    ) -> RegionResource:
        """
        Add several comments to the region

        Args:
            texts: list of texts
            permissions: optional permissions of these values
            comment: optional comment about these comments
            newline_replacement: options how to deal with `\\n` inside the text value. Default: replace with `<br/>`

        Returns:
            The original region, with the added comments

        Examples:
            ```python
            region = region.add_comment_multiple(["comment 1", "comment 2"])
            ```
        """
        vals = check_and_fix_collection_input(texts, "hasComment", self.res_id)
        comnts = [
            Richtext.new(
                value=x,
                prop_name="hasComment",
                permissions=permissions,
                comment=comment,
                resource_id=self.res_id,
                newline_replacement=newline_replacement,
            )
            for x in vals
        ]
        self.comments.extend(comnts)
        return self

    def add_comment_optional(
        self,
        text: Any,
        permissions: Permissions = Permissions.PROJECT_SPECIFIC_PERMISSIONS,
        comment: str | None = None,
        newline_replacement: NewlineReplacement = NewlineReplacement.LINEBREAK,
    ) -> RegionResource:
        """
        If the value is not empty, add it as comment, otherwise return the region unchanged.

        Args:
            text: text of the comment (or empty value)
            permissions: optional permissions of this value
            comment: optional comment about this comment
            newline_replacement: options how to deal with `\\n` inside the text value. Default: replace with `<br/>`

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
        if is_nonempty_value(text):
            return self.add_comment(text, permissions, comment, newline_replacement)
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
            msg_info = MessageInfo(
                "This resource already contains migration metadata, no new data can be added.", resource_id=self.res_id
            )
            raise_input_error(msg_info)
        self.migration_metadata = MigrationMetadata(creation_date=creation_date, iri=iri, ark=ark, res_id=self.res_id)
        return self


@dataclass
class LinkResource:
    res_id: str
    label: str
    link_to: list[LinkValue]
    comments: list[Richtext] = field(default_factory=list)
    permissions: Permissions = Permissions.PROJECT_SPECIFIC_PERMISSIONS
    migration_metadata: MigrationMetadata | None = None

    def __post_init__(self) -> None:
        _check_strings(string_to_check=self.res_id, res_id=self.res_id, field_name="Resource ID")
        check_and_warn_potentially_empty_string(value=self.label, res_id=self.res_id, expected="string", field="label")

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
        links_to = check_and_fix_collection_input(link_to, "hasLinkTo", res_id)
        link_vals = [
            LinkValue.new(value=x, prop_name="hasLinkTo", resource_id=res_id, comment=None, permissions=permissions)
            for x in links_to
        ]
        return LinkResource(
            res_id=res_id,
            label=label,
            link_to=link_vals,
            permissions=permissions,
        )

    def add_comment(
        self,
        text: str,
        permissions: Permissions = Permissions.PROJECT_SPECIFIC_PERMISSIONS,
        comment: str | None = None,
        newline_replacement: NewlineReplacement = NewlineReplacement.LINEBREAK,
    ) -> LinkResource:
        """
        Add a comment to the resource

        Args:
            text: text of the comment
            permissions: optional permissions of this value
            comment: optional comment about this comment
            newline_replacement: options how to deal with `\\n` inside the text value. Default: replace with `<br/>`

        Returns:
            The original resource, with the added comment

        Examples:
            ```python
            link_resource = link_resource.add_comment("comment text")
            ```

            ```python
            link_resource = link_resource.add_comment(text="comment text", comment="Comment about the comment.")
            ```
        """
        self.comments.append(
            Richtext.new(
                value=text,
                prop_name="hasComment",
                permissions=permissions,
                comment=comment,
                resource_id=self.res_id,
                newline_replacement=newline_replacement,
            )
        )
        return self

    def add_comment_multiple(
        self,
        texts: Collection[str],
        permissions: Permissions = Permissions.PROJECT_SPECIFIC_PERMISSIONS,
        comment: str | None = None,
        newline_replacement: NewlineReplacement = NewlineReplacement.LINEBREAK,
    ) -> LinkResource:
        """
        Add several comments to the resource

        Args:
            texts: list of texts
            permissions: optional permissions of these values
            comment: optional comment about this comment
            newline_replacement: options how to deal with `\\n` inside the text value. Default: replace with `<br/>`

        Returns:
            The original resource, with the added comments

        Examples:
            ```python
            link_resource = link_resource.add_comment_multiple(["comment 1", "comment 2"])
            ```
        """
        vals = check_and_fix_collection_input(texts, "hasComment", self.res_id)
        comnts = [
            Richtext.new(
                value=x,
                prop_name="hasComment",
                permissions=permissions,
                comment=comment,
                resource_id=self.res_id,
                newline_replacement=newline_replacement,
            )
            for x in vals
        ]
        self.comments.extend(comnts)
        return self

    def add_comment_optional(
        self,
        text: Any,
        permissions: Permissions = Permissions.PROJECT_SPECIFIC_PERMISSIONS,
        comment: str | None = None,
        newline_replacement: NewlineReplacement = NewlineReplacement.LINEBREAK,
    ) -> LinkResource:
        """
        If the value is not empty, add it as comment, otherwise return the resource unchanged.

        Args:
            text: text of the comment (or empty value)
            permissions: optional permissions of this value
            comment: optional comment about this comment
            newline_replacement: options how to deal with `\\n` inside the text value. Default: replace with `<br/>`

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
        if is_nonempty_value(text):
            return self.add_comment(text, permissions, comment, newline_replacement)
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
            msg_info = MessageInfo(
                "This resource already contains migration metadata, no new data can be added.", resource_id=self.res_id
            )
            raise_input_error(msg_info)
        self.migration_metadata = MigrationMetadata(creation_date=creation_date, iri=iri, ark=ark, res_id=self.res_id)
        return self


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
            wrng = f"{LIST_SEPARATOR}{LIST_SEPARATOR.join(msg)}"
            msg_info = MessageInfo(
                f"Segment bounds must be a float or integer. The following places have an unexpected type: {wrng}",
                self.res_id,
            )
            emit_xmllib_input_warning(msg_info)


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

    def __post_init__(self) -> None:
        _check_strings(string_to_check=self.res_id, res_id=self.res_id, field_name="Resource ID")
        check_and_warn_potentially_empty_string(value=self.label, res_id=self.res_id, expected="string", field="label")
        _check_strings(string_to_check=self.segment_of, res_id=self.res_id, prop_name="isSegmentOf")

    @staticmethod
    def create_new(
        res_id: str,
        label: str,
        segment_of: str,
        segment_start: float | int | str,
        segment_end: float | int | str,
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

    def add_comment(
        self,
        text: str,
    ) -> VideoSegmentResource:
        """
        Add a comment to the resource

        Args:
            text: text

        Returns:
            The original resource, with the added comment

        Examples:
            ```python
            video_segment = video_segment.add_comment("comment text")
            ```
        """
        self.comments.append(text)
        return self

    def add_comment_multiple(
        self,
        texts: Collection[str],
    ) -> VideoSegmentResource:
        """
        Add several comments to the resource

        Args:
            texts: list of texts

        Returns:
            The original resource, with the added comments

        Examples:
            ```python
            video_segment = video_segment.add_comment_multiple(["comment 1", "comment 2"])
            ```
        """
        vals = check_and_fix_collection_input(texts, "hasComment", self.res_id)
        self.comments.extend(vals)
        return self

    def add_comment_optional(
        self,
        text: Any,
    ) -> VideoSegmentResource:
        """
        If the value is not empty, add it as comment, otherwise return the resource unchanged.

        Args:
            text: text of the comment (or empty value)

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
        if is_nonempty_value(text):
            self.comments.append(text)
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
        vals = check_and_fix_collection_input(descriptions, "description", self.res_id)
        self.descriptions.extend(vals)
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
        vals = check_and_fix_collection_input(keywords, "keywords", self.res_id)
        self.keywords.extend(vals)
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
        vals = check_and_fix_collection_input(relates_to, "relatesTo", self.res_id)
        self.relates_to.extend(vals)
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
            msg_info = MessageInfo(
                "This resource already contains migration metadata, no new data can be added.", resource_id=self.res_id
            )
            raise_input_error(msg_info)
        self.migration_metadata = MigrationMetadata(creation_date=creation_date, iri=iri, ark=ark, res_id=self.res_id)
        return self


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

    def __post_init__(self) -> None:
        _check_strings(string_to_check=self.res_id, res_id=self.res_id, field_name="Resource ID")
        check_and_warn_potentially_empty_string(value=self.label, res_id=self.res_id, expected="string", field="label")
        _check_strings(string_to_check=self.segment_of, res_id=self.res_id, prop_name="isSegmentOf")

    @staticmethod
    def create_new(
        res_id: str,
        label: str,
        segment_of: str,
        segment_start: float | int | str,
        segment_end: float | int | str,
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

    def add_comment(self, text: str) -> AudioSegmentResource:
        """
        Add a comment to the resource

        Args:
            text: text of the comment

        Returns:
            The original resource, with the added comment

        Examples:
            ```python
            audio_segment = audio_segment.add_comment("comment text")
            ```
        """
        self.comments.append(text)
        return self

    def add_comment_multiple(self, texts: Collection[str]) -> AudioSegmentResource:
        """
        Add several comments to the resource

        Args:
            texts: list of texts

        Returns:
            The original resource, with the added comments

        Examples:
            ```python
            audio_segment = audio_segment.add_comment_multiple(["comment 1", "comment 2"])
            ```
        """
        vals = check_and_fix_collection_input(texts, "hasComment", self.res_id)
        self.comments.extend(vals)
        return self

    def add_comment_optional(self, text: Any) -> AudioSegmentResource:
        """
        If the value is not empty, add it as comment, otherwise return the resource unchanged.

        Args:
            text: text of the comment (or empty value)

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
        if is_nonempty_value(text):
            self.comments.append(text)
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
        vals = check_and_fix_collection_input(descriptions, "description", self.res_id)
        self.descriptions.extend(vals)
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
        vals = check_and_fix_collection_input(keywords, "keywords", self.res_id)
        self.keywords.extend(vals)
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
        vals = check_and_fix_collection_input(relates_to, "relatesTo", self.res_id)
        self.relates_to.extend(vals)
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
            msg_info = MessageInfo(
                "This resource already contains migration metadata, no new data can be added.", resource_id=self.res_id
            )
            raise_input_error(msg_info)
        self.migration_metadata = MigrationMetadata(creation_date=creation_date, iri=iri, ark=ark, res_id=self.res_id)
        return self


def _check_strings(
    *, string_to_check: str, res_id: str, prop_name: str | None = None, field_name: str | None = None
) -> None:
    if not is_nonempty_value(string_to_check):
        msg_info = MessageInfo("The entered string is not valid.", res_id, prop_name, field_name)
        emit_xmllib_input_warning(msg_info)


def _warn_value_exists(*, old_value: Any, new_value: Any, res_id: str | None, value_field: str | None = None) -> None:
    msg = (
        f"This resource already has a value in this location. "
        f"The old value '{old_value}' is being replace with '{new_value}'."
    )
    msg_info = MessageInfo(msg, res_id, field=value_field)
    emit_xmllib_input_warning(msg_info)
