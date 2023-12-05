from dataclasses import dataclass
from typing import Any, Protocol

# pylint: disable=too-few-public-methods


separator = "\n    "
list_separator = "\n    - "


class UserMessage(Protocol):
    """Information about user messages."""

    def __str__(self) -> str:
        """
        This function initiates all the steps for successful problem communication with the user.
        """


@dataclass(frozen=True)
class IngestMessage:
    unused_media_paths: list[str]
    media_no_uuid: list[tuple[str, str]]

    def __str__(self) -> str:
        msg_list = []
        if not self.unused_media_paths and not self.media_no_uuid:
            return (
                "All media referenced in the XML file were uploaded to sipi.\n"
                "No media was uploaded to sipi that was not referenced in the XML file."
            )
        if self.unused_media_paths:
            msg_list.append(
                "The following media were uploaded to sipi but not used in the data XML file:"
                + list_separator
                + list_separator.join(self.unused_media_paths)
            )
        if self.media_no_uuid:
            msg_list.append(
                "The following media were not uploaded to sipi but referenced in the data XML file:"
                + list_separator
                + list_separator.join([f"Resource ID: '{x[0]}' | Filepath: '{x[1]}'" for x in self.media_no_uuid])
            )
        return separator.join(msg_list)
