#!/usr/bin/env python3
"""
Validate user story format in specification files.

Checks:
- Priority markers (P1, P2, P3)
- Given/When/Then syntax completeness
- Independent test presence
- Priority justification
- Header format

Usage:
    python validate-user-stories.py <path-to-spec.md>

Output:
    JSON with validation results
"""

import json
import re
import sys
from pathlib import Path


def find_user_stories(content: str) -> list[dict]:
    """Extract user stories from markdown content."""
    stories = []

    # Pattern for user story headers
    header_pattern = re.compile(
        r'^###\s+User\s+Story\s+(\d+)\s*[-–—]\s*(.+?)\s*\(Priority:\s*(P[123])\)',
        re.MULTILINE | re.IGNORECASE
    )

    # Find all story headers and their positions
    matches = list(header_pattern.finditer(content))

    for i, match in enumerate(matches):
        start = match.start()
        # End at next story or end of content
        end = matches[i + 1].start() if i + 1 < len(matches) else len(content)

        story_content = content[start:end]
        stories.append({
            'number': int(match.group(1)),
            'title': match.group(2).strip(),
            'priority': match.group(3).upper(),
            'content': story_content,
            'line': content[:start].count('\n') + 1
        })

    return stories


def check_header_format(story: dict) -> dict:
    """Check if story header follows the correct format."""
    pattern = re.compile(
        r'^###\s+User\s+Story\s+\d+\s*[-–—]\s*.+\s*\(Priority:\s*P[123]\)',
        re.IGNORECASE
    )

    first_line = story['content'].split('\n')[0]
    passed = bool(pattern.match(first_line))

    return {
        'check': 'header_format',
        'passed': passed,
        'issues': [] if passed else [f"Story {story['number']}: Header format incorrect - '{first_line[:60]}...'"]
    }


def check_priority_marker(story: dict) -> dict:
    """Check if priority marker is valid (P1, P2, or P3)."""
    valid_priorities = {'P1', 'P2', 'P3'}
    passed = story['priority'] in valid_priorities

    return {
        'check': 'priority_markers',
        'passed': passed,
        'issues': [] if passed else [f"Story {story['number']}: Invalid priority '{story['priority']}'"]
    }


def check_priority_justification(story: dict) -> dict:
    """Check if priority justification is present and non-empty."""
    pattern = re.compile(r'\*\*Why this priority\*\*:\s*(.+?)(?=\n\n|\n\*\*|$)', re.DOTALL | re.IGNORECASE)
    match = pattern.search(story['content'])

    if not match:
        return {
            'check': 'priority_justifications',
            'passed': False,
            'issues': [f"Story {story['number']}: Missing '**Why this priority**:' section"]
        }

    justification = match.group(1).strip()
    if len(justification) < 20:
        return {
            'check': 'priority_justifications',
            'passed': False,
            'issues': [f"Story {story['number']}: Priority justification too brief ('{justification[:30]}...')"]
        }

    return {
        'check': 'priority_justifications',
        'passed': True,
        'issues': []
    }


def check_independent_test(story: dict) -> dict:
    """Check if independent test is specified."""
    pattern = re.compile(r'\*\*Independent Test\*\*:\s*(.+?)(?=\n\n|\n\*\*|$)', re.DOTALL | re.IGNORECASE)
    match = pattern.search(story['content'])

    if not match:
        return {
            'check': 'independent_tests',
            'passed': False,
            'issues': [f"Story {story['number']}: Missing '**Independent Test**:' section"]
        }

    test_desc = match.group(1).strip()
    if len(test_desc) < 20:
        return {
            'check': 'independent_tests',
            'passed': False,
            'issues': [f"Story {story['number']}: Independent test description too brief"]
        }

    return {
        'check': 'independent_tests',
        'passed': True,
        'issues': []
    }


