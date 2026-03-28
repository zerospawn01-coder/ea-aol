import sys
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


class ContractSmokeTest(unittest.TestCase):
    def test_expected_boundary_exists(self) -> None:
        self.assertTrue((REPO_ROOT / "docs").is_dir())
        self.assertTrue((REPO_ROOT / "contracts").is_dir())
        self.assertTrue((REPO_ROOT / "src").is_dir())
        self.assertTrue((REPO_ROOT / "tests").is_dir())

    def test_contract_document_exists(self) -> None:
        self.assertTrue((REPO_ROOT / "contracts" / "system_contract.md").is_file())

    def test_entrypoint_surface_imports(self) -> None:
        from src.entrypoint import describe_runtime_surface

        surface = describe_runtime_surface()
        self.assertEqual(surface["project"], "ea-aol")
        self.assertEqual(surface["status"], "bootstrap")
        self.assertEqual(surface["contract"], "contracts/system_contract.md")
        self.assertEqual(surface["supported_operations"], "describe-runtime-surface")

    def test_valid_entrypoint_request_succeeds(self) -> None:
        from src.entrypoint import run_entrypoint

        response = run_entrypoint(
            {
                "operation": "describe-runtime-surface",
                "payload": {},
            }
        )

        self.assertTrue(response["ok"])
        self.assertEqual(response["operation"], "describe-runtime-surface")
        self.assertEqual(response["surface"]["project"], "ea-aol")

    def test_missing_operation_fails_closed(self) -> None:
        from src.entrypoint import ContractViolationError, run_entrypoint

        with self.assertRaisesRegex(
            ContractViolationError,
            "Request.operation must be a non-empty string.",
        ):
            run_entrypoint({"payload": {}})

    def test_invalid_payload_fails_closed(self) -> None:
        from src.entrypoint import ContractViolationError, run_entrypoint

        with self.assertRaisesRegex(
            ContractViolationError,
            "Request.payload must be a mapping.",
        ):
            run_entrypoint(
                {
                    "operation": "describe-runtime-surface",
                    "payload": "invalid",
                }
            )

    def test_unsupported_operation_fails_closed(self) -> None:
        from src.entrypoint import ContractViolationError, run_entrypoint

        with self.assertRaisesRegex(
            ContractViolationError,
            "Unsupported operation: bootstrap-runtime",
        ):
            run_entrypoint(
                {
                    "operation": "bootstrap-runtime",
                    "payload": {},
                }
            )


if __name__ == "__main__":
    unittest.main()
