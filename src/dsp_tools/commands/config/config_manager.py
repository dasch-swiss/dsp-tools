"""Core functionality for managing configuration files."""

from __future__ import annotations

import json
import re
from pathlib import Path

from dsp_tools.commands.config.models import ServerConfig


def get_config_path() -> Path:
    """
    Get the path to the config file.

    Returns:
        Path to ~/.dsp-tools/config.json
    """
    return Path.home() / ".dsp-tools" / "config.json"


def ensure_config_dir_exists() -> None:
    """Create the config directory if it doesn't exist."""
    config_path = get_config_path()
    config_path.parent.mkdir(parents=True, exist_ok=True)


def validate_config_id(config_id: str) -> bool:
    """
    Validate that config ID contains only alphanumeric characters, hyphens, and underscores.

    Args:
        config_id: The config ID to validate

    Returns:
        True if valid, False otherwise
    """
    return bool(re.match(r"^[a-zA-Z0-9_-]+$", config_id))


def load_all_configs() -> dict[str, ServerConfig]:
    """
    Load all configurations from the config file.

    Returns:
        Dictionary mapping config IDs to ServerConfig objects
    """
    config_path = get_config_path()
    if not config_path.exists():
        return {}

    try:
        with open(config_path, encoding="utf-8") as f:
            data = json.load(f)
        return {config_id: ServerConfig.from_dict(config_data) for config_id, config_data in data.items()}
    except (json.JSONDecodeError, KeyError, ValueError) as e:
        print(f"Error loading config file: {e}")
        return {}


def save_config(config_id: str, config: ServerConfig) -> bool:
    """
    Save a configuration to the config file.

    Args:
        config_id: The ID for this configuration
        config: The ServerConfig object to save

    Returns:
        True if successful, False otherwise
    """
    if not validate_config_id(config_id):
        print(f"Invalid config ID '{config_id}'. Only alphanumeric characters, hyphens, and underscores are allowed.")
        return False

    ensure_config_dir_exists()
    config_path = get_config_path()

    # Load existing configs
    all_configs = load_all_configs()

    # Add or update the config
    all_configs[config_id] = config

    # Convert to dict format for JSON
    data_to_save = {cid: cfg.to_dict() for cid, cfg in all_configs.items()}

    # Write to file
    try:
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(data_to_save, f, indent=4)
        return True
    except OSError as e:
        print(f"Error writing config file: {e}")
        return False


def get_config(config_id: str) -> ServerConfig | None:
    """
    Retrieve a specific configuration.

    Args:
        config_id: The ID of the configuration to retrieve

    Returns:
        ServerConfig object if found, None otherwise
    """
    all_configs = load_all_configs()
    return all_configs.get(config_id)
