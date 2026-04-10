#!/usr/bin/env python3
"""
Validation script for data-model.md files.

Validates domain entity definitions for completeness and consistency
according to the patterns-entity-modeling skill requirements.

Usage:
    python validate-model.py <path-to-data-model.md>

Exit codes:
    0 - All checks passed
    1 - One or more checks failed
"""

import json
import re
import sys
from pathlib import Path


def read_file(filepath: str) -> str:
    """Read and return file contents."""
    path = Path(filepath)
    if not path.exists():
        print(f"Error: File not found: {filepath}", file=sys.stderr)
        sys.exit(1)
    return path.read_text(encoding="utf-8")


def extract_entities(content: str) -> list[dict]:
    """
    Extract entities from data-model.md content.

    Looks for patterns like:
    - ## Entity: EntityName
    - ## Entity: EntityName [NEW]
    - ## Entity: EntityName [EXTENDS EXISTING]
    - ### EntityName (simpler format)
    """
    entities = []

    # Pattern for ## Entity: Name [STATUS] format
    entity_pattern = r"^##\s+Entity:\s+(\w+)(?:\s+\[([^\]]+)\])?"

    # Also check for simpler ### EntityName patterns within entity sections
    simple_entity_pattern = r"^###\s+(\w+)\s*$"

    lines = content.split("\n")
    current_entity = None
    current_section = None
    entity_content = []

    for i, line in enumerate(lines):
        # Check for entity header
        match = re.match(entity_pattern, line, re.MULTILINE)
        if match:
            # Save previous entity if exists
            if current_entity:
                entities.append({
                    "name": current_entity,
                    "status": current_status,
                    "content": "\n".join(entity_content),
                    "line_number": current_line
                })

            current_entity = match.group(1)
            current_status = match.group(2) or "NEW"
            current_line = i + 1
            entity_content = []
            continue

        # Check if we've hit the next major section (## that's not Entity:)
        if re.match(r"^##\s+(?!Entity:)", line) and current_entity:
            entities.append({
                "name": current_entity,
                "status": current_status,
                "content": "\n".join(entity_content),
                "line_number": current_line
            })
            current_entity = None
            entity_content = []
            continue

        # Collect content for current entity
        if current_entity:
            entity_content.append(line)

    # Don't forget the last entity
    if current_entity:
        entities.append({
            "name": current_entity,
            "status": current_status,
            "content": "\n".join(entity_content),
            "line_number": current_line
        })

    # If no entities found with ## Entity: format, try summary table
    if not entities:
        entities = extract_entities_from_summary(content)

    return entities


def extract_entities_from_summary(content: str) -> list[dict]:
    """Extract entity names from summary table if present."""
    entities = []

    # Look for summary table pattern
    # | Entity | Attributes | Relationships | Status |
    summary_pattern = r"\|\s*(\w+)\s*\|[^|]*\|[^|]*\|\s*\[?(\w+[^\]]*)\]?\s*\|"

    in_summary = False
    for line in content.split("\n"):
        if "| Entity |" in line or "| Entity|" in line:
            in_summary = True
            continue
        if in_summary and line.strip().startswith("|"):
            match = re.match(summary_pattern, line.strip())
            if match and match.group(1) not in ["Entity", "---", ""]:
                entities.append({
                    "name": match.group(1),
                    "status": match.group(2).strip("[]"),
                    "content": "",
                    "line_number": 0
                })
        elif in_summary and not line.strip().startswith("|"):
            in_summary = False

    return entities


def check_entity_format(entities: list[dict], content: str) -> dict:
    """Check that entities follow the expected format."""
    issues = []

    if not entities:
        issues.append("No entities found in document. Expected '## Entity: Name' format.")

    for entity in entities:
        if not entity["name"]:
            issues.append("Found entity section without a name")
        elif not entity["name"][0].isupper():
            issues.append(f"{entity['name']}: Entity name should be PascalCase")

    return {
        "check": "entity_format",
        "passed": len(issues) == 0,
        "issues": issues
    }


