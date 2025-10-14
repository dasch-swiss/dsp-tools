"""Interactive configuration creation."""

from __future__ import annotations

from dsp_tools.commands.config.config_manager import save_config
from dsp_tools.commands.config.config_manager import validate_config_id
from dsp_tools.commands.config.models import CreateConfig
from dsp_tools.commands.config.models import ServerConfig
from dsp_tools.commands.config.models import XmluploadConfig


def _prompt_for_config_id() -> str | None:
    """
    Prompt user for a config ID.

    Returns:
        Config ID string, or None if invalid
    """
    print(
        "\nYou can create a new configuration for the create and xmlupload commands."
    )
    print("Please enter an ID for the config object, it may only contain alpha-numeric characters and the characters")
    print('"-" and "_"')
    config_id = input("Config ID: ").strip()

    if not validate_config_id(config_id):
        print(f"\nInvalid config ID '{config_id}'. Only alphanumeric characters, hyphens, and underscores are allowed.")
        return None

    return config_id


def _prompt_for_command_type() -> str | None:
    """
    Prompt user to select command type.

    Returns:
        "1" for create, "2" for xmlupload, or None if invalid
    """
    print("\nPlease enter the number for the config you want to create:")
    print("  [1] create")
    print("  [2] xmlupload")
    choice = input("Choice: ").strip()

    if choice not in ["1", "2"]:
        print(f"\nInvalid choice '{choice}'. Please enter 1 or 2.")
        return None

    return choice


def _prompt_for_localhost_defaults() -> bool:
    """
    Prompt user if they want to use localhost defaults.

    Returns:
        True if user wants defaults, False otherwise
    """
    print("\nDo you want to use the default server and credentials for localhost?")
    print("Enter 'y' if yes, 'n' if you want to enter the information manually.")
    choice = input("Choice (y/n): ").strip().lower()
    return choice == "y"


def _prompt_for_server() -> str:
    """Prompt user for server URL."""
    return input("Server URL: ").strip()


def _prompt_for_user() -> str:
    """Prompt user for username."""
    return input("Username: ").strip()


def _prompt_for_password() -> str:
    """Prompt user for password."""
    return input("Password: ").strip()


def _prompt_yes_no(prompt: str, default: bool = False) -> bool:
    """
    Prompt user for a yes/no question.

    Args:
        prompt: The question to ask
        default: Default value if user just presses enter

    Returns:
        True for yes, False for no
    """
    default_str = "y" if default else "n"
    choice = input(f"{prompt} (y/n, default: {default_str}): ").strip().lower()
    if not choice:
        return default
    return choice == "y"


def _prompt_for_create_options() -> CreateConfig:
    """
    Prompt user for create command options.

    Returns:
        CreateConfig object with user's choices
    """
    print("\n--- Create Command Configuration ---")

    file = input("Please enter the filepath for the project json file: ").strip()
    validate_only = _prompt_yes_no("Validate only without creating on server?")
    lists_only = _prompt_yes_no("Create only the lists?")
    verbose = _prompt_yes_no("Enable verbose output?")

    return CreateConfig(
        file=file,
        validate_only=validate_only,
        lists_only=lists_only,
        verbose=verbose,
    )


def _prompt_for_xmlupload_options() -> XmluploadConfig:
    """
    Prompt user for xmlupload command options.

    Returns:
        XmluploadConfig object with user's choices
    """
    print("\n--- XMLUpload Command Configuration ---")

    file = input("Please enter the filepath for the XML file: ").strip()

    imgdir = input("Folder for bitstream tags (default: .): ").strip()
    if not imgdir:
        imgdir = "."

    skip_validation = _prompt_yes_no("Skip SHACL schema validation?")
    skip_ontology_validation = _prompt_yes_no("Skip ontology validation?")

    interrupt_after_str = input("Interrupt after N resources (default: none, enter -1 for none): ").strip()
    interrupt_after = None
    if interrupt_after_str and interrupt_after_str != "-1":
        try:
            interrupt_after = int(interrupt_after_str)
        except ValueError:
            print(f"Invalid number '{interrupt_after_str}', using default (none)")

    no_iiif_uri_validation = _prompt_yes_no("Skip IIIF URI validation?")
    ignore_duplicate_files_warning = _prompt_yes_no("Ignore duplicate files warning?")

    validation_severity = input("Validation severity (error/warning/info, default: info): ").strip().lower()
    if validation_severity not in ["error", "warning", "info"]:
        validation_severity = "info"

    id2iri_input = input("ID to IRI mapping file (default: none, press enter to skip): ").strip()
    id2iri_replacement_with_file: str | None = id2iri_input if id2iri_input else None

    return XmluploadConfig(
        file=file,
        imgdir=imgdir,
        skip_validation=skip_validation,
        skip_ontology_validation=skip_ontology_validation,
        interrupt_after=interrupt_after,
        no_iiif_uri_validation=no_iiif_uri_validation,
        ignore_duplicate_files_warning=ignore_duplicate_files_warning,
        validation_severity=validation_severity,
        id2iri_replacement_with_file=id2iri_replacement_with_file,
    )


def config_new() -> bool:
    """
    Interactive configuration creation workflow.

    Returns:
        True if successful, False otherwise
    """
    # Step 1: Get config ID
    config_id = _prompt_for_config_id()
    if not config_id:
        return False

    # Step 2: Select command type
    command_type = _prompt_for_command_type()
    if not command_type:
        return False

    # Step 3: Get server credentials
    use_defaults = _prompt_for_localhost_defaults()
    if use_defaults:
        server = "http://0.0.0.0:3333"
        user = "root@example.com"
        password = "test"
        print("\nUsing default localhost credentials:")
        print(f"  Server: {server}")
        print(f"  User: {user}")
        print(f"  Password: {password}")
    else:
        print("\nPlease enter server credentials:")
        server = _prompt_for_server()
        user = _prompt_for_user()
        password = _prompt_for_password()

    # Step 4: Get command-specific options
    if command_type == "1":  # create
        create_config = _prompt_for_create_options()
        server_config = ServerConfig(
            server=server,
            user=user,
            password=password,
            create=create_config,
        )
    else:  # xmlupload
        xmlupload_config = _prompt_for_xmlupload_options()
        server_config = ServerConfig(
            server=server,
            user=user,
            password=password,
            xmlupload=xmlupload_config,
        )

    # Step 5: Save config
    if save_config(config_id, server_config):
        print(f"\nConfiguration '{config_id}' saved successfully!")
        return True
    else:
        print(f"\nFailed to save configuration '{config_id}'.")
        return False
