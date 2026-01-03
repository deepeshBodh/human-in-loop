#!/usr/bin/env python3
"""
Validate OpenAPI 3.x specifications for syntax, REST conventions, and completeness.

Checks:
- Valid OpenAPI 3.x syntax (YAML/JSON)
- REST naming conventions (plural nouns, kebab-case)
- Error responses defined for endpoints
- Security schemes documented
- Examples provided in schemas

Usage:
    python validate-openapi.py <path-to-openapi.yaml>

Output:
    JSON with validation results
"""

import json
import re
import sys
from pathlib import Path

# Try to import yaml, fall back to json-only mode
try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False


# Common singular nouns that should be plural in REST paths
SINGULAR_NOUNS = [
    'user', 'task', 'project', 'item', 'product', 'order', 'comment',
    'post', 'article', 'category', 'tag', 'file', 'image', 'document',
    'message', 'notification', 'setting', 'preference', 'session',
    'token', 'role', 'permission', 'team', 'organization', 'workspace',
    'invoice', 'payment', 'subscription', 'plan', 'feature', 'report',
    'event', 'log', 'audit', 'webhook', 'integration', 'connection'
]

# HTTP methods that typically need error responses
METHODS_NEEDING_ERRORS = ['post', 'put', 'patch', 'delete']

# Standard error status codes to check for
EXPECTED_ERROR_CODES = ['400', '401', '403', '404', '500']


def load_spec(file_path: str) -> dict:
    """Load OpenAPI spec from YAML or JSON file."""
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    content = path.read_text(encoding='utf-8')

    # Detect file type
    is_yaml_file = path.suffix in ['.yaml', '.yml']
    is_json_content = content.strip().startswith('{')

    # Try YAML first (if available and appropriate)
    if HAS_YAML and (is_yaml_file or not is_json_content):
        try:
            return yaml.safe_load(content)
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML: {e}")

    # YAML file but no PyYAML
    if is_yaml_file and not HAS_YAML:
        raise ValueError(
            "YAML file detected but PyYAML not installed. "
            "Install with: pip install pyyaml"
        )

    # Try JSON
    try:
        return json.loads(content)
    except json.JSONDecodeError as e:
        if not is_json_content and not HAS_YAML:
            raise ValueError(
                f"File appears to be YAML but PyYAML not installed. "
                f"Install with: pip install pyyaml"
            )
        raise ValueError(f"Invalid JSON: {e}")


def check_openapi_version(spec: dict) -> dict:
    """Check for valid OpenAPI version."""
    issues = []
    version = spec.get('openapi', '')

    if not version:
        issues.append("Missing 'openapi' version field")
    elif not version.startswith('3.'):
        issues.append(f"Expected OpenAPI 3.x, found: {version}")

    return {
        'check': 'openapi_version',
        'passed': len(issues) == 0,
        'issues': issues,
        'version': version if version else None
    }


def check_info_section(spec: dict) -> dict:
    """Check for required info section."""
    issues = []
    info = spec.get('info', {})

    if not info:
        issues.append("Missing 'info' section")
    else:
        if not info.get('title'):
            issues.append("Missing 'info.title'")
        if not info.get('version'):
            issues.append("Missing 'info.version'")

    return {
        'check': 'info_section',
        'passed': len(issues) == 0,
        'issues': issues
    }


def check_plural_nouns(spec: dict) -> dict:
    """Check that path segments use plural nouns."""
    issues = []
    paths = spec.get('paths', {})

    for path in paths.keys():
        # Extract path segments (ignore path parameters like {id})
        segments = [s for s in path.split('/') if s and not s.startswith('{')]

        for segment in segments:
            # Check if segment is a singular noun
            segment_lower = segment.lower().replace('-', '').replace('_', '')

            for singular in SINGULAR_NOUNS:
                # Check for exact singular match (not already plural)
                if segment_lower == singular and not segment_lower.endswith('s'):
                    issues.append(f"'{path}': Use plural '{singular}s' instead of '{segment}'")
                    break

    return {
        'check': 'plural_nouns',
        'passed': len(issues) == 0,
        'issues': issues
    }


