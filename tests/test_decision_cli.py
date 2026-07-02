import json
import os
import subprocess
import sys
import shutil
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def minimal_customer(**overrides):
    payload = {
        "request_id": "req_demo_vehicle_001",
        "schema_version": "synthetic_customer_context_v0.1",
        "synthetic_customer_id": "syn_vehicle_001",
        "source_dataset": "manual_demo",
        "source_record_ref": None,
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
            "engagement_level",
            "context_completeness",
            "synthetic_segment",
            "relationship_tier",
            "contact_repetition_count",
            "collateral_detail_status",
            "collateral_complexity",
            "risk_communication_available",
        ],
    }
    payload.update(overrides)
    return payload


class DecisionCliContractTest(unittest.TestCase):
    def run_cli(self, payload):
        tmp_path = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, tmp_path, ignore_errors=True)
        input_path = tmp_path / "customer.json"
        input_path.write_text(json.dumps(payload), encoding="utf-8")
        audit_dir = tmp_path / "audit"
        env = os.environ.copy()
        env["PYTHONPATH"] = str(REPO_ROOT / "src")

        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "responsible_next_step",
                "decide",
                "--input",
                str(input_path),
                "--audit-log-dir",
                str(audit_dir),
            ],
            cwd=REPO_ROOT,
            env=env,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        return json.loads(result.stdout), tmp_path

    def test_cli_returns_auditable_responsible_next_step_for_vehicle_customer(self):
        decision, tmp_path = self.run_cli(minimal_customer())

        for field in [
            "decision_id",
            "request_id",
            "selected_action",
            "policy_version",
            "reason_codes",
            "requires_human_review",
            "guardrails_triggered",
            "audit_log_ref",
        ]:
            self.assertIn(field, decision)

        self.assertEqual(decision["request_id"], "req_demo_vehicle_001")
        self.assertEqual(decision["selected_action"], "simulate_vehicle_secured_loan")
        self.assertEqual(decision["policy_version"], "baseline_deterministic_v0.1")
        self.assertFalse(decision["requires_human_review"])
        self.assertEqual(decision["guardrails_triggered"], [])
        self.assertTrue(decision["not_credit_approval"])
        self.assertTrue(decision["not_credit_contracting"])
        self.assertTrue(decision["does_not_define_real_rate"])
        self.assertTrue(decision["does_not_define_real_limit"])
        self.assertIn("não representa aprovação", decision["message"])

        audit_path = Path(decision["audit_log_ref"])
        self.assertTrue(audit_path.exists())
        audit_line = audit_path.read_text(encoding="utf-8").strip()
        audit_record = json.loads(audit_line)
        self.assertEqual(audit_record["decision_id"], decision["decision_id"])
        self.assertEqual(audit_record["request_id"], "req_demo_vehicle_001")
        self.assertEqual(audit_record["selected_action"], "simulate_vehicle_secured_loan")
        self.assertIn("context_minimized", audit_record)
        self.assertEqual(audit_record["context_minimized"]["collateral_type"], "vehicle")

    def test_documented_vehicle_example_file_runs_end_to_end(self):
        example_path = REPO_ROOT / "examples" / "synthetic-customers" / "vehicle-simple.json"
        payload = json.loads(example_path.read_text(encoding="utf-8"))

        decision, _ = self.run_cli(payload)

        self.assertEqual(decision["selected_action"], "simulate_vehicle_secured_loan")
        self.assertEqual(decision["policy_version"], "baseline_deterministic_v0.1")
        self.assertEqual(decision["guardrails_triggered"], [])
        self.assertFalse(decision["requires_human_review"])
        self.assertIn("vehicle_collateral_anchor", decision["reason_codes"])
        self.assertIn("digital_channel_fit", decision["reason_codes"])
        self.assertIn("sufficient_context_for_simulation", decision["reason_codes"])
        self.assertIn("no_critical_guardrail_triggered", decision["reason_codes"])
        self.assertTrue(Path(decision["audit_log_ref"]).exists())

    def test_home_complex_customer_is_routed_to_human_review(self):
        decision, _ = self.run_cli(
            minimal_customer(
                request_id="req_home_complex_001",
                synthetic_customer_id="syn_home_001",
                collateral_type="home",
                channel="hybrid",
                synthetic_risk_level="medium",
                policy_confidence="low",
                engagement_level="medium",
                context_completeness="sufficient",
                synthetic_segment="collateral_complex",
                relationship_tier="high_relationship",
                collateral_detail_status="complete",
                collateral_complexity="high",
                human_review_hint=True,
            )
        )

        self.assertEqual(decision["selected_action"], "route_to_specialist")
        self.assertTrue(decision["requires_human_review"])
        self.assertIn("human_in_the_loop", decision["reason_codes"])
        self.assertIn("route_to_specialist", decision["eligible_actions"])

    def test_guardrails_block_prohibited_data_and_temporal_leakage_without_logging_values(self):
        payload = minimal_customer(
            request_id="req_guardrail_001",
            allowed_input_features=["collateral_type", "channel", "duration"],
        )
        payload["email"] = "synthetic.person@example.test"
        payload["cpf"] = "123.456.789-00"

        decision, _ = self.run_cli(payload)

        self.assertEqual(decision["selected_action"], "no_offer_now")
        self.assertIn("temporal_leakage_duration", decision["guardrails_triggered"])
        self.assertIn("prohibited_personal_data", decision["guardrails_triggered"])
        self.assertTrue(decision["not_credit_approval"])

        audit_text = Path(decision["audit_log_ref"]).read_text(encoding="utf-8")
        self.assertNotIn("synthetic.person@example.test", audit_text)
        self.assertNotIn("123.456.789-00", audit_text)
        audit_record = json.loads(audit_text.strip())
        self.assertEqual(audit_record["dropped_prohibited_fields_count"], 2)
        self.assertNotIn("email", audit_record["context_minimized"])
        self.assertNotIn("cpf", audit_record["context_minimized"])

    def test_receivables_are_out_of_mvp_scope(self):
        decision, _ = self.run_cli(
            minimal_customer(
                request_id="req_receivables_001",
                collateral_type="synthetic_receivables",
                synthetic_segment="guardrail_sensitive",
            )
        )

        self.assertEqual(decision["selected_action"], "no_offer_now")
        self.assertIn("unsupported_collateral", decision["guardrails_triggered"])
        self.assertIn("synthetic_ineligibility", decision["reason_codes"])


if __name__ == "__main__":
    unittest.main()
