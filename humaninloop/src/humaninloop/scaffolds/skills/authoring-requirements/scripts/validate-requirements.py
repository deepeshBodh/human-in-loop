#!/usr/bin/env python3
"""
Validate functional requirements and success criteria format in specification files.

Checks:
- FR-XXX format and sequential numbering
- RFC 2119 keywords present (MUST, SHOULD, MAY)
- SC-XXX format and sequential numbering
- Technology-agnostic language (no banned terms)

Usage:
    python validate-requirements.py <path-to-spec.md>

Output:
    JSON with validation results
"""

import json
import re
import sys
from pathlib import Path


# Terms that indicate technology/implementation leakage
BANNED_TERMS = [
    # Databases
    'postgresql', 'postgres', 'mysql', 'mongodb', 'redis', 'sqlite',
    'dynamodb', 'cassandra', 'elasticsearch',
    # Frameworks
    'react', 'vue', 'angular', 'django', 'flask', 'express', 'rails',
    'spring', 'laravel', 'nextjs', 'next.js',
    # Languages (as implementation detail)
    'python', 'javascript', 'typescript', 'java', 'golang', 'rust',
    # Infrastructure
    'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'k8s', 'lambda',
    'ec2', 's3', 'cloudfront', 'heroku', 'vercel',
    # Technical metrics
    'api response', 'latency', 'throughput', 'cpu', 'memory usage',
    'query time', 'database query', 'http status',
    # Implementation patterns
    'endpoint', 'rest api', 'graphql', 'webhook', 'microservice',
    'cron job', 'queue', 'worker', 'cache layer',
    # Code-level
    'function', 'class', 'method', 'module', 'component', 'hook',
    'middleware', 'controller', 'service layer', 'repository pattern'
]

# RFC 2119 keywords
RFC_KEYWORDS = ['must', 'must not', 'shall', 'shall not', 'should',
                'should not', 'required', 'recommended', 'may', 'optional']


def find_requirements(content: str, prefix: str) -> list[dict]:
    """Extract requirements with given prefix (FR or SC) from content."""
    requirements = []

    # Pattern for requirements like **FR-001**: or **SC-001**:
    pattern = re.compile(
        rf'\*\*({prefix}-(\d{{3}}))[\*:]+\s*(.+?)(?=\n\*\*{prefix}-|\n##|\n\n##|\Z)',
        re.DOTALL | re.IGNORECASE
    )

    for match in pattern.finditer(content):
        req_id = match.group(1).upper()
        req_num = int(match.group(2))
        req_text = match.group(3).strip()

        requirements.append({
            'id': req_id,
            'number': req_num,
            'text': req_text,
            'line': content[:match.start()].count('\n') + 1
        })

    return requirements


def check_format(requirements: list[dict], prefix: str) -> dict:
    """Check if requirements follow the correct format."""
    issues = []

    for req in requirements:
        # Check format is correct (already matched by regex, so mostly valid)
        if not re.match(rf'^{prefix}-\d{{3}}$', req['id'], re.IGNORECASE):
            issues.append(f"{req['id']}: Invalid format (expected {prefix}-XXX)")

    return {
        'check': f'{prefix.lower()}_format',
        'passed': len(issues) == 0,
        'issues': issues
    }


def check_sequence(requirements: list[dict], prefix: str) -> dict:
    """Check if requirement numbers are sequential."""
    issues = []

    if not requirements:
        return {
            'check': f'{prefix.lower()}_sequence',
            'passed': True,
            'issues': []
        }

    numbers = sorted([r['number'] for r in requirements])

    # Check starts at 1
    if numbers[0] != 1:
        issues.append(f"{prefix} numbering should start at 001, found {prefix}-{numbers[0]:03d}")

    # Check for gaps
    for i, num in enumerate(numbers):
        expected = i + 1
        if num != expected:
            issues.append(f"Gap in {prefix} sequence: expected {prefix}-{expected:03d}, found {prefix}-{num:03d}")
            break

    # Check for duplicates
    seen = set()
    for num in numbers:
        if num in seen:
            issues.append(f"Duplicate {prefix}-{num:03d}")
        seen.add(num)

    return {
        'check': f'{prefix.lower()}_sequence',
        'passed': len(issues) == 0,
        'issues': issues
    }


