from enum import Enum
from typing import NotRequired, TypedDict

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
    model_validator,
)


class ComplianceStatus(str, Enum):
    COMPLIANT = "COMPLIANT"
    NON_COMPLIANT = "NON_COMPLIANT"
    PARTIALLY_COMPLIANT = "PARTIALLY_COMPLIANT"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"


class RiskSeverity(str, Enum):
    INFORMATIONAL = "INFORMATIONAL"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class SourceType(str, Enum):
    INTERNAL = "INTERNAL"
    WEB = "WEB"


class EvidenceChunk(BaseModel):
    """A retrievable evidence unit with source provenance."""

    model_config = ConfigDict(extra="forbid")

    id: str = Field(min_length=1)
    document_name: str = Field(min_length=1)
    page_number: int | None = Field(default=None, ge=1)
    section_title: str = ""
    text: str = Field(min_length=1)
    source_type: SourceType
    score: float = 0.0
    source_url: str | None = None

    @model_validator(mode="after")
    def validate_source_metadata(self):
        if self.source_type == SourceType.INTERNAL:
            if self.page_number is None:
                raise ValueError(
                    "Internal PDF evidence requires a one-indexed page number"
                )

        if self.source_type == SourceType.WEB:
            if self.page_number is not None:
                raise ValueError(
                    "Web evidence must use page_number=None"
                )

            if not self.source_url:
                raise ValueError(
                    "Web evidence requires its actual source URL"
                )

        return self


class AuditFinding(BaseModel):
    """Structured compliance assessment."""

    model_config = ConfigDict(extra="forbid")

    policy_clause_id: str = Field(min_length=1)
    policy_text_excerpt: str = Field(min_length=1)

    status: ComplianceStatus
    severity: RiskSeverity

    statutory_clause: str | None = None
    statutory_verbatim_quote: str | None = None

    evidence_ids: list[str] = Field(default_factory=list)

    gap_analysis: str = Field(min_length=1)
    remediation_action: str = Field(min_length=1)

    @field_validator("evidence_ids")
    @classmethod
    def validate_evidence_ids(cls, value):
        if len(value) != len(set(value)):
            raise ValueError("evidence_ids must not contain duplicates")

        return value

    @model_validator(mode="after")
    def validate_statutory_quote(self):
        if self.statutory_verbatim_quote and not self.statutory_clause:
            raise ValueError(
                "A statutory quotation requires a statutory_clause reference"
            )

        return self


class DocumentGrade(BaseModel):
    """LLM-generated relevance assessment."""

    model_config = ConfigDict(extra="forbid")

    is_relevant: bool
    confidence_score: float = Field(ge=0.0, le=1.0)
    rationale: str = Field(min_length=1)


class AuditGraphState(TypedDict):
    """Shared state contract for the LangGraph workflow."""

    policy_clause_id: str
    policy_text: str
    current_query: str

    retrieved_docs: list[EvidenceChunk]
    document_grade: DocumentGrade | None

    retry_count: int
    web_fallback_used: bool
    web_fallback_attempted: bool

    is_grounded: bool
    audit_report: AuditFinding | None
    error_message: str | None


class CitationVerificationResult(BaseModel):
    """Result of deterministic citation verification."""

    model_config = ConfigDict(extra="forbid")

    is_valid: bool
    verified_evidence_ids: list[str] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)