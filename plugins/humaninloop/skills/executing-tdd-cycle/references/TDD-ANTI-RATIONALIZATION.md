# TDD Anti-Rationalization

Common shortcuts engineers take when implementing TDD cycles, and why each one leads to failures. When you catch yourself thinking any of these, return to the execution sequence.

## Rationalization Table

| Rationalization | Why It's Wrong | What To Do Instead |
|----------------|---------------|-------------------|
| "The test already passes so I'll skip writing it first" | You haven't verified it fails — you might be testing nothing. A test that passes without implementation is either testing the wrong thing or asserting a tautology. | Write the test. Run it. If it passes, your assertion is wrong. Rewrite the assertion to actually test the requirement. |
| "I'll write all the code first and tests after" | Inverts TDD. Tests become retroactive justification — written to match the code, not to specify the behavior. Bugs hide because the test was shaped around the bug. | Write the failing test first. Every time. The test defines the requirement; the code satisfies it. |
| "This task is trivial, no test needed" | The task plan says test first — follow the plan. Trivial code has a way of becoming non-trivial when edge cases appear. The test catches regressions when future cycles modify related code. | Write the test. If it's truly trivial, the test is trivial too — fast to write, fast to run, permanent protection. |
| "I'll refactor this existing code while I'm here" | Scope creep. The refactoring introduces changes that the cycle report doesn't account for, the checkpoint doesn't verify, and future cycles don't expect. | Note the improvement opportunity in "Notes for Next Cycle" in the cycle report. Do not act on it. |
| "The task says EXTEND but I need to rewrite this" | Read existing code more carefully — extend means extend. The existing code has consumers you may not see. Rewriting breaks interfaces that other code depends on. | Follow existing patterns. Add new code alongside existing code. If existing code truly cannot support the extension, flag it in the cycle report. |

## Red Flags in Practice

### "I know this works"

If you're skipping a step because you "know" the result, you're not verifying — you're assuming. Assumptions are the source of production incidents.

### "The checkpoint will catch it"

The checkpoint evaluates structured data from your report and the qa-engineer's verification. It cannot catch problems you didn't report or tests you didn't write.

### "Just this once"

Every shortcut becomes a precedent. If you skip the red phase once, you'll skip it again when the next task "seems simple." Discipline is consistent.

### "I'll come back and add the test later"

You won't. The next task is waiting. The cycle report is due. "Later" is never.

### "This is obviously correct"

The tests exist to verify the obvious. When the obvious is wrong (and it sometimes is), the test catches it. When it's right, the test proves it.
