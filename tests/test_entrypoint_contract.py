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

        self.assertEqual(response["status"], "ok")
        self.assertEqual(response["operation"], "describe-runtime-surface")
        self.assertEqual(response["contract_version"], "ea-aol/0.1")
        self.assertEqual(response["result"]["project"], "ea-aol")
        self.assertEqual(
            response["result"]["supported_operations"],
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

        self.assertEqual(response["status"], "ok")
        self.assertEqual(response["operation"], "list-supported-operations")
        self.assertEqual(response["contract_version"], "ea-aol/0.1")
        self.assertEqual(
            response["result"]["operations"],
            ["describe-runtime-surface", "list-supported-operations"],
        )

    def test_missing_operation_returns_validation_error_shape(self) -> None:
        from src.entrypoint import run_entrypoint

        response = run_entrypoint({"payload": {}})
        self.assertEqual(response["status"], "error")
        self.assertEqual(response["operation"], "unknown")
        self.assertEqual(response["error"]["code"], "validation_error")
        self.assertEqual(response["error"]["category"], "validation")
        self.assertFalse(response["error"]["retryable"])
        self.assertIn("Request.operation is required.", response["error"]["message"])

    def test_invalid_payload_returns_validation_error_shape(self) -> None:
        from src.entrypoint import run_entrypoint

        response = run_entrypoint(
            {
                "operation": "describe-runtime-surface",
                "payload": "invalid",
            }
        )
        self.assertEqual(response["status"], "error")
        self.assertEqual(response["operation"], "describe-runtime-surface")
        self.assertEqual(response["error"]["code"], "validation_error")
        self.assertEqual(response["error"]["category"], "validation")
        self.assertIn("Request.payload must be a mapping.", response["error"]["message"])

    def test_unexpected_request_field_returns_validation_error_shape(self) -> None:
        from src.entrypoint import run_entrypoint

        response = run_entrypoint(
            {
                "operation": "describe-runtime-surface",
                "payload": {},
                "metadata": {},
            }
        )
        self.assertEqual(response["status"], "error")
        self.assertEqual(response["error"]["code"], "validation_error")
        self.assertIn("Unexpected request fields: metadata", response["error"]["message"])

    def test_unsupported_operation_returns_unsupported_error_shape(self) -> None:
        from src.entrypoint import run_entrypoint

        response = run_entrypoint(
            {
                "operation": "bootstrap-runtime",
                "payload": {},
            }
        )
        self.assertEqual(response["status"], "error")
        self.assertEqual(response["operation"], "bootstrap-runtime")
        self.assertEqual(response["error"]["code"], "unsupported_operation")
        self.assertEqual(response["error"]["category"], "unsupported")
        self.assertFalse(response["error"]["retryable"])

    def test_second_operation_rejects_payload_fields_with_error_shape(self) -> None:
        from src.entrypoint import run_entrypoint

        response = run_entrypoint(
            {
                "operation": "list-supported-operations",
                "payload": {"verbose": True},
            }
        )
        self.assertEqual(response["status"], "error")
        self.assertEqual(response["error"]["code"], "validation_error")
        self.assertIn(
            "Operation 'list-supported-operations' does not accept payload fields.",
            response["error"]["message"],
        )

    def test_internal_failure_returns_internal_error_shape(self) -> None:
        import src.entrypoint as entrypoint

        original_handler = entrypoint.HANDLERS["list-supported-operations"]

        def boom(_payload: dict[str, object]) -> dict[str, object]:
            raise RuntimeError("boom")

        entrypoint.HANDLERS["list-supported-operations"] = boom
        try:
            response = entrypoint.run_entrypoint(
                {
                    "operation": "list-supported-operations",
                    "payload": {},
                }
            )
        finally:
            entrypoint.HANDLERS["list-supported-operations"] = original_handler

        self.assertEqual(response["status"], "error")
        self.assertEqual(response["error"]["code"], "internal_error")
        self.assertEqual(response["error"]["category"], "internal")
        self.assertFalse(response["error"]["retryable"])
        self.assertEqual(response["error"]["message"], "boom")


if __name__ == "__main__":
    unittest.main()
