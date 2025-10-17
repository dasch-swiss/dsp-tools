"""Data models for config command."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class CreateConfig:
    """Configuration for the create command."""

    file: str
    validate_only: bool = False
    lists_only: bool = False
    verbose: bool = False

    def to_dict(self) -> dict[str, str | bool | int | None]:
        """Convert to dictionary for JSON serialization."""
        return {
            "file": self.file,
            "validate_only": self.validate_only,
            "lists_only": self.lists_only,
            "verbose": self.verbose,
        }

    @staticmethod
    def from_dict(data: dict[str, str | bool | int | None]) -> CreateConfig:
        """Create from dictionary loaded from JSON."""
        return CreateConfig(
            file=str(data["file"]),
            validate_only=bool(data.get("validate_only", False)),
            lists_only=bool(data.get("lists_only", False)),
            verbose=bool(data.get("verbose", False)),
        )


@dataclass
class XmluploadConfig:
    """Configuration for the xmlupload command."""

    file: str
    imgdir: str = "."
    skip_validation: bool = False
    skip_ontology_validation: bool = False
    interrupt_after: int | None = None
    no_iiif_uri_validation: bool = False
    ignore_duplicate_files_warning: bool = False
    validation_severity: str = "info"
    id2iri_replacement_with_file: str | None = None

    def to_dict(self) -> dict[str, str | bool | int | None]:
        """Convert to dictionary for JSON serialization."""
        return {
            "file": self.file,
            "imgdir": self.imgdir,
            "skip_validation": self.skip_validation,
            "skip_ontology_validation": self.skip_ontology_validation,
            "interrupt_after": self.interrupt_after,
            "no_iiif_uri_validation": self.no_iiif_uri_validation,
            "ignore_duplicate_files_warning": self.ignore_duplicate_files_warning,
            "validation_severity": self.validation_severity,
            "id2iri_replacement_with_file": self.id2iri_replacement_with_file,
        }

    @staticmethod
    def from_dict(data: dict[str, str | bool | int | None]) -> XmluploadConfig:
        """Create from dictionary loaded from JSON."""
        interrupt_value = data.get("interrupt_after")
        interrupt_after_int = int(interrupt_value) if interrupt_value is not None else None
        id2iri_value = data.get("id2iri_replacement_with_file")
        id2iri_str = str(id2iri_value) if id2iri_value else None

        return XmluploadConfig(
            file=str(data["file"]),
            imgdir=str(data.get("imgdir", ".")),
            skip_validation=bool(data.get("skip_validation", False)),
            skip_ontology_validation=bool(data.get("skip_ontology_validation", False)),
            interrupt_after=interrupt_after_int,
            no_iiif_uri_validation=bool(data.get("no_iiif_uri_validation", False)),
            ignore_duplicate_files_warning=bool(data.get("ignore_duplicate_files_warning", False)),
            validation_severity=str(data.get("validation_severity", "info")),
            id2iri_replacement_with_file=id2iri_str,
        )


@dataclass
class ServerConfig:
    """Configuration for a server including credentials and command configs."""

    server: str
    user: str
    password: str
    create: CreateConfig | None = None
    xmlupload: XmluploadConfig | None = None

    def to_dict(self) -> dict[str, str | dict[str, str | bool | int | None]]:
        """Convert to dictionary for JSON serialization."""
        result: dict[str, str | dict[str, str | bool | int | None]] = {
            "server": self.server,
            "user": self.user,
            "password": self.password,
        }
        if self.create:
            result["create"] = self.create.to_dict()
        if self.xmlupload:
            result["xmlupload"] = self.xmlupload.to_dict()
        return result

    @staticmethod
    def from_dict(data: dict[str, str | dict[str, str | bool | int | None]]) -> ServerConfig:
        """Create from dictionary loaded from JSON."""
        create_config = None
        if "create" in data and isinstance(data["create"], dict):
            create_config = CreateConfig.from_dict(data["create"])

        xmlupload_config = None
        if "xmlupload" in data and isinstance(data["xmlupload"], dict):
            xmlupload_config = XmluploadConfig.from_dict(data["xmlupload"])

        return ServerConfig(
            server=str(data["server"]),
            user=str(data["user"]),
            password=str(data["password"]),
            create=create_config,
            xmlupload=xmlupload_config,
        )
