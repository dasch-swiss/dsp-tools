from unittest.mock import Mock, patch

from dsp_tools import cli


# test lists validate
@patch("dsp_tools.cli.validate_lists_section_with_schema")
def test_lists_validate(validate_lists: Mock) -> None:
    """Test the 'dsp-tools create --lists-only --validate-only' command"""
    file = "filename.json"
    args = f"create --lists-only --validate-only {file}".split()
    cli.main(args)
    validate_lists.assert_called_once_with(file)


# test lists create
@patch("dsp_tools.cli.create_lists")
def test_lists_create(create_lists: Mock) -> None:
    """Test the 'dsp-tools create --lists-only' command"""
    create_lists.return_value = ({}, True)
    file = "filename.json"
    args = f"create --lists-only {file}".split()
    cli.main(args)
    create_lists.assert_called_once_with(
        project_file_as_path_or_parsed=file,
        server="http://0.0.0.0:3333",
        user="root@example.com",
        password="test",
        dump=False,
    )
