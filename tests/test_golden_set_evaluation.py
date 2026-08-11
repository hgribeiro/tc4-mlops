import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from responsible_next_step import evaluate_golden_set


REPO_ROOT = Path(__file__).resolve().parents[1]
GOLDEN_SET_PATH = REPO_ROOT / "data" / "golden_set" / "evaluation_cases.jsonl"


class GoldenSetEvaluationTest(unittest.TestCase):
    def test_public_evaluator_runs_the_five_versioned_cases(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            report = evaluate_golden_set(
                GOLDEN_SET_PATH,
                Path(tmp_dir) / "audit",
            )

        self.assertEqual(report["total_cases"], 5)
        self.assertEqual(report["passed_cases"], 5)
        self.assertEqual(report["failed_cases"], 0)
        self.assertTrue(report["all_passed"])
        self.assertEqual(
            [case["case_id"] for case in report["cases"]],
            [
                "vehicle_digital",
                "home_complex",
                "incomplete_context",
                "education_first",
                "adversarial_ineligible",
            ],
        )
        self.assertTrue(all(case["passed"] for case in report["cases"]))
        self.assertEqual(report["coverage"]["audit_logs"]["valid"], 5)
        self.assertEqual(report["coverage"]["audit_logs"]["coverage_rate"], 1.0)
        self.assertEqual(
            set(report["coverage"]["selected_actions"]),
            {
                "simulate_vehicle_secured_loan",
                "route_to_specialist",
                "request_documents",
                "educational_content_secured_credit",
                "no_offer_now",
            },
        )

    def test_evaluator_rejects_wrong_quantity_or_missing_case_schema_field(self):
        cases = [
            json.loads(line)
            for line in GOLDEN_SET_PATH.read_text(encoding="utf-8").splitlines()
        ]

        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            four_cases = tmp_path / "four-cases.jsonl"
            four_cases.write_text(
                "\n".join(json.dumps(case) for case in cases[:4]) + "\n",
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ValueError, "exatamente 5 casos"):
                evaluate_golden_set(four_cases, tmp_path / "audit-four")

            del cases[0]["justification"]
            invalid_schema = tmp_path / "invalid-schema.jsonl"
            invalid_schema.write_text(
                "\n".join(json.dumps(case) for case in cases) + "\n",
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ValueError, "justification"):
                evaluate_golden_set(invalid_schema, tmp_path / "audit-schema")

            cases = [
                json.loads(line)
                for line in GOLDEN_SET_PATH.read_text(encoding="utf-8").splitlines()
            ]
            del cases[0]["context"]["channel"]
            invalid_context = tmp_path / "invalid-context.jsonl"
            invalid_context.write_text(
                "\n".join(json.dumps(case) for case in cases) + "\n",
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ValueError, "context.*channel"):
                evaluate_golden_set(invalid_context, tmp_path / "audit-context")

    def test_malformed_decision_contract_and_missing_log_fail_evaluation(self):
        malformed_decision = {
            "decision_id": None,
            "request_id": None,
            "selected_action": None,
            "eligible_actions": "no_offer_now",
            "policy_version": None,
            "reason_codes": None,
            "requires_human_review": "false",
            "guardrails_triggered": "invalid",
            "audit_log_ref": None,
            "not_credit_approval": "true",
            "requires_formal_credit_analysis": "true",
        }
        with tempfile.TemporaryDirectory() as tmp_dir, patch(
            "responsible_next_step.golden_set.engine.decide",
            return_value=malformed_decision,
        ):
            report = evaluate_golden_set(GOLDEN_SET_PATH, Path(tmp_dir) / "audit")

        self.assertFalse(report["all_passed"])
        self.assertEqual(report["failed_cases"], 5)
        self.assertEqual(report["coverage"]["audit_logs"]["valid"], 0)
        self.assertTrue(
            any(
                "contrato de saída exige decision_id" in failure
                for failure in report["cases"][0]["failures"]
            )
        )
        self.assertIn(
            "log auditável ausente, inválido ou incoerente",
            report["cases"][0]["failures"],
        )

    def test_expected_behavior_mismatch_fails_the_case_and_aggregate(self):
        cases = [
            json.loads(line)
            for line in GOLDEN_SET_PATH.read_text(encoding="utf-8").splitlines()
        ]
        cases[0]["expected_reason_codes"].append("collateral_complexity")

        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            altered_set = tmp_path / "altered.jsonl"
            altered_set.write_text(
                "\n".join(json.dumps(case) for case in cases) + "\n",
                encoding="utf-8",
            )
            report = evaluate_golden_set(altered_set, tmp_path / "audit")
            env = os.environ.copy()
            env["PYTHONPATH"] = str(REPO_ROOT / "src")
            cli_result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "responsible_next_step",
                    "evaluate-golden-set",
                    "--input",
                    str(altered_set),
                    "--audit-log-dir",
                    str(tmp_path / "cli-audit"),
                ],
                cwd=REPO_ROOT,
                env=env,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )

        self.assertFalse(report["all_passed"])
        self.assertEqual(report["failed_cases"], 1)
        self.assertFalse(report["cases"][0]["passed"])
        self.assertIn(
            "Reason Codes esperados ausentes: ['collateral_complexity']",
            report["cases"][0]["failures"],
        )
        self.assertEqual(cli_result.returncode, 1, cli_result.stderr)
        self.assertFalse(json.loads(cli_result.stdout)["all_passed"])

    def test_cli_evaluates_the_golden_set_offline_and_prints_structured_summary(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            env = os.environ.copy()
            env["PYTHONPATH"] = str(REPO_ROOT / "src")
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "responsible_next_step",
                    "evaluate-golden-set",
                    "--input",
                    str(GOLDEN_SET_PATH),
                    "--audit-log-dir",
                    str(Path(tmp_dir) / "audit"),
                    "--pretty",
                ],
                cwd=REPO_ROOT,
                env=env,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )

        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(result.stdout)
        self.assertTrue(report["all_passed"])
        self.assertEqual(report["passed_cases"], 5)
        self.assertEqual(len(report["cases"]), 5)


if __name__ == "__main__":
    unittest.main()
