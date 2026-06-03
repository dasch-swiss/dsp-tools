from enum import StrEnum


class PlaceholderFile(StrEnum):
    ARCHIVE_REPRESENTATION = "ArchiveRepresentation"
    AUDIO_REPRESENTATION = "AudioRepresentation"
    DOCUMENT_REPRESENTATION = "DocumentRepresentation"
    MOVING_IMAGE_REPRESENTATION = "MovingImageRepresentation"
    STILL_IMAGE_REPRESENTATION = "StillImageRepresentation"
    TEXT_REPRESENTATION = "TextRepresentation"
