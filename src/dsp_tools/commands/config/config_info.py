"""Display configuration details."""

from __future__ import annotations

from dsp_tools.commands.config.config_manager import get_config


def config_info(config_id: str) -> bool:
    """
    Display details for a specific configuration.

    Args:
        config_id: The ID of the configuration to display

    Returns:
        True if successful, False if config not found
    """
    config = get_config(config_id)

    if not config:
        print(f"Configuration '{config_id}' not found.")
        return False

    print(f"\nConfiguration: {config_id}")
    print(f"  Server: {config.server}")
    print(f"  User: {config.user}")
    print("  Password: ***")  # Masked for security

    if config.create:
        print("\n  Create configuration:")
        print(f"    File: {config.create.file}")
        print(f"    Validate only: {config.create.validate_only}")
        print(f"    Lists only: {config.create.lists_only}")
        print(f"    Verbose: {config.create.verbose}")

    if config.xmlupload:
        print("\n  XMLUpload configuration:")
        print(f"    File: {config.xmlupload.file}")
        print(f"    Image directory: {config.xmlupload.imgdir}")
        print(f"    Skip validation: {config.xmlupload.skip_validation}")
        print(f"    Skip ontology validation: {config.xmlupload.skip_ontology_validation}")
        print(f"    Interrupt after: {config.xmlupload.interrupt_after}")
        print(f"    No IIIF URI validation: {config.xmlupload.no_iiif_uri_validation}")
        print(f"    Ignore duplicate files warning: {config.xmlupload.ignore_duplicate_files_warning}")
        print(f"    Validation severity: {config.xmlupload.validation_severity}")
        print(f"    ID to IRI mapping file: {config.xmlupload.id2iri_replacement_with_file}")

    return True
