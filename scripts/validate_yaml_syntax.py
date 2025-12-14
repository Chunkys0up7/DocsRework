#!/usr/bin/env python3
"""
Validate YAML syntax for all artifact files
"""

import sys
import yaml
from pathlib import Path
from typing import List, Tuple
import argparse


def validate_yaml_file(file_path: Path) -> Tuple[bool, str]:
    """
    Validate YAML syntax for a single file

    Args:
        file_path: Path to YAML file

    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            yaml.safe_load(f)
        return True, ""
    except yaml.YAMLError as e:
        return False, str(e)
    except Exception as e:
        return False, f"Unexpected error: {str(e)}"


def validate_directory(directory: Path) -> List[Tuple[Path, bool, str]]:
    """
    Validate all YAML files in a directory

    Args:
        directory: Path to directory

    Returns:
        List of tuples (file_path, is_valid, error_message)
    """
    results = []

    # Find all .yml and .yaml files
    for ext in ['*.yml', '*.yaml']:
        for file_path in directory.rglob(ext):
            is_valid, error = validate_yaml_file(file_path)
            results.append((file_path, is_valid, error))

    return results


def main():
    parser = argparse.ArgumentParser(description='Validate YAML syntax')
    parser.add_argument('directory', type=str, help='Directory to validate')
    parser.add_argument('--verbose', action='store_true', help='Verbose output')

    args = parser.parse_args()

    directory = Path(args.directory)
    if not directory.exists():
        print(f"Error: Directory {directory} does not exist")
        sys.exit(1)

    print(f"Validating YAML files in {directory}...")

    results = validate_directory(directory)

    if not results:
        print(f"No YAML files found in {directory}")
        sys.exit(0)

    # Print results
    passed = sum(1 for _, is_valid, _ in results if is_valid)
    failed = len(results) - passed

    if args.verbose or failed > 0:
        for file_path, is_valid, error in results:
            status = "PASS" if is_valid else "FAIL"
            print(f"[{status}] {file_path}")
            if not is_valid:
                print(f"  Error: {error}")

    print(f"\nResults: {passed} passed, {failed} failed out of {len(results)} files")

    if failed > 0:
        sys.exit(1)

    print("All YAML files are valid")
    sys.exit(0)


if __name__ == '__main__':
    main()
