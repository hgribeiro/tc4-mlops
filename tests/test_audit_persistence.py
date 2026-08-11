import json
import tempfile
import unittest
from pathlib import Path
from typing import Any, Mapping

from responsible_next_step.audit import LocalAuditPersistence
from responsible_next_step.engine import decide


PROHIBITED_VALUES = ("synthetic.person@example.test", "123.456.789-00")


def minimal_customer(**overrides: Any) -> dict[str, Any]:
    payload = {
        "request_id": "req_audit_contract_001",
        "schema_version": "synthetic_customer_context_v0.1",
        "synthetic_customer_id": "syn_vehicle_001",
        "source_dataset": "manual_demo",
        "random_seed": 20260629,
        "event_timestamp": "2026-06-29T12:00:00Z",
        "collateral_type": "vehicle",
        "channel": "superapp",
        "journey_stage": "simulation",
        "synthetic_risk_level": "low",
        "policy_confidence": "high",
        "engagement_level": "high",
        "context_completeness": "sufficient",
        "synthetic_segment": "digital_simple",
        "relationship_tier": "standard",
        "contact_repetition_count": 1,
        "collateral_detail_status": "complete",
        "collateral_complexity": "low",
        "risk_communication_available": True,
        "known_guardrail_flags": [],
        "human_review_hint": False,
        "allowed_input_features": [
            "collateral_type",
            "channel",
            "journey_stage",
            "synthetic_risk_level",
            "policy_confidence",
        ],
    }
    payload.update(overrides)
    return payload


class RecordingAuditPersistence:
    def __init__(self, reference: str = "memory://audit/decision.json") -> None:
        self.reference = reference
        self.records: list[dict[str, Any]] = []

    def persist(self, record: Mapping[str, Any]) -> str:
        self.records.append(dict(record))
        return self.reference


class FailingAuditPersistence:
    def persist(self, record: Mapping[str, Any]) -> str:
        raise OSError("audit unavailable")


class AuditPersistenceContract:
    persistence: LocalAuditPersistence

    def read_persisted_record(self, reference: str) -> dict[str, Any]:
        raise NotImplementedError

    def test_persists_the_record_and_returns_an_audit_reference(self):
        record = {
            "decision_id": "dec_contract_001",
            "logged_at": "2026-06-29T12:00:01Z",
            "context_minimized": {"event_timestamp": "2026-06-29T12:00:00Z"},
        }

        reference = self.persistence.persist(record)

        self.assertIsInstance(reference, str)
        self.assertTrue(reference)
        self.assertEqual(self.read_persisted_record(reference), record)


class LocalAuditPersistenceContractTest(AuditPersistenceContract, unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.persistence = LocalAuditPersistence(Path(self.temp_dir.name))

    def read_persisted_record(self, reference: str) -> dict[str, Any]:
        return json.loads(Path(reference).read_text(encoding="utf-8").strip())


class DecisionAuditIntegrationTest(unittest.TestCase):
    def test_engine_uses_replaceable_persistence_with_a_minimized_record(self):
        persistence = RecordingAuditPersistence()
        context = minimal_customer(
            email=PROHIBITED_VALUES[0],
            cpf=PROHIBITED_VALUES[1],
        )

        decision = decide(context, persistence)

        self.assertEqual(decision["audit_log_ref"], persistence.reference)
        self.assertEqual(len(persistence.records), 1)
        audit_record = persistence.records[0]
        self.assertEqual(audit_record["decision_id"], decision["decision_id"])
        self.assertEqual(audit_record["selected_action"], decision["selected_action"])
        self.assertEqual(audit_record["dropped_prohibited_fields_count"], 2)
        serialized_record = json.dumps(audit_record)
        for prohibited_value in PROHIBITED_VALUES:
            self.assertNotIn(prohibited_value, serialized_record)
        self.assertNotIn("email", audit_record["context_minimized"])
        self.assertNotIn("cpf", audit_record["context_minimized"])

    def test_engine_propagates_persistence_failure_without_returning_a_decision(self):
        with self.assertRaisesRegex(OSError, "audit unavailable"):
            decide(minimal_customer(), FailingAuditPersistence())


if __name__ == "__main__":
    unittest.main()
