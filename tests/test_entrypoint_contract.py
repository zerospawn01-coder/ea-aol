import sys
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


class EntrypointContractTest(unittest.TestCase):
    def test_completeness_check_passes_for_current_registry(self) -> None:
        import src.entrypoint as entrypoint
        from src.contract_runtime import assert_contract_completeness

        assert_contract_completeness(entrypoint.HANDLERS)

    def test_completeness_check_fails_when_handler_is_missing(self) -> None:
        import src.entrypoint as entrypoint
        from src.contract_runtime import ContractViolationError, assert_contract_completeness

        incomplete_handlers = dict(entrypoint.HANDLERS)
        incomplete_handlers.pop("validate-request-envelope")

        with self.assertRaisesRegex(
            ContractViolationError,
            "Operation manifest keys must match handler registry.",
        ):
            assert_contract_completeness(incomplete_handlers)

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
            [
                "describe-runtime-surface",
                "list-supported-operations",
                "validate-request-envelope",
                "normalize-module-definition",
                "validate-module-definition",
            ],
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
            [
                "describe-runtime-surface",
                "list-supported-operations",
                "validate-request-envelope",
                "normalize-module-definition",
                "validate-module-definition",
            ],
        )

    def test_normalize_module_definition_request_succeeds(self) -> None:
        from src.entrypoint import run_entrypoint

        response = run_entrypoint(
            {
                "operation": "normalize-module-definition",
                "payload": {
                    "module_definition": {
                        "name": "  runtime.bootstrap  ",
                        "kind": "runtime",
                        "capabilities": [" dispatch ", "contracts", "dispatch"],
                        "entrypoint": {
                            "module": " src.entrypoint ",
                            "callable": " run_entrypoint ",
                        },
                    }
                },
            }
        )

        self.assertEqual(response["status"], "ok")
        self.assertEqual(response["operation"], "normalize-module-definition")
        self.assertEqual(response["contract_version"], "ea-aol/0.1")
        self.assertEqual(
            response["result"]["normalized_module"],
            {
                "name": "runtime.bootstrap",
                "kind": "runtime",
                "capabilities": ["contracts", "dispatch"],
                "entrypoint": {
                    "module": "src.entrypoint",
                    "callable": "run_entrypoint",
                },
            },
        )
        self.assertTrue(response["result"]["ready_for_runtime_registration"])

    def test_normalize_module_definition_is_deterministic_across_order_and_spacing(self) -> None:
        from src.entrypoint import run_entrypoint

        first = run_entrypoint(
            {
                "operation": "normalize-module-definition",
                "payload": {
                    "module_definition": {
                        "name": " runtime.bootstrap ",
                        "kind": "runtime",
                        "capabilities": [" dispatch", "contracts ", "dispatch"],
                        "entrypoint": {
                            "module": " src.entrypoint",
                            "callable": "run_entrypoint ",
                        },
                    }
                },
            }
        )
        second = run_entrypoint(
            {
                "operation": "normalize-module-definition",
                "payload": {
                    "module_definition": {
                        "name": "runtime.bootstrap",
                        "kind": "runtime",
                        "capabilities": ["contracts", "dispatch"],
                        "entrypoint": {
                            "module": "src.entrypoint",
                            "callable": "run_entrypoint",
                        },
                    }
                },
            }
        )

        self.assertEqual(first["status"], "ok")
        self.assertEqual(second["status"], "ok")
        self.assertEqual(first["result"]["normalized_module"], second["result"]["normalized_module"])

    def test_validate_module_definition_request_succeeds(self) -> None:
        from src.entrypoint import run_entrypoint

        response = run_entrypoint(
            {
                "operation": "validate-module-definition",
                "payload": {
                    "module_definition": {
                        "name": " runtime.bootstrap ",
                        "kind": "runtime",
                        "capabilities": ["dispatch", "contracts"],
                        "entrypoint": {
                            "module": " src.entrypoint ",
                            "callable": " run_entrypoint ",
                        },
                    }
                },
            }
        )

        self.assertEqual(response["status"], "ok")
        self.assertEqual(response["operation"], "validate-module-definition")
        self.assertTrue(response["result"]["valid"])
        self.assertEqual(
            response["result"]["normalized_module"],
            {
                "name": "runtime.bootstrap",
                "kind": "runtime",
                "capabilities": ["contracts", "dispatch"],
                "entrypoint": {
                    "module": "src.entrypoint",
                    "callable": "run_entrypoint",
                },
            },
        )

    def test_validate_request_envelope_request_succeeds(self) -> None:
        from src.entrypoint import run_entrypoint

        response = run_entrypoint(
            {
                "operation": "validate-request-envelope",
                "payload": {
                    "candidate_request": {
                        "operation": "list-supported-operations",
                        "payload": {},
                    }
                },
            }
        )

        self.assertEqual(response["status"], "ok")
        self.assertEqual(response["operation"], "validate-request-envelope")
        self.assertEqual(response["contract_version"], "ea-aol/0.1")
        self.assertTrue(response["result"]["valid"])
        self.assertEqual(
            response["result"]["normalized_request"],
            {
                "operation": "list-supported-operations",
                "payload": {},
            },
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
            "Unexpected fields at payload: verbose",
            response["error"]["message"],
        )

    def test_validate_request_envelope_rejects_invalid_candidate(self) -> None:
        from src.entrypoint import run_entrypoint

        response = run_entrypoint(
            {
                "operation": "validate-request-envelope",
                "payload": {
                    "candidate_request": {
                        "payload": {},
                    }
                },
            }
        )

        self.assertEqual(response["status"], "error")
        self.assertEqual(response["operation"], "validate-request-envelope")
        self.assertEqual(response["error"]["code"], "validation_error")
        self.assertIn("Request.operation is required.", response["error"]["message"])

    def test_normalize_module_definition_rejects_invalid_kind(self) -> None:
        from src.entrypoint import run_entrypoint

        response = run_entrypoint(
            {
                "operation": "normalize-module-definition",
                "payload": {
                    "module_definition": {
                        "name": "runtime.bootstrap",
                        "kind": "service",
                        "capabilities": ["dispatch"],
                        "entrypoint": {
                            "module": "src.entrypoint",
                            "callable": "run_entrypoint",
                        },
                    }
                },
            }
        )

        self.assertEqual(response["status"], "error")
        self.assertEqual(response["operation"], "normalize-module-definition")
        self.assertEqual(response["error"]["code"], "validation_error")
        self.assertIn("payload.module_definition.kind must be one of", response["error"]["message"])

    def test_normalize_module_definition_rejects_blank_after_normalization(self) -> None:
        from src.entrypoint import run_entrypoint

        response = run_entrypoint(
            {
                "operation": "normalize-module-definition",
                "payload": {
                    "module_definition": {
                        "name": "runtime.bootstrap",
                        "kind": "runtime",
                        "capabilities": ["   "],
                        "entrypoint": {
                            "module": "src.entrypoint",
                            "callable": "run_entrypoint",
                        },
                    }
                },
            }
        )

        self.assertEqual(response["status"], "error")
        self.assertEqual(response["operation"], "normalize-module-definition")
        self.assertEqual(response["error"]["code"], "validation_error")
        self.assertIn(
            "payload.module_definition.capabilities[0] must not be empty after normalization.",
            response["error"]["message"],
        )

    def test_validate_module_definition_rejects_blank_callable_after_normalization(self) -> None:
        from src.entrypoint import run_entrypoint

        response = run_entrypoint(
            {
                "operation": "validate-module-definition",
                "payload": {
                    "module_definition": {
                        "name": "runtime.bootstrap",
                        "kind": "runtime",
                        "capabilities": ["dispatch"],
                        "entrypoint": {
                            "module": "src.entrypoint",
                            "callable": "   ",
                        },
                    }
                },
            }
        )

        self.assertEqual(response["status"], "error")
        self.assertEqual(response["operation"], "validate-module-definition")
        self.assertEqual(response["error"]["code"], "validation_error")
        self.assertIn(
            "payload.module_definition.entrypoint.callable must not be empty after normalization.",
            response["error"]["message"],
        )

    def test_internal_failure_returns_internal_error_shape(self) -> None:
        import src.entrypoint as entrypoint

        original_handler = entrypoint.HANDLERS["list-supported-operations"]

        def boom(_payload: dict[str, object]) -> dict[str, object]:
            raise RuntimeError("boom")

        boom.__name__ = original_handler.__name__
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
