from pathlib import Path

import pytest
import regex

from dsp_tools.commands.excel2xml import excel2xml_cli
from dsp_tools.error.exceptions import BaseError

INVALID_EXCEL_DIRECTORY = "testdata/invalid-testdata/excel2xml"


@pytest.fixture
def expected_output() -> str:
    with open("testdata/excel2xml/excel2xml-expected-output.xml", encoding="utf-8") as f:
        return f.read()


class TestDifferentExtensions:
    def test_xlsx(self, expected_output: str) -> None:
        warn_msg = (
            "The excel2xml lib is deprecated in favor of the xmllib. It will be removed in a future release.\n"
            "See the xmllib docs: https://docs.dasch.swiss/latest/DSP-TOOLS/xmllib-api-reference/xmlroot/"
        )
        _, catched_warnings = excel2xml_cli.excel2xml(
            "testdata/excel2xml/excel2xml-testdata.xlsx", "1234", "excel2xml-output"
        )
        assert len(catched_warnings) == 1
        assert catched_warnings[0].message.args[0] == warn_msg  # type: ignore[union-attr]
        returned = Path("excel2xml-output-data.xml")
        assert returned.read_text() == expected_output
        returned.unlink(missing_ok=True)

    def test_xls(self, expected_output: str) -> None:
        warn_msg = (
            "The excel2xml lib is deprecated in favor of the xmllib. It will be removed in a future release.\n"
            "See the xmllib docs: https://docs.dasch.swiss/latest/DSP-TOOLS/xmllib-api-reference/xmlroot/"
        )
        _, catched_warnings = excel2xml_cli.excel2xml(
            "testdata/excel2xml/excel2xml-testdata.xls", "1234", "excel2xml-output"
        )
        assert len(catched_warnings) == 1
        assert catched_warnings[0].message.args[0] == warn_msg  # type: ignore[union-attr]
        returned = Path("excel2xml-output-data.xml")
        assert returned.read_text() == expected_output
        returned.unlink(missing_ok=True)

    def test_csv(self, expected_output: str) -> None:
        warn_msg = (
            "The excel2xml lib is deprecated in favor of the xmllib. It will be removed in a future release.\n"
            "See the xmllib docs: https://docs.dasch.swiss/latest/DSP-TOOLS/xmllib-api-reference/xmlroot/"
        )
        _, catched_warnings = excel2xml_cli.excel2xml(
            "testdata/excel2xml/excel2xml-testdata.csv", "1234", "excel2xml-output"
        )
        assert len(catched_warnings) == 1
        assert catched_warnings[0].message.args[0] == warn_msg  # type: ignore[union-attr]
        returned = Path("excel2xml-output-data.xml")
        assert returned.read_text() == expected_output
        returned.unlink(missing_ok=True)


