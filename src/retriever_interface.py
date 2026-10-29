from typing import Protocol

from src.schemas import EvidenceChunk


class Retriever(Protocol):
    """Interface for any AuditAgent evidence retriever."""

    def retrieve(
        self,
        query: str,
        top_k: int = 4,
    ) -> list[EvidenceChunk]:
        """
        Retrieve up to top_k unique evidence chunks.

        Implementations must:
        - Reject empty queries.
        - Return EvidenceChunk objects.
        - Preserve source metadata.
        - Return deterministic rankings.
        - Return no more than top_k results.
        """
        ...