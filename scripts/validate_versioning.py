#!/usr/bin/env python3
"""
Validate semantic versioning compliance for artifacts
"""

import sys
import yaml
import re
from pathlib import Path
from typing import List, Tuple
import argparse
import glob


# Semantic versioning pattern
SEMVER_PATTERN = re.compile(r'^\d+\.\d+\.\d+$')

# ID pattern: type:name:vX.Y.Z
ID_PATTERN = re.compile(r'^(atom|molecule|workflow|risk|control|regulation):([a-z0-9-]+):v(\d+\.\d+\.\d+)$')


def validate_versioning(file_path: Path, artifact_type: str) -> Tuple[bool, List[str]]:
    """
    Validate versioning for a single artifact

    Args:
        file_path: Path to artifact file
        artifact_type: Type of artifact (atom, molecule, workflow, etc.)

    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    errors = []

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)

        # Check ID format
        artifact_id = data.get('id')
        if not artifact_id:
            errors.append("Missing 'id' field")
        else:
            match = ID_PATTERN.match(artifact_id)
            if not match:
                errors.append(
                    f"Invalid ID format: {artifact_id}. "
                    f"Expected pattern: {artifact_type}:name:vX.Y.Z"
                )
            else:
                id_type, id_name, id_version = match.groups()

                # Verify type matches
                if id_type != artifact_type:
                    errors.append(
                        f"ID type '{id_type}' does not match artifact type '{artifact_type}'"
                    )

                # Verify version in ID matches version field
                version_field = data.get('version')
                if not version_field:
                    errors.append("Missing 'version' field")
                elif id_version != version_field:
                    errors.append(
                        f"Version mismatch: ID has 'v{id_version}' but version field is '{version_field}'"
                    )

        # Validate version field format
        version = data.get('version')
        if version and not SEMVER_PATTERN.match(version):
            errors.append(
                f"Invalid semantic version format: {version}. Expected X.Y.Z"
            )

        # Check for required fields
        if 'owner' not in data:
            errors.append("Missing 'owner' field")

        if 'steward' not in data:
            errors.append("Missing 'steward' field")

        # Validate email format for owner and steward
        email_pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')

        owner = data.get('owner', '')
        if owner and not email_pattern.match(owner):
            errors.append(f"Invalid email format for owner: {owner}")

        steward = data.get('steward', '')
        if steward and not email_pattern.match(steward):
            errors.append(f"Invalid email format for steward: {steward}")

        return len(errors) == 0, errors

    except yaml.YAMLError as e:
        return False, [f"YAML parsing error: {str(e)}"]
    except Exception as e:
        return False, [f"Unexpected error: {str(e)}"]


def main():
    parser = argparse.ArgumentParser(
        description='Validate semantic versioning compliance'
    )
    parser.add_argument(
        '--type',
        type=str,
        required=True,
        choices=['atom', 'molecule', 'workflow', 'risk', 'control', 'regulation'],
        help='Artifact type'
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

    # Find files
    files = [Path(f) for f in glob.glob(args.files, recursive=True)]

    if not files:
        print(f"No files found matching pattern: {args.files}")
        sys.exit(0)

    print(f"Validating versioning for {len(files)} {args.type} files...")

    # Validate each file
    results = []
    for file_path in files:
        is_valid, errors = validate_versioning(file_path, args.type)
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

    print("All files have valid versioning")
    sys.exit(0)


if __name__ == '__main__':
    main()
