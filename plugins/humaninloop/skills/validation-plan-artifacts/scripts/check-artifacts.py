#!/usr/bin/env python3
"""
Plan Artifact Validation Script

Automates common artifact checks for plan phase outputs including:
- Unresolved markers ([NEEDS CLARIFICATION], [TBD], [TODO], [PLACEHOLDER])
- Required sections based on file type
- Traceability references (FR-XXX, US-XXX)
- PII annotations for sensitive fields
- Entity consistency across multiple files

Usage:
    python check-artifacts.py <file1> [file2] ...

Exit codes:
    0 - All checks passed
    1 - One or more checks failed
"""

import sys
import os
import re
import json
from pathlib import Path
from typing import Dict, List, Tuple, Set, Any


# Markers that indicate unresolved content
UNRESOLVED_MARKERS = [
    r'\[NEEDS CLARIFICATION\]',
    r'\[TBD\]',
    r'\[TODO\]',
    r'\[PLACEHOLDER\]',
]

# Required sections by file type (filename pattern -> list of required headers)
REQUIRED_SECTIONS = {
    'research.md': [
        '## Technical Decisions',
        '## Alternatives Considered',
        '## Rationale',
    ],
    'data-model.md': [
        '## Entities',
        '## Relationships',
        '## Validation Rules',
    ],
}

# Common PII field patterns (case insensitive)
PII_FIELD_PATTERNS = [
    r'\bemail\b',
    r'\bphone\b',
    r'\bssn\b',
    r'\bsocial.?security\b',
    r'\baddress\b',
    r'\b(?:first|last|full).?name\b',
    r'\bdate.?of.?birth\b',
    r'\bdob\b',
    r'\bpassword\b',
    r'\bcredit.?card\b',
    r'\bbank.?account\b',
]

# Entity name pattern (capitalized words in backticks - most reliable indicator)
ENTITY_PATTERN = r'`([A-Z][a-zA-Z0-9]+)`'

# Common section header words to exclude from entity detection
SECTION_HEADERS = {
    'entities', 'relationships', 'validation', 'rules', 'technical',
    'decisions', 'alternatives', 'considered', 'rationale', 'overview',
    'summary', 'introduction', 'conclusion', 'notes', 'references',
    'requirements', 'constraints', 'assumptions', 'dependencies',
    'authentication', 'authorization', 'security', 'performance',
    'scalability', 'monitoring', 'logging', 'testing', 'deployment',
}