def check_required_attributes(entities: list[dict]) -> dict:
    """Check that entities have attributes defined."""
    issues = []

    # Pattern to find attribute tables
    attr_table_pattern = r"\|\s*Attribute\s*\|.*\|"
    attr_row_pattern = r"\|\s*(\w+)\s*\|"

    for entity in entities:
        content = entity["content"]

        # Skip check for [REUSES EXISTING] entities
        if entity.get("status") == "REUSES EXISTING":
            continue

        # Look for attributes section or table
        has_attributes = bool(re.search(attr_table_pattern, content, re.IGNORECASE))
        has_attributes = has_attributes or "### Attributes" in content
        has_attributes = has_attributes or "### Standard Fields" in content

        if not has_attributes:
            issues.append(f"{entity['name']}: No attributes table found")
        else:
            # Count attribute rows (excluding header and separator)
            attr_rows = re.findall(r"\|\s*\w+\s*\|[^|]+\|", content)
            # Filter out header rows
            data_rows = [r for r in attr_rows if "Attribute" not in r and "---" not in r]
            if len(data_rows) == 0:
                issues.append(f"{entity['name']}: Attributes table appears empty")

    return {
        "check": "required_attributes",
        "passed": len(issues) == 0,
        "issues": issues
    }


def check_relationships(entities: list[dict], content: str) -> dict:
    """Check that relationships are documented."""
    issues = []

    # Relationship keywords to look for
    relationship_keywords = [
        r"belongs\s+to",
        r"has\s+many",
        r"has\s+one",
        r"references",
        r"Reference\(",
        r"N:1",
        r"1:N",
        r"N:M",
        r"1:1",
        r"One-to-Many",
        r"Many-to-One",
        r"Many-to-Many",
        r"One-to-One",
        r"Foreign\s*Key",
        r"→",
        r"←",
        r"↔",
    ]

    # Check if there's a relationships section globally
    has_global_relationships = bool(re.search(r"^##\s+Relationships", content, re.MULTILINE))

    for entity in entities:
        entity_content = entity["content"]

        # Skip check for [REUSES EXISTING] entities
        if entity.get("status") == "REUSES EXISTING":
            continue

        # Look for relationship indicators in entity section
        has_relationships = False
        for keyword in relationship_keywords:
            if re.search(keyword, entity_content, re.IGNORECASE):
                has_relationships = True
                break

        # Also check for ### Relationships subsection
        if "### Relationships" in entity_content:
            has_relationships = True

        if not has_relationships and not has_global_relationships:
            issues.append(f"{entity['name']}: No relationships defined")

    return {
        "check": "relationships",
        "passed": len(issues) == 0,
        "issues": issues
    }


def check_state_machines(entities: list[dict], content: str) -> dict:
    """Check that entities with state/status fields have state machine documentation."""
    issues = []

    # Pattern to identify status/state fields
    state_field_pattern = r"\|\s*(status|state)\s*\|.*Enum\[([^\]]+)\]"

    # Check for global state machine section
    has_state_section = bool(re.search(r"##\s+State\s+Machine", content, re.IGNORECASE))

    for entity in entities:
        entity_content = entity["content"]

        # Look for state/status fields
        state_match = re.search(state_field_pattern, entity_content, re.IGNORECASE)
        if state_match:
            # Entity has a state field, check for state machine docs
            state_field = state_match.group(1)
            states = state_match.group(2)

            # Look for transitions documentation
            has_transitions = any([
                re.search(r"###?\s+Transitions", entity_content, re.IGNORECASE),
                re.search(r"###?\s+States", entity_content, re.IGNORECASE),
                re.search(r"\|\s*From\s*\|\s*To\s*\|", entity_content),
                has_state_section
            ])

            if not has_transitions:
                issues.append(
                    f"{entity['name']}.{state_field}: Has state field with values [{states}] but no state transitions documented"
                )

    return {
        "check": "state_machines",
        "passed": len(issues) == 0,
        "issues": issues
    }


