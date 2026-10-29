import pytest
from pydantic import ValidationError

from src.schemas import (
    AuditFinding,
    ComplianceStatus,
    DocumentGrade,
    EvidenceChunk,
    RiskSeverity,
    SourceType,
)


def make_internal_evidence(**overrides):
    data = {
        "id": "doc1-page1-chunk1",
        "document_name": "sample.pdf",
        "page_number": 1,
        "section_title": "Data Retention",
        "text": "Records must be retained for five years.",
        "source_type": SourceType.INTERNAL,
        "score": 0.85,
        "source_url": None,
    }

    data.update(overrides)

    return EvidenceChunk(**data)


def test_valid_internal_evidence():
    evidence = make_internal_evidence()

    assert evidence.page_number == 1
    assert evidence.source_type == SourceType.INTERNAL


def test_internal_evidence_requires_page_number():
    with pytest.raises(ValidationError):
        make_internal_evidence(page_number=None)


def test_pdf_page_numbers_are_one_indexed():
    with pytest.raises(ValidationError):
        make_internal_evidence(page_number=0)


def test_web_evidence_requires_url():
    with pytest.raises(ValidationError):
        EvidenceChunk(
            id="web-1",
            document_name="Reference page",
            page_number=None,
            section_title="",
            text="Synthetic reference text.",
            source_type=SourceType.WEB,
            score=0.8,
            source_url=None,
        )


def test_web_evidence_has_no_page_number():
    evidence = EvidenceChunk(
        id="web-1",
        document_name="Reference page",
        page_number=None,
        section_title="",
        text="Synthetic reference text.",
        source_type=SourceType.WEB,
        score=0.8,
        source_url="https://example.com/reference",
    )

    assert evidence.page_number is None


def test_document_grade_confidence_range():
    with pytest.raises(ValidationError):
        DocumentGrade(
            is_relevant=True,
            confidence_score=1.5,
            rationale="Synthetic test rationale.",
        )


def test_audit_finding_rejects_duplicate_evidence_ids():
    with pytest.raises(ValidationError):
        AuditFinding(
            policy_clause_id="POL-001",
            policy_text_excerpt="Synthetic policy text.",
            status=ComplianceStatus.PARTIALLY_COMPLIANT,
            severity=RiskSeverity.MEDIUM,
            statutory_clause=None,
            statutory_verbatim_quote=None,
            evidence_ids=["doc1", "doc1"],
            gap_analysis="Synthetic test gap.",
            remediation_action="Review the retention period.",
        )


def test_audit_finding_uses_separate_status_and_severity():
    finding = AuditFinding(
        policy_clause_id="POL-002",
        policy_text_excerpt="Synthetic policy text.",
        status=ComplianceStatus.NON_COMPLIANT,
        severity=RiskSeverity.LOW,
        evidence_ids=["doc1"],
        gap_analysis="Synthetic test gap.",
        remediation_action="Review the policy.",
    )

    assert finding.status == ComplianceStatus.NON_COMPLIANT
    assert finding.severity == RiskSeverity.LOW