class TestWarnings:
    def test_double_bool(self) -> None:
        file = f"{INVALID_EXCEL_DIRECTORY}/boolean-prop-two-values.xlsx"
        expected_msg = (
            "A <boolean-prop> can only have a single value, but resource "
            "'test_thing_1', property ':hasBoolean' (Excel row 6) contains more than one value."
        )
        _, catched_warnings = excel2xml_cli.excel2xml(file, "1234", "excel2xml-invalid")
        assert len(catched_warnings) == 2
        catched = catched_warnings[0].message.args[0]  # type:ignore[union-attr]
        assert catched == expected_msg

    def test_missing_child(self) -> None:
        file = f"{INVALID_EXCEL_DIRECTORY}/empty-property.xlsx"
        expected_missing_prop = regex.escape(
            "At least one value per property is required, but resource 'person_0', property ':hasName' "
            "(Excel row 3) doesn't contain any values."
        )
        expected_validation = regex.escape("Element 'text-prop': Missing child element(s). Expected is ( text ).")
        _, catched_warnings = excel2xml_cli.excel2xml(file, "1234", "excel2xml-invalid")
        assert len(catched_warnings) == 3
        message_missing_prop = catched_warnings[0].message.args[0]  # type:ignore[union-attr]
        assert regex.search(expected_missing_prop, message_missing_prop)
        message_xml_validation = catched_warnings[2].message.args[0]  # type:ignore[union-attr]
        assert regex.search(expected_validation, message_xml_validation)

    def test_missing_prop_permission(self) -> None:
        file = f"{INVALID_EXCEL_DIRECTORY}/missing-prop-permissions.xlsx"
        expected_msg = "Resource 'person_0': Missing permissions in column '2_permissions' of property ':hasName'"
        _, catched_warnings = excel2xml_cli.excel2xml(file, "1234", "excel2xml-invalid")
        assert len(catched_warnings) == 2
        message = catched_warnings[0].message.args[0]  # type:ignore[union-attr]
        assert message == expected_msg

    def test_missing_label(self) -> None:
        file = f"{INVALID_EXCEL_DIRECTORY}/missing-resource-label.xlsx"
        expected_msg_missing = "Missing label for resource 'person_0' (Excel row 2)"
        expected_xml_validation = regex.escape(
            "Element 'resource', attribute 'label': [facet 'minLength'] The value '' has a length of '0'"
        )
        _, catched_warnings = excel2xml_cli.excel2xml(file, "1234", "excel2xml-invalid")
        assert len(catched_warnings) == 3
        msg_missing_label = catched_warnings[0].message.args[0]  # type:ignore[union-attr]
        assert msg_missing_label == expected_msg_missing
        msg_validation = catched_warnings[2].message.args[0]  # type:ignore[union-attr]
        assert regex.search(expected_xml_validation, msg_validation)

    def test_missing_resource_permission(self) -> None:
        file = f"{INVALID_EXCEL_DIRECTORY}/missing-resource-permissions.xlsx"
        expected_msg = "Missing permissions for resource 'person_0' (Excel row 2)"
        expected_xml_validation = regex.escape(
            "Element 'resource', attribute 'permissions': '' is not a valid value of the atomic type 'xs:IDREF'."
        )
        _, catched_warnings = excel2xml_cli.excel2xml(file, "1234", "excel2xml-invalid")
        assert len(catched_warnings) == 3
        message = catched_warnings[0].message.args[0]  # type:ignore[union-attr]
        assert message == expected_msg
        msg_validation = catched_warnings[2].message.args[0]  # type:ignore[union-attr]
        assert regex.search(expected_xml_validation, msg_validation)

    def test_missing_restype(self) -> None:
        file = f"{INVALID_EXCEL_DIRECTORY}/missing-restype.xlsx"
        expected_msg = "Missing restype for resource 'person_0' (Excel row 2)"
        _, catched_warnings = excel2xml_cli.excel2xml(file, "1234", "excel2xml-invalid")
        assert len(catched_warnings) == 2
        message = catched_warnings[0].message.args[0]  # type:ignore[union-attr]
        assert message == expected_msg

    def test_missing_bitstream_permission(self) -> None:
        file = f"{INVALID_EXCEL_DIRECTORY}/no-bitstream-permissions.xlsx"
        expected_res_perm_missing = "Missing permissions for resource 'test_thing_1' (Excel row 2)"
        expected_msg_missing = (
            "Missing file permissions for file 'testdata/bitstreams/test.jpg' "
            "(Resource ID 'test_thing_1', Excel row 2)."
            " An attempt to deduce them from the resource permissions failed."
        )
        expected_xml_validation = regex.escape(
            "Element 'bitstream', attribute 'permissions': '' is not a valid value of the atomic type 'xs:IDREF'."
        )
        _, catched_warnings = excel2xml_cli.excel2xml(file, "1234", "excel2xml-invalid")
        assert len(catched_warnings) == 4
        assert catched_warnings[0].message.args[0] == expected_res_perm_missing  # type:ignore[union-attr]
        assert catched_warnings[1].message.args[0] == expected_msg_missing  # type:ignore[union-attr]
        assert regex.search(expected_xml_validation, catched_warnings[3].message.args[0])  # type:ignore[union-attr]

    def test_invalid_prop_val(self) -> None:
        file = f"{INVALID_EXCEL_DIRECTORY}/single-invalid-value-for-property.xlsx"
        expected_msg_missing = regex.escape(
            "Error in resource 'person_0': Excel row 3 has an entry in column(s) '1_encoding', '1_permissions', "
            "but not in '1_value'. Please note that cell contents that don't meet the requirements"
        )
        expected_msg_excel = (
            "At least one value per property is required, "
            "but resource 'person_0', property ':hasName' (Excel row 3) doesn't contain any values."
        )
        expected_xml_validation = regex.escape("Element 'text-prop': Missing child element(s). Expected is ( text ).")
        _, catched_warnings = excel2xml_cli.excel2xml(file, "1234", "excel2xml-invalid")
        assert len(catched_warnings) == 4
        msg_missing_label = catched_warnings[0].message.args[0]  # type:ignore[union-attr]
        assert regex.search(expected_msg_missing, msg_missing_label)
        msg_excel = catched_warnings[1].message.args[0]  # type:ignore[union-attr]
        assert msg_excel == expected_msg_excel
        msg_validation = catched_warnings[3].message.args[0]  # type:ignore[union-attr]
        assert regex.search(expected_xml_validation, msg_validation)


class TestRaisesException:
    def test_id_prop_name(self) -> None:
        file = f"{INVALID_EXCEL_DIRECTORY}/id-propname-both.xlsx"
        expected_msg = regex.escape("Exactly 1 of the 2 columns 'id' and 'prop name' must be filled.")
        with pytest.raises(BaseError, match=expected_msg):
            excel2xml_cli.excel2xml(file, "1234", "excel2xml-invalid")

    def test_id_prop_none(self) -> None:
        file = f"{INVALID_EXCEL_DIRECTORY}/id-propname-none.xlsx"
        expected_msg = regex.escape("Exactly 1 of the 2 columns 'id' and 'prop name' must be filled.")
        with pytest.raises(BaseError, match=expected_msg):
            excel2xml_cli.excel2xml(file, "1234", "excel2xml-invalid")

    def test_nonexisting_proptype(self) -> None:
        file = f"{INVALID_EXCEL_DIRECTORY}/nonexisting-proptype.xlsx"
        expected_msg = regex.escape("Invalid prop type for property :hasName in resource person_0")
        with pytest.raises(BaseError, match=expected_msg):
            excel2xml_cli.excel2xml(file, "1234", "excel2xml-invalid")

    def test_start_with_prop_row(self) -> None:
        file = f"{INVALID_EXCEL_DIRECTORY}/start-with-property-row.xlsx"
        expected_msg = regex.escape(
            "The first row of your Excel/CSV is invalid. The first row must define a resource, not a property."
        )
        with pytest.raises(BaseError, match=expected_msg):
            excel2xml_cli.excel2xml(file, "1234", "excel2xml-invalid")


if __name__ == "__main__":
    pytest.main([__file__])
