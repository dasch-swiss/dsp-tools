from dataclasses import dataclass, field


@dataclass
class IriResolver:
    """Service for resolving internal IDs to IRIs."""

    lookup: dict[str, str] = field(default_factory=dict)

    def add_iri(self, internal_id: str, iri: str) -> None:
        """Adds an IRI to the resolver."""
        self.lookup[internal_id] = iri

    def resolve(self, internal_id: str) -> str | None:
        """Resolves an internal ID to an IRI."""
        return self.lookup.get(internal_id)
