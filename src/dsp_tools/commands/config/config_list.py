"""List all available configurations."""

from __future__ import annotations

from dsp_tools.commands.config.config_manager import load_all_configs


def config_list() -> bool:
    """
    List all available configurations.

    Returns:
        True if successful, False otherwise
    """
    configs = load_all_configs()

    if not configs:
        print("No configurations found.")
        return True

    print("\nAvailable configurations:")
    for config_id in sorted(configs.keys()):
        config = configs[config_id]
        has_create = config.create is not None
        has_xmlupload = config.xmlupload is not None
        commands = []
        if has_create:
            commands.append("create")
        if has_xmlupload:
            commands.append("xmlupload")
        print(f"  - {config_id} ({', '.join(commands)})")

    return True