def check_rfc_keywords(requirements: list[dict]) -> dict:
    """Check if functional requirements contain RFC 2119 keywords."""
    issues = []

    for req in requirements:
        text_lower = req['text'].lower()
        has_keyword = any(kw in text_lower for kw in RFC_KEYWORDS)

        if not has_keyword:
            issues.append(f"{req['id']}: Missing RFC 2119 keyword (MUST, SHOULD, MAY, etc.)")

    return {
        'check': 'rfc_keywords',
        'passed': len(issues) == 0,
        'issues': issues
    }


def check_tech_agnostic(requirements: list[dict], prefix: str) -> dict:
    """Check if requirements are technology-agnostic."""
    issues = []

    for req in requirements:
        text_lower = req['text'].lower()

        for term in BANNED_TERMS:
            if term.lower() in text_lower:
                issues.append(f"{req['id']}: Contains technology term '{term}'")
                break  # Only report first violation per requirement

    return {
        'check': 'tech_agnostic',
        'passed': len(issues) == 0,
        'issues': issues
    }


def check_outcome_focus(success_criteria: list[dict]) -> dict:
    """Check if success criteria focus on user/business outcomes."""
    issues = []

    # Patterns that suggest technical metrics instead of outcomes
    technical_patterns = [
        r'\d+\s*ms\b',  # milliseconds
        r'\d+%\s*(cpu|memory|coverage)',  # technical percentages
        r'uptime',
        r'error rate.*\d',  # numeric error rates (vs "decreased errors")
        r'requests?\s*per\s*second',
        r'concurrent\s*(users?|connections?)\s*>\s*\d',
    ]

    for sc in success_criteria:
        text_lower = sc['text'].lower()

        for pattern in technical_patterns:
            if re.search(pattern, text_lower):
                issues.append(f"{sc['id']}: May contain technical metric instead of user outcome")
                break

    return {
        'check': 'outcome_focus',
        'passed': len(issues) == 0,
        'issues': issues
    }


def validate_file(file_path: str) -> dict:
    """Validate requirements in a file."""
    path = Path(file_path)

    if not path.exists():
        return {
            'file': file_path,
            'error': f"File not found: {file_path}",
            'requirements_found': 0,
            'success_criteria_found': 0,
            'checks': [],
            'summary': {'total': 0, 'passed': 0, 'failed': 0}
        }

    content = path.read_text(encoding='utf-8')

    # Find requirements
    fr_requirements = find_requirements(content, 'FR')
    sc_requirements = find_requirements(content, 'SC')

    checks = []

    # FR checks
    if fr_requirements:
        checks.append(check_format(fr_requirements, 'FR'))
        checks.append(check_sequence(fr_requirements, 'FR'))
        checks.append(check_rfc_keywords(fr_requirements))
        checks.append(check_tech_agnostic(fr_requirements, 'FR'))
    else:
        checks.append({
            'check': 'fr_format',
            'passed': True,
            'issues': [],
            'message': 'No functional requirements found'
        })

    # SC checks
    if sc_requirements:
        checks.append(check_format(sc_requirements, 'SC'))
        checks.append(check_sequence(sc_requirements, 'SC'))
        checks.append(check_tech_agnostic(sc_requirements, 'SC'))
        checks.append(check_outcome_focus(sc_requirements))
    else:
        checks.append({
            'check': 'sc_format',
            'passed': True,
            'issues': [],
            'message': 'No success criteria found'
        })

    passed_count = sum(1 for c in checks if c['passed'])
    failed_count = len(checks) - passed_count

    return {
        'file': file_path,
        'requirements_found': len(fr_requirements),
        'success_criteria_found': len(sc_requirements),
        'requirements': [
            {'id': r['id'], 'line': r['line']}
            for r in fr_requirements
        ],
        'success_criteria': [
            {'id': r['id'], 'line': r['line']}
            for r in sc_requirements
        ],
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
            'error': 'Usage: python validate-requirements.py <path-to-spec.md>'
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