def check_validation_rules(entities: list[dict]) -> dict:
    """Check that validation constraints are documented."""
    issues = []

    # Validation keywords
    validation_patterns = [
        r"required",
        r"unique",
        r"min",
        r"max",
        r"format",
        r"Enum\[",
        r"Text\(\d+\)",
        r"Decimal\(\d+",
        r"Yes\s*\|",  # Required column with Yes
        r"No\s*\|",   # Required column with No
    ]

    for entity in entities:
        entity_content = entity["content"]

        # Skip check for [REUSES EXISTING] entities
        if entity.get("status") == "REUSES EXISTING":
            continue

        # Look for validation indicators
        has_validation = False
        for pattern in validation_patterns:
            if re.search(pattern, entity_content, re.IGNORECASE):
                has_validation = True
                break

        # Check for Required column in attribute table
        if "| Required |" in entity_content or "|Required|" in entity_content:
            has_validation = True

        if not has_validation and entity_content.strip():
            issues.append(f"{entity['name']}: No validation constraints documented")

    return {
        "check": "validation_rules",
        "passed": len(issues) == 0,
        "issues": issues
    }


def check_audit_fields(entities: list[dict]) -> dict:
    """Check that entities have audit timestamp fields."""
    issues = []

    # Common audit field names
    audit_fields = [
        "createdat", "created_at", "creationtime", "created",
        "updatedat", "updated_at", "modifiedat", "modified_at", "lastupdated",
    ]

    for entity in entities:
        entity_content = entity["content"].lower()

        # Skip check for [REUSES EXISTING] or [EXTENDS EXISTING] entities
        if entity.get("status") in ["REUSES EXISTING", "EXTENDS EXISTING"]:
            continue

        # Check for at least one audit field
        has_audit = False
        for field in audit_fields:
            if field in entity_content:
                has_audit = True
                break

        # Also check for Timestamp type which often indicates audit fields
        if "timestamp" in entity_content and ("created" in entity_content or "updated" in entity_content):
            has_audit = True

        if not has_audit and entity_content.strip():
            issues.append(f"{entity['name']}: Missing audit fields (createdAt/updatedAt)")

    return {
        "check": "audit_fields",
        "passed": len(issues) == 0,
        "issues": issues
    }


def check_id_fields(entities: list[dict]) -> dict:
    """Check that entities have an identifier field."""
    issues = []

    # ID field patterns
    id_patterns = [
        r"\|\s*id\s*\|",
        r"\|\s*\w+Id\s*\|",
        r"\|\s*\w+_id\s*\|",
        r"Identifier",
        r"UUID",
        r"Primary\s*key",
    ]

    for entity in entities:
        entity_content = entity["content"]

        # Skip check for [REUSES EXISTING] or [EXTENDS EXISTING] entities
        if entity.get("status") in ["REUSES EXISTING", "EXTENDS EXISTING"]:
            continue

        # Look for ID field
        has_id = False
        for pattern in id_patterns:
            if re.search(pattern, entity_content, re.IGNORECASE):
                has_id = True
                break

        if not has_id and entity_content.strip():
            issues.append(f"{entity['name']}: Missing identifier field (id)")

    return {
        "check": "id_fields",
        "passed": len(issues) == 0,
        "issues": issues
    }


def validate_data_model(filepath: str) -> dict:
    """Run all validation checks on a data-model.md file."""
    content = read_file(filepath)
    entities = extract_entities(content)

    entity_names = [e["name"] for e in entities]

    checks = [
        check_entity_format(entities, content),
        check_required_attributes(entities),
        check_relationships(entities, content),
        check_state_machines(entities, content),
        check_validation_rules(entities),
        check_audit_fields(entities),
        check_id_fields(entities),
    ]

    passed_count = sum(1 for c in checks if c["passed"])
    failed_count = len(checks) - passed_count

    return {
        "file": Path(filepath).name,
        "entities_found": entity_names,
        "checks": checks,
        "summary": {
            "total": len(checks),
            "passed": passed_count,
            "failed": failed_count
        }
    }


def main():
    if len(sys.argv) != 2:
        print("Usage: python validate-model.py <path-to-data-model.md>", file=sys.stderr)
        sys.exit(1)

    filepath = sys.argv[1]
    result = validate_data_model(filepath)

    # Output JSON result
    print(json.dumps(result, indent=2))

    # Exit with appropriate code
    if result["summary"]["failed"] > 0:
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
