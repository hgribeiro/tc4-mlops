import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from responsible_next_step.official_artifacts import (
    validate_official_experiment_artifacts,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
OFFICIAL_ARTIFACTS = REPO_ROOT / "artifacts" / "official-experiment"


class OfficialExperimentArtifactsTest(unittest.TestCase):
    def test_committed_evidence_is_complete_hash_verified_and_deploy_ready(self):
        summary = validate_official_experiment_artifacts(OFFICIAL_ARTIFACTS)

        self.assertEqual(summary["dataset_row_count"], 45_211)
        self.assertGreaterEqual(summary["seed_count"], 5)
        self.assertEqual(summary["horizon_per_seed"], 45_211)
        self.assertEqual(
            summary["validated_artifacts"],
            ["policy.json", "report.json"],
        )
        self.assertEqual(summary["actions_without_adaptive_exposure"], [])
        self.assertGreaterEqual(summary["context_count"], 3)
        self.assertTrue(summary["synthetic_offline_non_causal"])

    def test_validator_detects_artifact_tampering_without_downloading_source(self):
        tmp_path = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, tmp_path, ignore_errors=True)
        copied = tmp_path / "official-experiment"
        shutil.copytree(OFFICIAL_ARTIFACTS, copied)
        report_path = copied / "report.json"
        report_path.write_text(
            report_path.read_text(encoding="utf-8") + " ", encoding="utf-8"
        )

        with self.assertRaisesRegex(ValueError, "SHA-256.*report.json"):
            validate_official_experiment_artifacts(copied)

    def test_validator_rejects_raw_or_unapproved_files(self):
        tmp_path = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, tmp_path, ignore_errors=True)
        copied = tmp_path / "official-experiment"
        shutil.copytree(OFFICIAL_ARTIFACTS, copied)
        (copied / "bank-full.csv").write_text("raw data must not be published\n")

        with self.assertRaisesRegex(ValueError, "somente os artefatos derivados aprovados"):
            validate_official_experiment_artifacts(copied)

    def test_cli_validates_official_evidence_without_source_or_network(self):
        env = os.environ.copy()
        env["PYTHONPATH"] = str(REPO_ROOT / "src")
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "responsible_next_step",
                "validate-experiment-artifacts",
                "--artifact-dir",
                str(OFFICIAL_ARTIFACTS),
            ],
            cwd=REPO_ROOT,
            env=env,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        summary = json.loads(result.stdout)
        self.assertEqual(summary["dataset_row_count"], 45_211)
        self.assertTrue(summary["hashes_verified"])


if __name__ == "__main__":
    unittest.main()
