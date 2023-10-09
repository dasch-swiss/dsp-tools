from unittest.mock import Mock, patch

from dsp_tools import cli


# test lists validate
@patch("dsp_tools.cli.validate_lists_section_with_schema")
def test_lists_validate(validate_lists: Mock) -> None:
    """Test the 'dsp-tools create --lists-only --validate-only' command"""
    file = "filename.json"
    args = f"create --lists-only --validate-only {file}".split()
    cli.run(args)
    validate_lists.assert_called_once_with(file)


# test lists create
@patch("dsp_tools.cli.create_lists")
def test_lists_create(create_lists: Mock) -> None:
    """Test the 'dsp-tools create --lists-only' command"""
    create_lists.return_value = ({}, True)
    file = "filename.json"
    args = f"create --lists-only {file}".split()
    cli.run(args)
    create_lists.assert_called_once_with(
        project_file_as_path_or_parsed=file,
        server="http://0.0.0.0:3333",
        user="root@example.com",
        password="test",
        dump=False,
    )


# test project validate
@patch("dsp_tools.cli.validate_project")
def test_project_validate(validate_project: Mock) -> None:
    """Test the 'dsp-tools create --validate-only' command"""
    file = "filename.json"
    args = f"create --validate-only {file}".split()
    cli.run(args)
    validate_project.assert_called_once_with(file)


# test project create
@patch("dsp_tools.cli.create_project")
def test_project_create(create_project: Mock) -> None:
    """Test the 'dsp-tools create' command"""
    create_project.return_value = True
    file = "filename.json"
    args = f"create {file}".split()
    cli.run(args)
    create_project.assert_called_once_with(
        project_file_as_path_or_parsed=file,
        server="http://0.0.0.0:3333",
        user_mail="root@example.com",
        password="test",
        verbose=False,
        dump=False,
    )


# test project get
@patch("dsp_tools.cli.get_project")
def test_project_get(get_project: Mock) -> None:
    """Test the 'dsp-tools get --project' command"""
    get_project.return_value = True
    file = "filename.json"
    project = "shortname"
    args = f"get --project {project} {file}".split()
    cli.run(args)
    get_project.assert_called_once_with(
        project_identifier=project,
        outfile_path=file,
        server="http://0.0.0.0:3333",
        user="root@example.com",
        password="test",
        verbose=False,
        dump=False,
    )
