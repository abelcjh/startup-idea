"""
SOC2-compliant PII scrubber — Microsoft Presidio.

Single source of truth for PII redaction across the ingestion pipeline
and LangGraph agent nodes. ALL text MUST pass through this before
reaching any LLM (LiteLLM / Mistral) or external service.
"""

from __future__ import annotations

import structlog
from presidio_analyzer import AnalyzerEngine, RecognizerResult
from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import EngineResult

logger = structlog.get_logger(__name__)

_analyzer = AnalyzerEngine()
_anonymizer = AnonymizerEngine()

SCRUB_ENTITIES: list[str] = [
    "PERSON",
    "EMAIL_ADDRESS",
    "PHONE_NUMBER",
    "CREDIT_CARD",
    "IBAN_CODE",
    "IP_ADDRESS",
    "US_SSN",
    "US_BANK_NUMBER",
    "LOCATION",
    "DATE_TIME",
    "NRP",
    "MEDICAL_LICENSE",
    "URL",
]


def analyze(text: str, *, language: str = "en") -> list[RecognizerResult]:
    return _analyzer.analyze(
        text=text,
        entities=SCRUB_ENTITIES,
        language=language,
    )


def scrub(text: str, *, language: str = "en", tenant_id: str = "") -> str:
    results = analyze(text, language=language)
    anonymized: EngineResult = _anonymizer.anonymize(text=text, analyzer_results=results)
    if results:
        logger.info(
            "pii.scrubbed",
            tenant_id=tenant_id,
            entity_count=len(results),
            entity_types=list({r.entity_type for r in results}),
        )
    return anonymized.text


def scrub_batch(
    texts: list[str],
    *,
    language: str = "en",
    tenant_id: str = "",
) -> list[str]:
    log = logger.bind(tenant_id=tenant_id)
    scrubbed = [scrub(t, language=language, tenant_id=tenant_id) for t in texts]
    log.info("pii.batch_done", count=len(scrubbed))
    return scrubbed
