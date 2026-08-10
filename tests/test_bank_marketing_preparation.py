import unittest
from pathlib import Path

from responsible_next_step.bank_marketing import prepare_bank_marketing


REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURE_PATH = REPO_ROOT / "tests" / "fixtures" / "bank-full-small.csv"


class BankMarketingPreparationContractTest(unittest.TestCase):
    def test_prepares_minimized_features_target_and_lineage(self):
        prepared = prepare_bank_marketing(FIXTURE_PATH, seed=42)

        self.assertEqual(len(prepared.features), 4)
        self.assertCountEqual(prepared.target, (0, 1, 0, 1))
        self.assertEqual(
            set(prepared.features[0]),
            {
                "contact_channel_proxy",
                "contact_repetition_count",
                "days_since_previous_contact",
                "previous_contact_count",
                "previous_outcome",
            },
        )
        all_feature_names = set().union(*(row.keys() for row in prepared.features))
        self.assertNotIn("duration", all_feature_names)
        self.assertTrue(
            {
                "age",
                "job",
                "marital",
                "education",
                "default",
                "balance",
                "housing",
                "loan",
                "day",
                "month",
                "duration",
            }.issubset(prepared.metadata["excluded_columns"])
        )
        self.assertEqual(prepared.metadata["source_dataset"], "bank_marketing_public_proxy")
        self.assertEqual(prepared.metadata["source_version"], "UCI dataset 222 / bank-full.csv")
        self.assertEqual(prepared.metadata["schema_version"], "bank_marketing_prepared_v0.1")
        self.assertEqual(prepared.metadata["random_seed"], 42)
        self.assertEqual(prepared.metadata["row_count"], 4)
        self.assertEqual(prepared.metadata["target_name"], "y")
        self.assertEqual(len(prepared.metadata["source_sha256"]), 64)

    def test_fixed_seed_reproduces_the_prepared_experiment_order(self):
        first = prepare_bank_marketing(FIXTURE_PATH, seed=20260629)
        second = prepare_bank_marketing(FIXTURE_PATH, seed=20260629)
        another_seed = prepare_bank_marketing(FIXTURE_PATH, seed=7)

        self.assertEqual(first, second)
        self.assertNotEqual(first.features, another_seed.features)
        self.assertEqual(first.metadata["source_sha256"], another_seed.metadata["source_sha256"])

    def test_rejects_an_invalid_target_instead_of_silently_coercing_it(self):
        invalid_path = REPO_ROOT / "tests" / "fixtures" / "bank-full-invalid-target.csv"

        with self.assertRaisesRegex(ValueError, "target 'y'.*maybe"):
            prepare_bank_marketing(invalid_path, seed=42)


if __name__ == "__main__":
    unittest.main()
