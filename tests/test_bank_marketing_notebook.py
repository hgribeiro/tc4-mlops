import contextlib
import io
import json
import os
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


REPO_ROOT = Path(__file__).resolve().parents[1]
NOTEBOOK_PATH = REPO_ROOT / "notebooks" / "bank-marketing-eda.ipynb"
FIXTURE_PATH = REPO_ROOT / "tests" / "fixtures" / "bank-full-small.csv"


class BankMarketingNotebookContractTest(unittest.TestCase):
    def test_notebook_runs_end_to_end_with_local_data_and_exports_prepared_artifacts(self):
        temporary_directory = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, temporary_directory, ignore_errors=True)
        output_directory = temporary_directory / "processed"

        notebook = json.loads(NOTEBOOK_PATH.read_text(encoding="utf-8"))
        namespace = {"__name__": "__main__"}
        stdout = io.StringIO()
        environment = {
            "BANK_MARKETING_CSV": str(FIXTURE_PATH),
            "BANK_MARKETING_PROCESSED_DIR": str(output_directory),
            "BANK_MARKETING_SEED": "42",
        }

        previous_cwd = Path.cwd()
        try:
            # nbconvert starts the kernel beside the notebook, not necessarily at repo root.
            os.chdir(NOTEBOOK_PATH.parent)
            with patch.dict(os.environ, environment, clear=False), contextlib.redirect_stdout(stdout):
                for cell in notebook["cells"]:
                    if cell["cell_type"] == "code":
                        source = "".join(cell["source"])
                        exec(compile(source, NOTEBOOK_PATH.name, "exec"), namespace)
        finally:
            os.chdir(previous_cwd)

        self.assertEqual(namespace["repo_root"], REPO_ROOT)
        report = stdout.getvalue()
        self.assertIn("Dimensões", report)
        self.assertIn("Distribuição do target", report)
        self.assertIn("Qualidade básica", report)
        self.assertIn("Decisões de tratamento", report)

        features_path = output_directory / "features.jsonl"
        target_path = output_directory / "target.csv"
        metadata_path = output_directory / "metadata.json"
        self.assertTrue(features_path.exists())
        self.assertTrue(target_path.exists())
        self.assertTrue(metadata_path.exists())
        self.assertNotIn("duration", features_path.read_text(encoding="utf-8"))
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        self.assertEqual(metadata["random_seed"], 42)
        self.assertEqual(metadata["row_count"], 4)


if __name__ == "__main__":
    unittest.main()
