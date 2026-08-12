import os
import tempfile
import unittest
from pathlib import Path
from typing import Any, Mapping
from unittest.mock import patch

from fastapi.testclient import TestClient

from responsible_next_step.api import create_app


class RecordingAuditPersistence:
    def __init__(self) -> None:
        self.records: list[dict[str, Any]] = []

    def persist(self, record: Mapping[str, Any]) -> str:
        copied = dict(record)
        self.records.append(copied)
        return f"memory://audit/{copied['decision_id']}.json"


class FailingAuditPersistence:
    def persist(self, record: Mapping[str, Any]) -> str:
        raise OSError("storage credentials leaked only in logs")


class DemoApiHttpContractTest(unittest.TestCase):
    def setUp(self):
        self.persistence = RecordingAuditPersistence()
        self.client = TestClient(
            create_app(
                audit_persistence=self.persistence,
                adaptive_enabled=True,
            )
        )

    def test_only_official_scenario_and_policy_mode_are_accepted(self):
        for payload in (
            {"scenario_id": "unknown", "policy_mode": "baseline"},
            {"scenario_id": "vehicle_simple", "policy_mode": "unknown"},
            {
                "scenario_id": "vehicle_simple",
                "policy_mode": "baseline",
                "customer_context": {"email": "not-accepted@example.test"},
            },
        ):
            with self.subTest(payload=payload):
                response = self.client.post("/v1/decisions", json=payload)
                self.assertEqual(response.status_code, 422)
                self.assertEqual(
                    response.json(),
                    {"detail": "Requisição inválida para a API de Demonstração."},
                )
                self.assertNotIn("not-accepted@example.test", response.text)

        self.assertEqual(self.persistence.records, [])

    def test_three_official_scenarios_use_the_responsible_engine_and_are_audited(self):
        expected = {
            "vehicle_simple": ("simulate_vehicle_secured_loan", False, []),
            "home_complex": ("route_to_specialist", True, []),
            "guardrail_sensitive": (
                "no_offer_now",
                False,
                ["adversarial_or_unsafe_context"],
            ),
        }

        for scenario_id, outcome in expected.items():
            with self.subTest(scenario_id=scenario_id):
                response = self.client.post(
                    "/v1/decisions",
                    json={"scenario_id": scenario_id, "policy_mode": "baseline"},
                )
                self.assertEqual(response.status_code, 200, response.text)
                decision = response.json()
                self.assertEqual(decision["selected_action"], outcome[0])
                self.assertEqual(decision["requires_human_review"], outcome[1])
                self.assertEqual(decision["guardrails_triggered"], outcome[2])
                self.assertEqual(
                    decision["policy_version"], "baseline_deterministic_v0.1"
                )
                self.assertTrue(decision["audit_log_ref"].startswith("memory://audit/"))
                self.assertTrue(decision["not_credit_approval"])
                self.assertTrue(decision["not_credit_contracting"])
                self.assertTrue(decision["does_not_define_real_rate"])
                self.assertTrue(decision["does_not_define_real_limit"])

        self.assertEqual(len(self.persistence.records), 3)
        self.assertEqual(
            [record["selected_action"] for record in self.persistence.records],
            [outcome[0] for outcome in expected.values()],
        )

    def test_telemetry_logs_only_decision_metadata_not_payload(self):
        with self.assertLogs("responsible_next_step.api", level="INFO") as logs:
            response = self.client.post(
                "/v1/decisions",
                json={"scenario_id": "vehicle_simple", "policy_mode": "baseline"},
            )

        self.assertEqual(response.status_code, 200)
        serialized = "\n".join(logs.output)
        self.assertIn('"event": "decision"', serialized)
        self.assertIn('"selected_action": "simulate_vehicle_secured_loan"', serialized)
        for forbidden in ("vehicle_simple", "synthetic_customer_id", "context_minimized"):
            self.assertNotIn(forbidden, serialized)

    def test_adaptive_policy_uses_the_same_guardrails_and_audit_contract(self):
        response = self.client.post(
            "/v1/decisions",
            json={
                "scenario_id": "guardrail_sensitive",
                "policy_mode": "adaptive",
            },
        )

        self.assertEqual(response.status_code, 200, response.text)
        decision = response.json()
        self.assertEqual(decision["selected_action"], "no_offer_now")
        self.assertEqual(decision["eligible_actions"], ["no_offer_now"])
        self.assertEqual(
            decision["guardrails_triggered"], ["adversarial_or_unsafe_context"]
        )
        self.assertTrue(
            decision["policy_version"].startswith("contextual_thompson_sampling_")
        )
        self.assertEqual(len(self.persistence.records), 1)

    def test_incompatible_adaptive_artifact_fails_explicitly_without_audit(self):
        persistence = RecordingAuditPersistence()
        client = TestClient(
            create_app(
                audit_persistence=persistence,
                adaptive_enabled=True,
                policy_artifact={"schema_version": "incompatible"},
            )
        )

        response = client.post(
            "/v1/decisions",
            json={"scenario_id": "vehicle_simple", "policy_mode": "adaptive"},
        )

        self.assertEqual(response.status_code, 503)
        self.assertEqual(
            response.json(), {"detail": "Política Adaptativa indisponível."}
        )
        self.assertEqual(persistence.records, [])

    def test_paused_adaptive_policy_fails_without_silent_baseline_fallback(self):
        persistence = RecordingAuditPersistence()
        with patch.dict(os.environ, {"ADAPTIVE_ENABLED": "false"}):
            client = TestClient(create_app(audit_persistence=persistence))

        response = client.post(
            "/v1/decisions",
            json={"scenario_id": "vehicle_simple", "policy_mode": "adaptive"},
        )

        self.assertEqual(response.status_code, 503)
        self.assertEqual(
            response.json(),
            {
                "detail": (
                    "Política Adaptativa pausada; selecione explicitamente o "
                    "Baseline Determinístico."
                )
            },
        )
        self.assertEqual(persistence.records, [])

        baseline_response = client.post(
            "/v1/decisions",
            json={"scenario_id": "vehicle_simple", "policy_mode": "baseline"},
        )
        self.assertEqual(baseline_response.status_code, 200)
        self.assertEqual(
            baseline_response.json()["policy_version"], "baseline_deterministic_v0.1"
        )

    def test_audit_failure_returns_service_error_without_a_valid_decision(self):
        client = TestClient(
            create_app(
                audit_persistence=FailingAuditPersistence(),
                adaptive_enabled=True,
            )
        )

        response = client.post(
            "/v1/decisions",
            json={"scenario_id": "vehicle_simple", "policy_mode": "baseline"},
        )

        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.json(), {"detail": "Auditoria indisponível."})
        self.assertNotIn("decision_id", response.text)
        self.assertNotIn("storage credentials", response.text)

    def test_health_and_readiness_expose_only_technical_status(self):
        health = self.client.get("/health")
        readiness = self.client.get("/ready")

        self.assertEqual(health.status_code, 200)
        self.assertEqual(health.json(), {"status": "ok"})
        self.assertEqual(readiness.status_code, 200)
        self.assertEqual(readiness.json(), {"status": "ready"})
        serialized = health.text + readiness.text
        for forbidden in ("policy", "scenario", "customer", "audit", "credential"):
            self.assertNotIn(forbidden, serialized.lower())

    def test_packaged_scenarios_and_policy_do_not_depend_on_repository_files(self):
        with tempfile.TemporaryDirectory() as directory:
            old_cwd = Path.cwd()
            try:
                os.chdir(directory)
                client = TestClient(
                    create_app(
                        audit_persistence=RecordingAuditPersistence(),
                        adaptive_enabled=True,
                    )
                )
                response = client.post(
                    "/v1/decisions",
                    json={"scenario_id": "vehicle_simple", "policy_mode": "adaptive"},
                )
            finally:
                os.chdir(old_cwd)

        self.assertEqual(response.status_code, 200, response.text)


if __name__ == "__main__":
    unittest.main()
