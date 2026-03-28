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
        self.assertTrue(
            (REPO_ROOT / "contracts" / "operations" / "describe_runtime_surface.md").is_file()
        )
        self.assertTrue(
            (REPO_ROOT / "contracts" / "operations" / "list_supported_operations.md").is_file()
        )
        self.assertTrue((REPO_ROOT / "contracts" / "schemas" / "operation.schema.json").is_file())
        self.assertTrue(
            (REPO_ROOT / "contracts" / "schemas" / "describe_runtime_surface.schema.json").is_file()
        )
        self.assertTrue(
            (REPO_ROOT / "contracts" / "schemas" / "list_supported_operations.schema.json").is_file()
        )

    def test_entrypoint_surface_imports(self) -> None:
        from src.entrypoint import describe_runtime_surface

        surface = describe_runtime_surface()
        self.assertEqual(surface["project"], "ea-aol")
        self.assertEqual(surface["status"], "bootstrap")
        self.assertEqual(surface["contract"], "contracts/system_contract.md")
        self.assertEqual(
            surface["supported_operations"],
            ["describe-runtime-surface", "list-supported-operations"],
        )


if __name__ == "__main__":
    unittest.main()
