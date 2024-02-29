from dataclasses import dataclass
from dataclasses import field


@dataclass
class ListNodeNames:
    """
    Contains the information to construct a list

    Args:
        lists_with_previous_cell_values: used to ensure that there are no duplicate node names
        previous_node_names: used to ensure that there are no duplicate node names
    """

    lists_with_previous_cell_values: list[list[str]] = field(default_factory=list)
    previous_node_names: list[str] = field(default_factory=list)