def check_kebab_case(spec: dict) -> dict:
    """Check that path segments use kebab-case (not camelCase or snake_case)."""
    issues = []
    paths = spec.get('paths', {})

    for path in paths.keys():
        segments = [s for s in path.split('/') if s and not s.startswith('{')]

        for segment in segments:
            # Check for camelCase (lowercase followed by uppercase)
            if re.search(r'[a-z][A-Z]', segment):
                kebab = re.sub(r'([a-z])([A-Z])', r'\1-\2', segment).lower()
                issues.append(f"'{path}': Use kebab-case '{kebab}' instead of '{segment}'")

            # Check for snake_case
            elif '_' in segment:
                kebab = segment.replace('_', '-').lower()
                issues.append(f"'{path}': Use kebab-case '{kebab}' instead of '{segment}'")

    return {
        'check': 'kebab_case',
        'passed': len(issues) == 0,
        'issues': issues
    }


def check_error_responses(spec: dict) -> dict:
    """Check that endpoints have error responses defined."""
    issues = []
    paths = spec.get('paths', {})

    for path, methods in paths.items():
        if not isinstance(methods, dict):
            continue

        for method, operation in methods.items():
            if method.lower() not in ['get', 'post', 'put', 'patch', 'delete']:
                continue

            if not isinstance(operation, dict):
                continue

            responses = operation.get('responses', {})

            # Check for at least one error response (4xx or 5xx)
            has_error_response = any(
                str(code).startswith('4') or str(code).startswith('5')
                for code in responses.keys()
                if code != 'default'
            )

            if not has_error_response and method.lower() in METHODS_NEEDING_ERRORS:
                issues.append(f"{method.upper()} {path}: Missing error responses (4xx/5xx)")

            # Check for 401 on authenticated endpoints
            security = operation.get('security', spec.get('security', []))
            if security and '401' not in responses and 'default' not in responses:
                issues.append(f"{method.upper()} {path}: Has security but missing 401 response")

    return {
        'check': 'error_responses',
        'passed': len(issues) == 0,
        'issues': issues
    }


def check_request_bodies(spec: dict) -> dict:
    """Check that POST/PUT/PATCH have request bodies defined."""
    issues = []
    paths = spec.get('paths', {})

    for path, methods in paths.items():
        if not isinstance(methods, dict):
            continue

        for method, operation in methods.items():
            if method.lower() not in ['post', 'put', 'patch']:
                continue

            if not isinstance(operation, dict):
                continue

            # Skip if it's an action endpoint (like /users/{id}/activate)
            if path.split('/')[-1].startswith('{'):
                continue

            request_body = operation.get('requestBody')

            if not request_body:
                # Check if it's a simple action (no path params at end suggests it needs a body)
                last_segment = path.rstrip('/').split('/')[-1]
                if not last_segment.startswith('{'):
                    issues.append(f"{method.upper()} {path}: Missing requestBody")

    return {
        'check': 'request_bodies',
        'passed': len(issues) == 0,
        'issues': issues
    }


def check_operation_ids(spec: dict) -> dict:
    """Check that operations have operationId defined."""
    issues = []
    paths = spec.get('paths', {})
    operation_ids = set()

    for path, methods in paths.items():
        if not isinstance(methods, dict):
            continue

        for method, operation in methods.items():
            if method.lower() not in ['get', 'post', 'put', 'patch', 'delete']:
                continue

            if not isinstance(operation, dict):
                continue

            op_id = operation.get('operationId')

            if not op_id:
                issues.append(f"{method.upper()} {path}: Missing operationId")
            elif op_id in operation_ids:
                issues.append(f"{method.upper()} {path}: Duplicate operationId '{op_id}'")
            else:
                operation_ids.add(op_id)

    return {
        'check': 'operation_ids',
        'passed': len(issues) == 0,
        'issues': issues
    }


