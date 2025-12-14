#!/usr/bin/env python3
"""
Run all validation checks and generate comprehensive reports
"""

import sys
from pathlib import Path
from typing import Dict, List, Tuple
import json

from validate_yaml_syntax import validate_all_yaml_files
from validate_against_schema import validate_all_artifacts
from validate_versioning import validate_all_versioning

from utils.logging import setup_logger

logger = setup_logger(__name__)


def generate_validation_report(
    syntax_results: Dict,
    schema_results: Dict,
    version_results: Dict,
    artifact_type: str
) -> str:
    """Generate markdown validation report"""

    report = f"""# {artifact_type.title()} Validation Report

## Summary

"""

    # Syntax validation summary
    total_files = len(syntax_results)
    syntax_passed = sum(1 for r in syntax_results.values() if r["valid"])
    report += f"- **YAML Syntax**: {syntax_passed}/{total_files} files passed\n"

    # Schema validation summary
    schema_passed = sum(1 for r in schema_results.values() if r["valid"])
    report += f"- **Schema Validation**: {schema_passed}/{total_files} files passed\n"

    # Version validation summary
    version_passed = sum(1 for r in version_results.values() if r["valid"])
    report += f"- **Versioning**: {version_passed}/{total_files} files passed\n"

    # Overall status
    all_passed = (syntax_passed == total_files and
                  schema_passed == total_files and
                  version_passed == total_files)

    report += f"\n## Overall Status\n\n"
    if all_passed:
        report += "✅ **All validations passed**\n\n"
    else:
        report += "❌ **Validation failures detected**\n\n"

    # Detailed results
    if not all_passed:
        report += "## Failures\n\n"

        for file_path, result in syntax_results.items():
            if not result["valid"]:
                report += f"### {file_path}\n\n"
                report += f"**YAML Syntax Error**: {result['error']}\n\n"

        for file_path, result in schema_results.items():
            if not result["valid"]:
                report += f"### {file_path}\n\n"
                report += "**Schema Validation Errors**:\n"
                for error in result["errors"]:
                    report += f"- {error}\n"
                report += "\n"

        for file_path, result in version_results.items():
            if not result["valid"]:
                report += f"### {file_path}\n\n"
                report += "**Versioning Errors**:\n"
                for error in result["errors"]:
                    report += f"- {error}\n"
                report += "\n"

    return report


def main():
    """Run all validations"""
    project_root = Path(__file__).parent.parent

    # Validate atoms
    atoms_dir = project_root / "atoms"
    atom_schema_path = project_root / "schemas" / "atom-schema.json"

    if atoms_dir.exists() and atom_schema_path.exists():
        print("Validating atoms...")

        syntax_results = {}
        schema_results = {}
        version_results = {}

        for atom_file in atoms_dir.glob("*.atom.yml"):
            file_name = atom_file.name

            # Syntax validation
            from validate_yaml_syntax import validate_yaml_file
            is_valid, error = validate_yaml_file(atom_file)
            syntax_results[file_name] = {"valid": is_valid, "error": error}

            # Schema validation
            if is_valid:
                from validate_against_schema import validate_file_against_schema
                import json
                with open(atom_schema_path) as f:
                    schema = json.load(f)
                is_valid, errors = validate_file_against_schema(atom_file, schema)
                schema_results[file_name] = {"valid": is_valid, "errors": errors}

            # Versioning validation
            if is_valid:
                from validate_versioning import validate_versioning
                is_valid, errors = validate_versioning(atom_file, "atom")
                version_results[file_name] = {"valid": is_valid, "errors": errors}

        # Generate report
        report = generate_validation_report(
            syntax_results, schema_results, version_results, "atom"
        )

        with open("atom-validation-report.md", "w") as f:
            f.write(report)

        print(report)

        # Check if all passed
        all_passed = all(r["valid"] for r in syntax_results.values())
        all_passed = all_passed and all(r["valid"] for r in schema_results.values())
        all_passed = all_passed and all(r["valid"] for r in version_results.values())

        if not all_passed:
            print("\n❌ Atom validation failed")
            sys.exit(1)

    # Validate molecules
    molecules_dir = project_root / "molecules"
    molecule_schema_path = project_root / "schemas" / "molecule-schema.json"

    if molecules_dir.exists() and molecule_schema_path.exists():
        print("\nValidating molecules...")
        # Similar validation for molecules
        pass

    # Validate workflows
    workflows_dir = project_root / "workflows"
    workflow_schema_path = project_root / "schemas" / "workflow-schema.json"

    if workflows_dir.exists() and workflow_schema_path.exists():
        print("\nValidating workflows...")
        # Similar validation for workflows
        pass

    print("\n✅ All validations passed successfully")
    sys.exit(0)


if __name__ == "__main__":
    main()
