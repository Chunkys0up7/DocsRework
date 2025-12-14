#!/usr/bin/env python3
"""
Validate YAML artifacts against JSON schemas
"""

import sys
import json
import yaml
from pathlib import Path
from typing import List, Tuple, Dict, Any
import argparse
from jsonschema import validate, ValidationError, Draft7Validator
import glob


def load_schema(schema_path: Path) -> Dict[str, Any]:
    """Load JSON schema from file"""
    with open(schema_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_yaml(yaml_path: Path) -> Dict[str, Any]:
    """Load YAML file"""
    with open(yaml_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def validate_file_against_schema(
    file_path: Path,
    schema: Dict[str, Any]
) -> Tuple[bool, List[str]]:
    """
    Validate a YAML file against a JSON schema

    Args:
        file_path: Path to YAML file
        schema: JSON schema dictionary

    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    try:
        data = load_yaml(file_path)
        validator = Draft7Validator(schema)
        errors = list(validator.iter_errors(data))

        if errors:
            error_messages = []
            for error in errors:
                path = ".".join(str(p) for p in error.path) if error.path else "root"
                error_messages.append(f"{path}: {error.message}")
            return False, error_messages

        return True, []

    except yaml.YAMLError as e:
        return False, [f"YAML parsing error: {str(e)}"]
    except Exception as e:
        return False, [f"Unexpected error: {str(e)}"]


def main():
    parser = argparse.ArgumentParser(
        description='Validate YAML artifacts against JSON schemas'
    )
    parser.add_argument(
        '--schema',
        type=str,
        required=True,
        help='Path to JSON schema file'
    )
    parser.add_argument(
        '--files',
        type=str,
        required=True,
        help='Glob pattern for files to validate'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Verbose output'
    )

    args = parser.parse_args()

    # Load schema
    schema_path = Path(args.schema)
    if not schema_path.exists():
        print(f"Error: Schema file {schema_path} does not exist")
        sys.exit(1)

    try:
        schema = load_schema(schema_path)
    except Exception as e:
        print(f"Error loading schema: {e}")
        sys.exit(1)

    # Find files
    files = [Path(f) for f in glob.glob(args.files, recursive=True)]

    if not files:
        print(f"No files found matching pattern: {args.files}")
        sys.exit(0)

    print(f"Validating {len(files)} files against {schema_path.name}...")

    # Validate each file
    results = []
    for file_path in files:
        is_valid, errors = validate_file_against_schema(file_path, schema)
        results.append((file_path, is_valid, errors))

    # Print results
    passed = sum(1 for _, is_valid, _ in results if is_valid)
    failed = len(results) - passed

    if args.verbose or failed > 0:
        for file_path, is_valid, errors in results:
            status = "PASS" if is_valid else "FAIL"
            print(f"[{status}] {file_path}")
            if not is_valid:
                for error in errors:
                    print(f"  - {error}")

    print(f"\nResults: {passed} passed, {failed} failed out of {len(results)} files")

    if failed > 0:
        sys.exit(1)

    print("All files are valid according to the schema")
    sys.exit(0)


if __name__ == '__main__':
    main()