def read_file(filepath: str) -> Tuple[str, List[str]]:
    """Read file and return content and lines."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = content.split('\n')
        return content, lines
    except Exception as e:
        return '', []


def check_unresolved_markers(content: str, lines: List[str]) -> Dict[str, Any]:
    """Check for unresolved markers in the content."""
    issues = []

    for marker_pattern in UNRESOLVED_MARKERS:
        marker_regex = re.compile(marker_pattern, re.IGNORECASE)
        for line_num, line in enumerate(lines, 1):
            matches = marker_regex.findall(line)
            for match in matches:
                marker_text = match if match else marker_pattern.replace('\\[', '[').replace('\\]', ']')
                issues.append(f"Line {line_num}: {marker_text} marker found")

    return {
        'check': 'unresolved_markers',
        'passed': len(issues) == 0,
        'issues': issues
    }


def check_required_sections(filepath: str, content: str) -> Dict[str, Any]:
    """Check for required markdown sections based on file type."""
    filename = os.path.basename(filepath).lower()
    issues = []

    # Find matching file type
    required = None
    for pattern, sections in REQUIRED_SECTIONS.items():
        if pattern.lower() in filename:
            required = sections
            break

    # Skip if no required sections defined for this file type
    if required is None:
        return {
            'check': 'required_sections',
            'passed': True,
            'issues': [],
            'skipped': True,
            'reason': f'No required sections defined for file type: {filename}'
        }

    # Check for each required section
    content_lower = content.lower()
    for section in required:
        section_lower = section.lower()
        if section_lower not in content_lower:
            issues.append(f"Missing required section: {section}")

    return {
        'check': 'required_sections',
        'passed': len(issues) == 0,
        'issues': issues
    }


def check_traceability(content: str) -> Dict[str, Any]:
    """Check for FR-XXX or US-XXX references."""
    # Pattern for functional requirements (FR-001, FR-1, FR-ABC-001, etc.)
    fr_pattern = r'\bFR-[A-Z0-9]+-?[0-9]*\b|\bFR-[0-9]+\b'
    # Pattern for user stories (US-001, US-1, US-ABC-001, etc.)
    us_pattern = r'\bUS-[A-Z0-9]+-?[0-9]*\b|\bUS-[0-9]+\b'

    fr_matches = set(re.findall(fr_pattern, content, re.IGNORECASE))
    us_matches = set(re.findall(us_pattern, content, re.IGNORECASE))

    fr_count = len(fr_matches)
    us_count = len(us_matches)

    has_traceability = fr_count > 0 or us_count > 0
    issues = []

    if not has_traceability:
        issues.append("No FR-XXX or US-XXX traceability references found in document")

    return {
        'check': 'traceability',
        'passed': has_traceability,
        'fr_count': fr_count,
        'us_count': us_count,
        'issues': issues
    }


def check_pii_markers(filepath: str, content: str, lines: List[str]) -> Dict[str, Any]:
    """Check if PII fields have [PII] annotation nearby."""
    filename = os.path.basename(filepath).lower()
    issues = []

    # Only check data-model files
    if 'data-model' not in filename and 'datamodel' not in filename and 'model' not in filename:
        return {
            'check': 'pii_markers',
            'passed': True,
            'issues': [],
            'skipped': True,
            'reason': 'Not a data model file'
        }

    # Check each line for PII fields
    # Only check lines that look like field definitions (contain : or have list/table format)
    field_definition_pattern = r'^[\s\-\*\|]*[a-zA-Z_]+[\s]*[:\|]'

    for line_num, line in enumerate(lines, 1):
        line_lower = line.lower()

        # Skip lines that don't look like field definitions
        if not re.match(field_definition_pattern, line):
            continue

        for pii_pattern in PII_FIELD_PATTERNS:
            if re.search(pii_pattern, line_lower):
                # Check if [PII] annotation exists on same line only
                # Field definitions should have [PII] annotation directly on the field line
                if '[PII]' not in line and '[pii]' not in line_lower:
                    # Extract the field name for clearer messaging
                    match = re.search(pii_pattern, line_lower)
                    if match:
                        field_name = match.group(0).strip()
                        issues.append(f"Line {line_num}: '{field_name}' field may need [PII] annotation")
                break  # Only report once per line

    # Deduplicate issues (same field might match multiple patterns)
    unique_issues = list(dict.fromkeys(issues))

    return {
        'check': 'pii_markers',
        'passed': len(unique_issues) == 0,
        'issues': unique_issues
    }


def extract_entities(content: str) -> Set[str]:
    """Extract entity names from content.

    Focuses on backtick-wrapped entities as the most reliable indicator
    of domain model entities (e.g., `User`, `Order`, `Product`).
    """
    entities = set()

    # Match backtick entities - most reliable indicator
    matches = re.findall(ENTITY_PATTERN, content)
    for match in matches:
        entity = match if isinstance(match, str) else match[0]
        if entity and len(entity) > 1:
            # Skip common section header words
            if entity.lower() not in SECTION_HEADERS:
                entities.add(entity)

    # Also match explicit entity declaration patterns
    # e.g., "### User Entity" or "#### UserProfile"
    declaration_pattern = r'###\s+([A-Z][a-zA-Z0-9]+)\s+(?:Entity|Model|Schema)'
    matches = re.findall(declaration_pattern, content)
    for entity in matches:
        if entity and len(entity) > 1 and entity.lower() not in SECTION_HEADERS:
            entities.add(entity)

    return entities


def check_entity_consistency(files_data: List[Tuple[str, str]]) -> Dict[str, Any]:
    """Check that entities mentioned in one file appear in others."""
    if len(files_data) < 2:
        return {
            'check': 'entity_consistency',
            'passed': True,
            'issues': [],
            'skipped': True,
            'reason': 'Entity consistency check requires 2+ files'
        }

    # Extract entities from each file
    file_entities = {}
    all_entities = set()

    for filepath, content in files_data:
        entities = extract_entities(content)
        file_entities[filepath] = entities
        all_entities.update(entities)

    # Check for entities missing from files
    issues = []
    for filepath, entities in file_entities.items():
        filename = os.path.basename(filepath)
        missing = all_entities - entities

        # Only report if significant entities are missing
        for entity in missing:
            # Skip common words that might be false positives
            if entity.lower() in ['id', 'type', 'status', 'date', 'time', 'name', 'api', 'json']:
                continue
            issues.append(f"Entity '{entity}' not found in {filename}")

    return {
        'check': 'entity_consistency',
        'passed': len(issues) == 0,
        'issues': issues
    }


def is_openapi_file(filepath: str) -> bool:
    """Check if file is an OpenAPI/contract file."""
    filename = os.path.basename(filepath).lower()
    dirname = os.path.dirname(filepath).lower()

    return (
        filename.endswith('.yaml') or
        filename.endswith('.yml') or
        'contract' in filename or
        'api' in filename or
        'contracts' in dirname or
        'openapi' in filename
    )


def validate_files(filepaths: List[str]) -> Dict[str, Any]:
    """Run all validations on provided files."""
    all_checks = []
    files_data = []
    validated_files = []

    for filepath in filepaths:
        if not os.path.exists(filepath):
            continue

        # Skip OpenAPI files (defer to validate-openapi.py)
        if is_openapi_file(filepath):
            all_checks.append({
                'check': f'openapi_validation:{os.path.basename(filepath)}',
                'passed': True,
                'issues': [],
                'skipped': True,
                'reason': 'OpenAPI files should be validated with validate-openapi.py'
            })
            validated_files.append(filepath)
            continue

        content, lines = read_file(filepath)
        if not content:
            all_checks.append({
                'check': f'file_read:{os.path.basename(filepath)}',
                'passed': False,
                'issues': [f'Could not read file: {filepath}']
            })
            continue

        validated_files.append(filepath)
        files_data.append((filepath, content))

        # Run file-specific checks
        all_checks.append(check_unresolved_markers(content, lines))
        all_checks.append(check_required_sections(filepath, content))
        all_checks.append(check_traceability(content))
        all_checks.append(check_pii_markers(filepath, content, lines))

    # Run cross-file checks
    if len(files_data) >= 2:
        all_checks.append(check_entity_consistency(files_data))

    # Calculate summary
    total = sum(1 for c in all_checks if not c.get('skipped', False))
    passed = sum(1 for c in all_checks if c['passed'] and not c.get('skipped', False))
    failed = total - passed

    return {
        'files': [os.path.basename(f) for f in validated_files],
        'checks': all_checks,
        'summary': {
            'total': total,
            'passed': passed,
            'failed': failed
        }
    }


def main():
    if len(sys.argv) < 2:
        print("Usage: check-artifacts.py <file1> [file2] ...", file=sys.stderr)
        print("", file=sys.stderr)
        print("Validates plan phase artifacts for common issues:", file=sys.stderr)
        print("  - Unresolved markers ([NEEDS CLARIFICATION], [TBD], etc.)", file=sys.stderr)
        print("  - Required sections based on file type", file=sys.stderr)
        print("  - Traceability references (FR-XXX, US-XXX)", file=sys.stderr)
        print("  - PII annotations for sensitive fields", file=sys.stderr)
        print("  - Entity consistency across files", file=sys.stderr)
        sys.exit(1)

    filepaths = sys.argv[1:]

    # Validate files exist
    valid_paths = []
    for path in filepaths:
        if os.path.exists(path):
            valid_paths.append(path)
        else:
            print(f"Warning: File not found: {path}", file=sys.stderr)

    if not valid_paths:
        print("Error: No valid files provided", file=sys.stderr)
        sys.exit(1)

    # Run validation
    results = validate_files(valid_paths)

    # Output JSON
    print(json.dumps(results, indent=2))

    # Exit with appropriate code
    sys.exit(0 if results['summary']['failed'] == 0 else 1)


if __name__ == '__main__':
    main()
