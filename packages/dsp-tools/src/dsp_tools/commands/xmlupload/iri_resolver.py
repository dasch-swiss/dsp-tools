from dataclasses import dataclass
from dataclasses import field


@dataclass
class IriResolver:
    """Service for resolving internal IDs to IRIs."""

    lookup: dict[str, str] = field(default_factory=dict)

    def update(self, internal_id: str, iri: str) -> None:
        """Adds or updates an internal ID to IRI mapping"""
        self.lookup[internal_id] = iri

    def get(self, internal_id: str) -> str | None:
        """Resolves an internal ID to an IRI."""
        return self.lookup.get(internal_id)

    def non_empty(self) -> bool:
        """Checks if the resolver is empty."""
        return bool(self.lookup)
