import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURE = REPO_ROOT / "tests" / "fixtures" / "bank-full-small.csv"


class ExperimentCliContractTest(unittest.TestCase):
    def run_experiment(self, output_dir: Path):
        env = os.environ.copy()
        env["PYTHONPATH"] = str(REPO_ROOT / "src")
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "responsible_next_step",
                "experiment",
                "--input",
                str(FIXTURE),
                "--output-dir",
                str(output_dir),
                "--seeds",
                "11,29,47",
                "--horizon",
                "400",
            ],
            cwd=REPO_ROOT,
            env=env,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        return json.loads(result.stdout)

    def test_experiment_compares_baseline_and_contextual_thompson_sampling(self):
        tmp_path = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, tmp_path, ignore_errors=True)

        report = self.run_experiment(tmp_path / "run")

        self.assertEqual(report["experiment_schema_version"], "offline_bandit_experiment_v0.1")
        self.assertEqual(report["seeds"], [11, 29, 47])
        self.assertEqual(report["horizon_per_seed"], 400)
        self.assertEqual(report["context_features"], [
            "collateral_type",
            "channel",
            "synthetic_segment",
            "journey_stage",
        ])
        self.assertNotIn("duration", report["dataset"]["feature_columns"])
        self.assertGreater(report["metrics"]["adaptive_reward_mean"], report["metrics"]["baseline_reward_mean"])
        self.assertGreater(report["metrics"]["uplift_mean"], 0)
        self.assertGreaterEqual(report["metrics"]["exploration_rate_mean"], 0)
        self.assertLessEqual(report["metrics"]["exploration_rate_mean"], 1)
        self.assertIn("adaptive_exposure", report["metrics"])
        self.assertIn("baseline_cumulative_reward_mean", report["metrics"])
        self.assertIn("adaptive_cumulative_reward_mean", report["metrics"])
        self.assertIn("adaptive_cumulative_regret_mean", report["metrics"])
        self.assertEqual(len(report["runs"]), 3)

        report_path = tmp_path / "run" / "report.json"
        policy_path = tmp_path / "run" / "policy.json"
        decisions_path = tmp_path / "run" / "evaluation_decisions.jsonl"
        self.assertTrue(report_path.exists())
        self.assertTrue(policy_path.exists())
        self.assertTrue(decisions_path.exists())

        policy = json.loads(policy_path.read_text(encoding="utf-8"))
        self.assertEqual(policy["policy_version"], "contextual_thompson_sampling_v0.1")
        self.assertEqual(policy["schema_version"], "adaptive_policy_artifact_v0.1")
        self.assertEqual(policy["priors"], {"alpha": 1.0, "beta": 1.0})
        self.assertEqual(policy["context_features"], report["context_features"])
        self.assertTrue(policy["posteriors"])
        self.assertIn("experiment_ref", policy)

        decisions = [
            json.loads(line)
            for line in decisions_path.read_text(encoding="utf-8").splitlines()
        ]
        self.assertTrue(decisions)
        self.assertTrue(all(item["policy_version"] for item in decisions))
        self.assertTrue(all(item["decision_id"] for item in decisions))
        self.assertTrue(all(item["request_id"] for item in decisions))
        self.assertTrue(all(item["reason_codes"] for item in decisions))
        self.assertTrue(all("requires_human_review" in item for item in decisions))
        self.assertTrue(all(item["requires_formal_credit_analysis"] for item in decisions))
        self.assertTrue(all("não representa aprovação" in item["message"] for item in decisions))
        self.assertTrue(all("eligible_actions" in item for item in decisions))
        self.assertTrue(all(item["selected_action"] in item["eligible_actions"] for item in decisions))
        self.assertTrue(all(item["audit_event_id"] for item in decisions))

    def test_same_configuration_is_deterministic_and_guardrails_limit_exploration(self):
        tmp_path = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, tmp_path, ignore_errors=True)

        first = self.run_experiment(tmp_path / "first")
        second = self.run_experiment(tmp_path / "second")

        self.assertEqual(first, second)
        first_policy = json.loads((tmp_path / "first" / "policy.json").read_text(encoding="utf-8"))
        second_policy = json.loads((tmp_path / "second" / "policy.json").read_text(encoding="utf-8"))
        self.assertEqual(first_policy, second_policy)

        decisions = [
            json.loads(line)
            for line in (tmp_path / "first" / "evaluation_decisions.jsonl").read_text(encoding="utf-8").splitlines()
        ]
        guarded = [item for item in decisions if item["guardrails_triggered"]]
        self.assertTrue(guarded)
        self.assertTrue(all(item["eligible_actions"] == ["no_offer_now"] for item in guarded))
        self.assertTrue(all(item["selected_action"] == "no_offer_now" for item in guarded))


if __name__ == "__main__":
    unittest.main()
