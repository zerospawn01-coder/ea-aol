import sys
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


class EntrypointContractTest(unittest.TestCase):
    def test_describe_runtime_surface_request_succeeds(self) -> None:
        from src.entrypoint import run_entrypoint

        response = run_entrypoint(
            {
                "operation": "describe-runtime-surface",
                "payload": {},
            }
        )

        self.assertTrue(response["ok"])
        self.assertEqual(response["operation"], "describe-runtime-surface")
        self.assertEqual(response["payload"], {})
        self.assertEqual(response["surface"]["project"], "ea-aol")
        self.assertEqual(
            response["surface"]["supported_operations"],
            ["describe-runtime-surface", "list-supported-operations"],
        )

    def test_list_supported_operations_request_succeeds(self) -> None:
        from src.entrypoint import run_entrypoint

        response = run_entrypoint(
            {
                "operation": "list-supported-operations",
                "payload": {},
            }
        )

        self.assertTrue(response["ok"])
        self.assertEqual(response["operation"], "list-supported-operations")
        self.assertEqual(
            response["operations"],
            ["describe-runtime-surface", "list-supported-operations"],
        )

    def test_missing_operation_fails_closed(self) -> None:
        from src.entrypoint import ContractViolationError, run_entrypoint

        with self.assertRaisesRegex(
            ContractViolationError,
            "Request.operation is required.",
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

    def test_unexpected_request_field_fails_closed(self) -> None:
        from src.entrypoint import ContractViolationError, run_entrypoint

        with self.assertRaisesRegex(
            ContractViolationError,
            "Unexpected request fields: metadata",
        ):
            run_entrypoint(
                {
                    "operation": "describe-runtime-surface",
                    "payload": {},
                    "metadata": {},
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

    def test_second_operation_rejects_payload_fields(self) -> None:
        from src.entrypoint import ContractViolationError, run_entrypoint

        with self.assertRaisesRegex(
            ContractViolationError,
            "Operation 'list-supported-operations' does not accept payload fields.",
        ):
            run_entrypoint(
                {
                    "operation": "list-supported-operations",
                    "payload": {"verbose": True},
                }
            )


if __name__ == "__main__":
    unittest.main()
