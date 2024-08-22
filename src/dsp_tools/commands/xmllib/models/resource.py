from __future__ import annotations

import warnings
from collections import defaultdict
from dataclasses import dataclass
from dataclasses import field

from lxml import etree

from dsp_tools.commands.xmllib.models.values import FileValue
from dsp_tools.commands.xmllib.models.values import IntValue
from dsp_tools.commands.xmllib.models.values import LinkValue
from dsp_tools.commands.xmllib.models.values import SimpleText
from dsp_tools.commands.xmllib.models.values import Value
from dsp_tools.commands.xmllib.utils import is_string
from dsp_tools.models.custom_warnings import DspToolsUserWarning
from dsp_tools.models.exceptions import InputError

XML_NAMESPACE_MAP = {None: "https://dasch.swiss/schema", "xsi": "http://www.w3.org/2001/XMLSchema-instance"}
DASCH_SCHEMA = "{https://dasch.swiss/schema}"


@dataclass
class ResourceCollection:
    resources: dict[str, Resource] = field(default_factory=dict)

    def to_list(self) -> list[Resource]:
        return list(self.resources.values())

    def with_resource(self, resource: Resource) -> ResourceCollection:
        self._raise_exists(resource.res_id)
        self.resources[resource.res_id] = resource
        return self

    def with_empty_resource(self, res_id: str, restype: str, label: str) -> ResourceCollection:
        self._raise_exists(res_id)
        self.resources[res_id] = Resource(res_id=res_id, restype=restype, label=label)
        return self

    def add_value_to_resource(self, res_id: str, value: Value) -> ResourceCollection:
        self._raise_does_not_exist(res_id)
        self.resources[res_id].values.append(value)
        return self

    def add_file_value_to_resource(
        self, res_id: str, filepath: str, permissions: str | None = None, comment: str | None = None
    ) -> ResourceCollection:
        self._raise_does_not_exist(res_id)
        if self.resources[res_id].file_value:
            raise InputError(f"The resource with the ID: '{res_id}' already has a FileValue. Another cannot be added.")
        self.resources[res_id].file_value = FileValue(value=filepath, permissions=permissions, comment=comment)
        return self

    def _raise_exists(self, res_id: str) -> None:
        if res_id in self.resources:
            raise InputError(f"A resource with the ID: '{res_id}' already exists.")

    def _raise_does_not_exist(self, res_id: str) -> None:
        if res_id not in self.resources:
            raise InputError(f"Resource with ID '{res_id}' not found.")


@dataclass
class Resource:
    res_id: str
    restype: str
    label: str
    values: list[Value] = field(default_factory=list)
    permissions: str = "res-default"
    file_value: FileValue | None = None

    def __post_init__(self) -> None:
        if not is_string(str(self.label)):
            msg = (
                f"The label of a resource should be a string.\n"
                f"The label '{self.label}' of the resource with the ID {self.res_id} is not a string."
            )
            warnings.warn(DspToolsUserWarning(msg))

    def serialise(self) -> etree._Element:
        res_ele = self._make_resource_ele()
        if self.file_value:
            res_ele.append(self.file_value.serialise())
        res_ele.extend(self._serialise_values())
        return res_ele

    def _make_resource_ele(self) -> etree._Element:
        attribs = {"label": self.label, "restype": self.restype, "id": self.res_id}
        if self.permissions:
            attribs["permissions"] = self.permissions
        return etree.Element(f"{DASCH_SCHEMA}resource", attrib=attribs, nsmap=XML_NAMESPACE_MAP)

    def _serialise_values(self) -> list[etree._Element]:
        grouped = defaultdict(list)
        for val in self.values:
            grouped[val.prop_name].append(val)
        return [self._combine_values(prop_values) for prop_values in grouped.values()]

    @staticmethod
    def _combine_values(prop_values: list[Value]) -> etree._Element:
        prop_ = prop_values[0].make_prop()
        prop_eles = [x.make_element() for x in prop_values]
        prop_.extend(prop_eles)
        return prop_

    def with_int_value(
        self, prop_name: str, value: int | str, permissions: str | None = None, comments: str | None = None
    ) -> Resource:
        self.values.append(IntValue(value=value, prop_name=prop_name, permissions=permissions, comment=comments))
        return self

    def with_several_int_values(
        self, prop_name: str, values: list[int | str], permissions: str | None = None, comments: str | None = None
    ) -> Resource:
        inv_values = [IntValue(value=x, prop_name=prop_name, permissions=permissions, comment=comments) for x in values]
        self.values.extend(inv_values)
        return self

    def with_simple_text(
        self, prop_name: str, value: str, permissions: str | None = None, comments: str | None = None
    ) -> Resource:
        self.values.append(SimpleText(value=value, prop_name=prop_name, permissions=permissions, comment=comments))
        return self

    def with_several_simple_texts(
        self, prop_name: str, values: list[str], permissions: str | None = None, comments: str | None = None
    ) -> Resource:
        simple_text_values = [
            SimpleText(value=x, prop_name=prop_name, permissions=permissions, comment=comments) for x in values
        ]
        self.values.extend(simple_text_values)
        return self

    def with_link_value(
        self, prop_name: str, value: str, permissions: str | None = None, comments: str | None = None
    ) -> Resource:
        self.values.append(LinkValue(value=value, prop_name=prop_name, permissions=permissions, comment=comments))
        return self

    def with_several_link_values(
        self, prop_name: str, values: list[str], permissions: str | None = None, comments: str | None = None
    ) -> Resource:
        link_values = [
            LinkValue(value=x, prop_name=prop_name, permissions=permissions, comment=comments) for x in values
        ]
        self.values.extend(link_values)
        return self
