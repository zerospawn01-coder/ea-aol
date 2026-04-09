import json
import subprocess
import sys
import unittest
from pathlib import Path


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


if __name__ == "__main__":
    unittest.main()
