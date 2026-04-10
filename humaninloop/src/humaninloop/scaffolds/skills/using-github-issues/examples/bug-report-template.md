# Bug Report Template

Use this template when creating bug reports.

## Template

```markdown
## Description

[Clear, concise description of the bug]

## Steps to Reproduce

1. [First step]
2. [Second step]
3. [Third step]
4. [Continue as needed]

## Expected Behavior

[What SHOULD happen]

## Actual Behavior

[What DOES happen - include error messages verbatim]

## Environment

- **OS**: [e.g., macOS 14.2, Windows 11, Ubuntu 22.04]
- **Browser**: [e.g., Chrome 120, Safari 17, Firefox 121]
- **Version**: [Application/library version]
- **Configuration**: [Any relevant settings]

## Severity

- [ ] Critical - System unusable, data loss, security issue
- [ ] High - Major feature broken, no workaround
- [ ] Medium - Feature impaired, workaround exists
- [ ] Low - Minor issue, cosmetic

## Additional Context

[Screenshots, logs, related issues, workarounds discovered]
```

---

## Example: Complete Bug Report

```markdown
## Description

Dark mode toggle in settings does not persist after page refresh. Users must re-enable dark mode on every visit.

## Steps to Reproduce

1. Navigate to Settings > Appearance
2. Click the "Dark Mode" toggle to enable
3. Observe the UI switches to dark theme
4. Refresh the page (Cmd+R / F5)
5. Observe the UI reverts to light theme

## Expected Behavior

Dark mode preference should persist across page refreshes and browser sessions via localStorage or user preferences API.

## Actual Behavior

Dark mode visually activates but reverts to light mode on any page refresh. Console shows no errors. localStorage inspection shows `theme` key is not being set.

## Environment

- **OS**: macOS 14.2.1
- **Browser**: Chrome 120.0.6099.129
- **Version**: App v2.3.1
- **Configuration**: Default settings, logged in as standard user

## Severity

- [ ] Critical
- [x] High - Major feature broken, no workaround
- [ ] Medium
- [ ] Low

## Additional Context

- First noticed after deploying commit abc123
- Affects all browsers tested (Chrome, Safari, Firefox)
- Works correctly in incognito mode (suggests conflict with existing localStorage)
- Related: May be connected to #456 (localStorage migration)
```

---

## Example: Incomplete Bug Report (What NOT to Do)

```markdown
## Title: Dark mode doesn't work

Dark mode toggle broken. Please fix.
```

**Why this fails:**
- No steps to reproduce
- "Doesn't work" is ambiguous (toggle missing? doesn't activate? doesn't persist?)
- No environment information
- No severity assessment
- Developer cannot begin investigating without follow-up questions
