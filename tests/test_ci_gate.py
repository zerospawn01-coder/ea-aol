import json
import subprocess
import sys
import unittest
from io import StringIO
from pathlib import Path
from contextlib import redirect_stdout


REPO_ROOT = Path(__file__).resolve().parents[1]


class CiGateTest(unittest.TestCase):
    def run_gate(self, gate: str) -> dict[str, object]:
        completed = subprocess.run(
            [sys.executable, "tools/ci_gate.py", gate],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(completed.returncode, 0, msg=completed.stdout + completed.stderr)
        return json.loads(completed.stdout)

    def test_validate_schema_gate_passes(self) -> None:
        payload = self.run_gate("validate-schema")
        self.assertEqual(payload["status"], "PASS")
        self.assertEqual(payload["gate"], "validate-schema")

    def test_validate_completeness_gate_passes(self) -> None:
        payload = self.run_gate("validate-completeness")
        self.assertEqual(payload["status"], "PASS")
        self.assertEqual(payload["gate"], "validate-completeness")

    def test_validate_response_contract_gate_passes(self) -> None:
        payload = self.run_gate("validate-response-contract")
        self.assertEqual(payload["status"], "PASS")
        self.assertEqual(payload["gate"], "validate-response-contract")

    def test_validate_governance_gate_passes(self) -> None:
        payload = self.run_gate("validate-governance")
        self.assertEqual(payload["status"], "PASS")
        self.assertEqual(payload["gate"], "validate-governance")

    def test_unknown_internal_gate_errors_are_normalized(self) -> None:
        sys.path.insert(0, str(REPO_ROOT))
        try:
            import tools.ci_gate as ci_gate
        finally:
            sys.path.pop(0)

        original_gate = ci_gate.GATES["validate-schema"]

        def boom() -> int:
            raise RuntimeError("boom")

        ci_gate.GATES["validate-schema"] = boom
        try:
            stdout = StringIO()
            with redirect_stdout(stdout):
                code = ci_gate.main(["tools/ci_gate.py", "validate-schema"])
        finally:
            ci_gate.GATES["validate-schema"] = original_gate

        self.assertEqual(code, 1)
        payload = json.loads(stdout.getvalue())
        self.assertEqual(payload["status"], "FAIL")
        self.assertEqual(payload["gate"], "validate-schema")
        self.assertEqual(payload["violations"][0]["type"], "INTERNAL_CI_ERROR")


if __name__ == "__main__":
    unittest.main()