def check_security_schemes(spec: dict) -> dict:
    """Check for security scheme definitions if security is used."""
    issues = []

    # Check if any operation uses security
    has_security = bool(spec.get('security'))

    paths = spec.get('paths', {})
    for methods in paths.values():
        if isinstance(methods, dict):
            for operation in methods.values():
                if isinstance(operation, dict) and operation.get('security'):
                    has_security = True
                    break

    if has_security:
        components = spec.get('components', {})
        security_schemes = components.get('securitySchemes', {})

        if not security_schemes:
            issues.append("Security is used but no securitySchemes defined in components")

    return {
        'check': 'security_schemes',
        'passed': len(issues) == 0,
        'issues': issues
    }


def check_schema_examples(spec: dict) -> dict:
    """Check that schemas have examples."""
    issues = []

    components = spec.get('components', {})
    schemas = components.get('schemas', {})

    schemas_without_examples = []

    for name, schema in schemas.items():
        if not isinstance(schema, dict):
            continue

        # Check for example at schema level or in properties
        has_example = 'example' in schema or 'examples' in schema

        if not has_example and schema.get('properties'):
            # Check if any property has an example
            has_example = any(
                'example' in prop
                for prop in schema['properties'].values()
                if isinstance(prop, dict)
            )

        if not has_example:
            schemas_without_examples.append(name)

    if schemas_without_examples:
        issues.append(f"Schemas missing examples: {', '.join(schemas_without_examples[:5])}")
        if len(schemas_without_examples) > 5:
            issues[-1] += f" (+{len(schemas_without_examples) - 5} more)"

    return {
        'check': 'schema_examples',
        'passed': len(issues) == 0,
        'issues': issues
    }


def check_descriptions(spec: dict) -> dict:
    """Check that operations have descriptions or summaries."""
    issues = []
    paths = spec.get('paths', {})

    for path, methods in paths.items():
        if not isinstance(methods, dict):
            continue

        for method, operation in methods.items():
            if method.lower() not in ['get', 'post', 'put', 'patch', 'delete']:
                continue

            if not isinstance(operation, dict):
                continue

            has_desc = operation.get('summary') or operation.get('description')

            if not has_desc:
                issues.append(f"{method.upper()} {path}: Missing summary/description")

    return {
        'check': 'descriptions',
        'passed': len(issues) == 0,
        'issues': issues
    }


def validate_file(file_path: str) -> dict:
    """Validate an OpenAPI spec file."""
    try:
        spec = load_spec(file_path)
    except FileNotFoundError as e:
        return {
            'file': file_path,
            'valid_openapi': False,
            'error': str(e),
            'checks': [],
            'summary': {'total': 0, 'passed': 0, 'failed': 0}
        }
    except ValueError as e:
        return {
            'file': file_path,
            'valid_openapi': False,
            'error': str(e),
            'checks': [],
            'summary': {'total': 0, 'passed': 0, 'failed': 0}
        }

    checks = []

    # Run all checks
    version_check = check_openapi_version(spec)
    checks.append(version_check)
    checks.append(check_info_section(spec))
    checks.append(check_plural_nouns(spec))
    checks.append(check_kebab_case(spec))
    checks.append(check_error_responses(spec))
    checks.append(check_request_bodies(spec))
    checks.append(check_operation_ids(spec))
    checks.append(check_security_schemes(spec))
    checks.append(check_schema_examples(spec))
    checks.append(check_descriptions(spec))

    passed_count = sum(1 for c in checks if c['passed'])
    failed_count = len(checks) - passed_count

    return {
        'file': file_path,
        'valid_openapi': version_check['passed'],
        'openapi_version': version_check.get('version'),
        'paths_count': len(spec.get('paths', {})),
        'schemas_count': len(spec.get('components', {}).get('schemas', {})),
        'checks': checks,
        'summary': {
            'total': len(checks),
            'passed': passed_count,
            'failed': failed_count
        }
    }


def main():
    if len(sys.argv) < 2:
        print(json.dumps({
            'error': 'Usage: python validate-openapi.py <path-to-openapi.yaml>'
        }, indent=2))
        sys.exit(1)

    file_path = sys.argv[1]
    result = validate_file(file_path)
    print(json.dumps(result, indent=2))

    # Exit with error code if validation failed
    if result.get('error') or result['summary']['failed'] > 0:
        sys.exit(1)
    sys.exit(0)


if __name__ == '__main__':
    main()
