from enum import StrEnum


class PlaceholderFile(StrEnum):
    """
    Temporary stand-in to use instead of a real file when the actual file is not yet available.

    Attention:
        This is only allowed on localhost and test servers.
        Production environments do not allow a resource with a placeholder.

    The chosen value must match the representation type defined in the ontology.

    For example, if the `super` of the resource is `StillImageRepresentation`,
    use `PlaceholderFile.STILL_IMAGE_REPRESENTATION`.

    Examples:
        ```python
        resource = resource.add_file(
            filename=PlaceholderFile.STILL_IMAGE_REPRESENTATION,
            license=xmllib.LicenseRecommended.CC.BY_NC_ND,
            copyright_holder="Example University",
            authorship=["Jane Doe"],
        )
        ```
    """

    ARCHIVE_REPRESENTATION = "ArchiveRepresentation"
    AUDIO_REPRESENTATION = "AudioRepresentation"
    DOCUMENT_REPRESENTATION = "DocumentRepresentation"
    MOVING_IMAGE_REPRESENTATION = "MovingImageRepresentation"
    STILL_IMAGE_REPRESENTATION = "StillImageRepresentation"
    TEXT_REPRESENTATION = "TextRepresentation"