def check_given_when_then(story: dict) -> dict:
    """Check if acceptance scenarios use Given/When/Then format."""
    issues = []

    # Find acceptance scenarios section
    scenarios_pattern = re.compile(
        r'\*\*Acceptance Scenarios?\*\*:?\s*(.*?)(?=\n###|\n##|\Z)',
        re.DOTALL | re.IGNORECASE
    )
    scenarios_match = scenarios_pattern.search(story['content'])

    if not scenarios_match:
        return {
            'check': 'given_when_then',
            'passed': False,
            'issues': [f"Story {story['number']}: Missing '**Acceptance Scenarios**:' section"]
        }

    scenarios_content = scenarios_match.group(1)

    # Find numbered scenarios
    scenario_pattern = re.compile(r'^\d+\.\s+(.+?)(?=^\d+\.|\Z)', re.MULTILINE | re.DOTALL)
    scenarios = scenario_pattern.findall(scenarios_content)

    if not scenarios:
        return {
            'check': 'given_when_then',
            'passed': False,
            'issues': [f"Story {story['number']}: No numbered scenarios found"]
        }

    for idx, scenario in enumerate(scenarios, 1):
        scenario_lower = scenario.lower()

        has_given = '**given**' in scenario_lower or 'given' in scenario_lower
        has_when = '**when**' in scenario_lower or 'when' in scenario_lower
        has_then = '**then**' in scenario_lower or 'then' in scenario_lower

        if not has_given:
            issues.append(f"Story {story['number']}, Scenario {idx}: Missing 'Given' clause")
        if not has_when:
            issues.append(f"Story {story['number']}, Scenario {idx}: Missing 'When' clause")
        if not has_then:
            issues.append(f"Story {story['number']}, Scenario {idx}: Missing 'Then' clause")

    return {
        'check': 'given_when_then',
        'passed': len(issues) == 0,
        'issues': issues
    }


def validate_file(file_path: str) -> dict:
    """Validate user stories in a file."""
    path = Path(file_path)

    if not path.exists():
        return {
            'file': file_path,
            'error': f"File not found: {file_path}",
            'stories_found': 0,
            'checks': [],
            'summary': {'total': 0, 'passed': 0, 'failed': 0}
        }

    content = path.read_text(encoding='utf-8')
    stories = find_user_stories(content)

    if not stories:
        return {
            'file': file_path,
            'stories_found': 0,
            'checks': [],
            'summary': {'total': 0, 'passed': 0, 'failed': 0},
            'message': 'No user stories found in file'
        }

    # Aggregate checks across all stories
    all_checks = {
        'header_format': {'check': 'header_format', 'passed': True, 'issues': []},
        'priority_markers': {'check': 'priority_markers', 'passed': True, 'issues': []},
        'priority_justifications': {'check': 'priority_justifications', 'passed': True, 'issues': []},
        'independent_tests': {'check': 'independent_tests', 'passed': True, 'issues': []},
        'given_when_then': {'check': 'given_when_then', 'passed': True, 'issues': []}
    }

    for story in stories:
        checks = [
            check_header_format(story),
            check_priority_marker(story),
            check_priority_justification(story),
            check_independent_test(story),
            check_given_when_then(story)
        ]

        for check in checks:
            check_name = check['check']
            if not check['passed']:
                all_checks[check_name]['passed'] = False
            all_checks[check_name]['issues'].extend(check['issues'])

    checks_list = list(all_checks.values())
    passed_count = sum(1 for c in checks_list if c['passed'])
    failed_count = len(checks_list) - passed_count

    return {
        'file': file_path,
        'stories_found': len(stories),
        'stories': [
            {'number': s['number'], 'title': s['title'], 'priority': s['priority'], 'line': s['line']}
            for s in stories
        ],
        'checks': checks_list,
        'summary': {
            'total': len(checks_list),
            'passed': passed_count,
            'failed': failed_count
        }
    }


def main():
    if len(sys.argv) < 2:
        print(json.dumps({
            'error': 'Usage: python validate-user-stories.py <path-to-spec.md>'
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
