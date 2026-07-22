from __future__ import annotations

from enum import Enum
from enum import auto


class NewlineReplacement(Enum):
    """
    Options how to deal with `\\n` inside rich text values.

    - `NONE`: don't modify the rich text (`\\n` will be lost, because it is meaningless in an XML file)
    - `PARAGRAPH`: replace `Start\\nEnd` with `<p>Start</p><p>End</p>`
    - `LINEBREAK`: replace `Start\\nEnd` with `Start<br/>End`

    Examples:
        ```python
        # setting the replacement options for newlines
        resource = resource.add_richtext(
            prop_name=":propName",
            value="Start\\n\\nEnd",
            newline_replacement=xmllib.NewlineReplacement.PARAGRAPH
        )
        ```
    """

    NONE = auto()
    PARAGRAPH = auto()
    LINEBREAK = auto()


class ResourceAuthorshipDefault(Enum):
    """
    Sentinel for the `apply_default_resource_authorship` parameter of `XMLRoot`.

    The single member `PROJECT_DEFAULT` (exported as `xmllib.PROJECT_DEFAULT`) marks that the
    project's `default_data_authorship` should be applied to every resource that does not set its own
    authorship. Unlike a literal list of authors, this is not resolved during serialisation
    (xmllib does not know the project's default), but at `xmlupload`, against the project on the server.
    """

    PROJECT_DEFAULT = auto()


PROJECT_DEFAULT = ResourceAuthorshipDefault.PROJECT_DEFAULT
