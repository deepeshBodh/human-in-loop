---
name: patterns-flow-mapping
description: This skill MUST be invoked when the user says "map the flow", "connect these screens", "build user journey", "navigation mapping", "interaction flow", or "flow diagram". SHOULD also invoke when user mentions "screen transitions", "user flow", "navigation architecture", "entry points", "dead ends", or "orphaned screens". Provides structured procedure for connecting analyzed screenshots into coherent interaction flows with navigation logic and journey definitions.
---

# Flow Mapping

## Overview

Connect multiple analyzed screenshots into coherent interaction flows by systematically inventorying screens, mapping navigation elements, identifying transitions, and assembling user journeys. Every screen must have defined entry and exit points, every gap must be explicitly noted, and every flow must be organized around user goals.

## When to Use

- Multiple screenshots of an app or site have been analyzed and need connecting into flows
- Building a navigation architecture from visual references
- Identifying how users move between screens in an existing product
- Documenting user journeys from screenshot evidence
- Auditing an existing flow for dead ends, orphaned screens, or missing states
- Preparing interaction specifications for implementation

## When NOT to Use

- Only a single screenshot is available (use `humaninloop:analysis-screenshot` instead)
- Designing flows from scratch without reference screenshots
- Working from wireframes or Figma prototypes where flows are already documented
- The task is purely visual design without navigation concerns

## Prerequisites

Each screenshot entering the flow mapping process should already have a completed analysis from `humaninloop:analysis-screenshot`. If screenshots have not been analyzed, complete that step first.

**REQUIRED:** Run `humaninloop:analysis-screenshot` on each screenshot before beginning flow mapping.

## Step 1: Screen Inventory

Catalog every available screenshot before mapping any connections.

### Process

1. **List every screenshot** -- Assign each a short identifier (e.g., `S01-home`, `S02-profile`, `S03-settings`).
2. **Classify each screen** -- Determine what state or view it represents.
3. **Identify screen type** -- Categorize by function.
4. **Note platform** -- Confirm the navigation paradigm (mobile, web, desktop).

### Screen Type Classification

| Type | Description | Examples |
|------|-------------|---------|
| Landing | Entry point, first impression | Splash, onboarding, login |
| Hub | Navigation center, many exit points | Home, dashboard, main tab |
| Task | Focused on completing an action | Checkout, compose, form |
| Detail | Displays information about an entity | Profile, product page, article |
| Utility | Settings, preferences, auxiliary | Settings, help, about |
| Overlay | Appears above another screen | Modal, bottom sheet, dialog |
| Transitional | Brief state between actions | Loading, success confirmation |

### Output Format

```
SCREEN INVENTORY:
  Total screenshots: [N]
  Platform: [mobile-ios / mobile-android / web-desktop / web-responsive / desktop-app]
  Navigation paradigm: [tab-bar / sidebar / hamburger / breadcrumb / URL-based / mixed]

  ID          | Type         | Screen Name           | Key Content
  ------------|--------------|----------------------|------------------
  S01-home    | Hub          | Home Feed             | Feed, nav bar, FAB
  S02-profile | Detail       | User Profile          | Avatar, stats, posts
  S03-login   | Landing      | Login                 | Email, password, social
  ...

IDENTIFIED GAPS:
  - No screenshot for [expected screen, e.g., "registration flow"]
  - Missing [state type, e.g., "empty state for home feed"]
  - No screenshot showing [transition, e.g., "search results"]
```

Always document gaps. A complete inventory includes explicit acknowledgment of what is missing.

## Step 2: Navigation Mapping

For each screen, identify every interactive element that causes navigation.

### Process

1. **Scan each screen** -- Identify all tappable, clickable, or swipeable elements.
2. **Classify the navigation element** -- Tab, button, link, gesture, menu item, breadcrumb, back arrow.
3. **Determine destination** -- Where does each element lead? Map to a screen ID from the inventory. If the destination is not in the inventory, mark it as `UNKNOWN-[description]`.
4. **Note element location** -- Top bar, bottom bar, inline, floating.

### Platform-Specific Navigation Elements

| Platform | Common Elements |
|----------|----------------|
| Mobile (iOS) | Tab bar, navigation bar back button, swipe gestures, pull-to-refresh, floating action button, bottom sheet trigger |
| Mobile (Android) | Bottom navigation, navigation drawer/hamburger, FAB, top app bar, system back button |
| Web | Top nav links, sidebar menu, breadcrumbs, URL routing, footer links, logo-home link |
| Desktop | Menu bar, sidebar tree, toolbar buttons, keyboard shortcuts, context menus |

### Output Format

```
NAVIGATION MAP:

Screen: S01-home
  Element               | Type      | Location    | Destination
  ----------------------|-----------|-------------|------------------
  Profile avatar        | Button    | Top-right   | S02-profile
  Tab: Search           | Tab       | Bottom bar  | UNKNOWN-search
  Settings gear         | Icon btn  | Top-left    | S03-settings
  Feed item tap         | List item | Content     | UNKNOWN-post-detail
  FAB (+)               | FAB       | Bottom-right| UNKNOWN-compose
  Pull down             | Gesture   | Content     | S01-home (refresh)

Screen: S02-profile
  Element               | Type      | Location    | Destination
  ----------------------|-----------|-------------|------------------
  Back arrow            | Button    | Top-left    | [previous screen]
  Edit Profile          | Button    | Inline      | UNKNOWN-edit-profile
  Tab: Posts             | Tab       | Content     | S02-profile (tab)
  Tab: Likes            | Tab       | Content     | S02-profile (tab)
```

## Step 3: Transition Identification

Document how users move between screens, what triggers each transition, and what data carries across.

### Transition Properties

For each connection between screens, capture:

| Property | Description |
|----------|-------------|
| Trigger | What action initiates the transition (tap, swipe, submit, timer) |
| Animation type | Push (slide), modal (rise), fade, tab switch, replace, none |
| Direction | Forward (deeper), backward (return), lateral (sibling), overlay |
| Data carried | What information passes to the next screen (user ID, search query, selected item) |
| Reversibility | Can the user return? How? (back button, swipe back, close button, system back) |
| Conditions | Any prerequisites (authentication, completed form, network availability) |

### Output Format

```
TRANSITIONS:

  FROM          → TO              | Trigger          | Type    | Direction | Data Carried
  ------        → ------          | -------          | ----    | --------- | -----------
  S01-home      → S02-profile     | Tap avatar       | Push    | Forward   | user_id
  S02-profile   → S01-home        | Back arrow       | Pop     | Backward  | none
  S01-home      → S03-settings    | Tap gear icon    | Push    | Forward   | none
  S01-home      → UNKNOWN-compose | Tap FAB          | Modal   | Overlay   | none
  S03-settings  → UNKNOWN-theme   | Tap "Theme"      | Push    | Forward   | current_theme

CONDITIONAL TRANSITIONS:
  S03-login → S01-home: Requires successful authentication
  UNKNOWN-compose → S01-home: Requires post submission (or cancel)
```

## Step 4: User Journey Construction

Assemble screens into named journeys organized around user goals.

### Process

1. **Identify user goals** -- What does a user come to this app to accomplish? (browse content, make a purchase, update profile, onboard).
2. **Trace the path** -- For each goal, trace the screen sequence from entry to completion.
3. **Name the journey** -- Use goal-oriented naming (not screen-oriented).
4. **Mark start and end** -- Every journey has a clear beginning and defined completion state.
5. **Note decision points** -- Where does the user choose between paths?
6. **Note failure paths** -- What happens if the user fails at a step? (wrong password, network error, validation failure).

### Output Format

```
USER JOURNEYS:

Journey: First-Time Onboarding
  Goal: New user creates account and reaches home feed
  Start: S03-login
  End: S01-home
  Path: S03-login → UNKNOWN-register → UNKNOWN-onboarding → S01-home
  Decision points:
    - S03-login: choose login vs. register
    - UNKNOWN-register: choose email vs. social signup
  Failure paths:
    - S03-login: invalid credentials → error state (NOT CAPTURED)
    - UNKNOWN-register: duplicate email → error state (NOT CAPTURED)
  Missing screenshots: register, onboarding, error states
  Completeness: PARTIAL — 1 of 4 screens captured

Journey: Profile Viewing
  Goal: View another user's profile from the feed
  Start: S01-home
  End: S02-profile
  Path: S01-home → S02-profile
  Decision points: none
  Failure paths: none visible
  Missing screenshots: none for this journey
  Completeness: COMPLETE
```

### Completeness Rating

| Rating | Meaning |
|--------|---------|
| COMPLETE | All screens in the journey are captured |
| PARTIAL | Some screens are captured, gaps identified |
| SKELETAL | Only entry or exit point captured, most screens missing |
| INFERRED | Journey is hypothesized from navigation elements but no screens exist |

## Step 5: Entry and Exit Point Mapping

For every screen in the inventory, document all ways a user can arrive and all ways a user can leave.

### Output Format

```
ENTRY/EXIT MAP:

Screen: S01-home
  Entry points:
    - App launch (direct)
    - Back from S02-profile (pop)
    - Back from S03-settings (pop)
    - Tab bar from any screen (tab switch)
    - Post-login redirect from S03-login (replace)
  Exit points:
    - S02-profile via avatar tap (push)
    - S03-settings via gear icon (push)
    - UNKNOWN-search via search tab (tab switch)
    - UNKNOWN-compose via FAB (modal)
    - UNKNOWN-post-detail via feed item (push)
  Entry count: 5
  Exit count: 5

Screen: S03-login
  Entry points:
    - App launch when unauthenticated (direct)
    - Logout from S03-settings (replace)
  Exit points:
    - S01-home via successful login (replace)
    - UNKNOWN-register via signup link (push)
    - UNKNOWN-forgot-password via link (push)
  Entry count: 2
  Exit count: 3
```

## Step 6: Flow Validation

Audit the assembled flow for structural problems.

### Validation Checks

| Check | What to Look For | Severity |
|-------|------------------|----------|
| Dead ends | Screens with no exit points | Critical |
| Orphaned screens | Screens with no entry points | Critical |
| Circular traps | Loops with no escape (A -> B -> A with no other exits) | High |
| Missing error states | Task screens without visible error handling | Medium |
| Missing empty states | List/feed screens without empty state | Medium |
| Missing loading states | Data-dependent screens without loading indicator | Medium |
| Unreachable actions | Key actions requiring too many taps/clicks | Medium |
| Single entry point | Important screens reachable only one way | Low |
| Missing confirmation | Destructive actions without confirmation step | High |
| No back navigation | Screens where return path is unclear | High |

### Output Format

```
FLOW VALIDATION:

CRITICAL ISSUES:
  - S04-checkout: DEAD END — no exit after payment confirmation
  - UNKNOWN-archive: ORPHANED — no navigation element leads here

HIGH ISSUES:
  - S01-home ↔ S02-profile: CIRCULAR — only two screens link to each other
    with no other exits from S02-profile
  - UNKNOWN-delete-account: no confirmation dialog captured

MEDIUM ISSUES:
  - S01-home: no empty state screenshot (what if feed is empty?)
  - S02-profile: no loading state (profile data is async)
  - S03-settings: no error state (what if save fails?)

LOW ISSUES:
  - S02-profile: reachable only from S01-home feed item tap

SUMMARY:
  Total screens: [N]
  Screens with issues: [N]
  Critical: [N] | High: [N] | Medium: [N] | Low: [N]
```

## Step 7: Flow Documentation

Produce the final flow map combining all previous steps into a deliverable document.

### Final Document Structure

```
FLOW MAP: [App/Product Name]
Date: [date]
Platform: [platform]
Screenshots analyzed: [N]

1. SCREEN INVENTORY
   [From Step 1]

2. NAVIGATION ARCHITECTURE
   [Synthesized from Step 2 — overall navigation paradigm,
    primary vs secondary navigation, global vs local nav]

3. TRANSITION CATALOG
   [From Step 3]

4. USER JOURNEYS
   [From Step 4 — ordered by priority/frequency]

5. ENTRY/EXIT MATRIX
   [From Step 5 — summarized as a matrix]

   Screen  | Entry Count | Exit Count | Balance
   --------|-------------|------------|--------
   S01     | 5           | 5          | Balanced
   S02     | 2           | 1          | Exit-limited
   S03     | 3           | 3          | Balanced

6. VALIDATION RESULTS
   [From Step 6]

7. GAPS AND RECOMMENDATIONS
   Missing screenshots needed:
   - [screen]: needed for [journey] completion
   - [state]: needed for [validation check]

   Recommended next steps:
   - Capture [specific screenshots] to complete [journey]
   - Design [missing state] for [screen]
   - Resolve [critical issue] by [recommendation]
```

### Entry/Exit Balance

The entry/exit matrix reveals flow structure:

| Pattern | Meaning | Action |
|---------|---------|--------|
| High entry, high exit | Hub screen | Expected for home/dashboard |
| High entry, low exit | Funnel endpoint | Check for dead ends |
| Low entry, high exit | Decision point | Verify entry paths are discoverable |
| Low entry, low exit | Leaf screen | Normal for detail/utility screens |
| Zero entry | Orphaned | Critical: screen is unreachable |
| Zero exit | Dead end | Critical: user is trapped |

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Mapping navigation before inventorying all screens | Complete the full inventory first; premature mapping misses connections |
| Assuming navigation is bidirectional | Verify return paths explicitly; many transitions are one-directional |
| Ignoring platform navigation conventions | Check for system back button (Android), swipe-to-go-back (iOS), browser back (web) |
| Treating overlays as separate screens | Overlays share context with their parent screen; track the parent relationship |
| Organizing flows by screen adjacency instead of user goals | Name journeys after goals ("Purchase Flow"), not screens ("Screen A to Screen B") |
| Skipping gap documentation | Every missing screen and state must be explicitly called out |
| Forgetting conditional transitions | Authentication gates, permission checks, and feature flags create conditional paths |
| Mapping only the happy path | Document error, empty, and loading states; these are part of the flow |

## Quality Checklist

Before delivering any flow map:

**Completeness:**
- [ ] Every screenshot has a screen ID and type classification
- [ ] Every screen has defined entry points
- [ ] Every screen has defined exit points
- [ ] Gaps are explicitly documented with specific missing screens named
- [ ] Platform navigation paradigm is identified and applied

**Navigation:**
- [ ] Every interactive element is mapped to a destination
- [ ] Unknown destinations are labeled `UNKNOWN-[description]`
- [ ] Transition types (push, modal, tab switch) are specified
- [ ] Return paths are verified, not assumed

**Journeys:**
- [ ] At least one user journey is defined
- [ ] Every journey has a named goal, start point, and end point
- [ ] Decision points are documented
- [ ] Failure paths are noted (even if screenshots are missing)
- [ ] Completeness rating is assigned to each journey

**Validation:**
- [ ] Dead end check completed
- [ ] Orphaned screen check completed
- [ ] Missing states (error, empty, loading) noted
- [ ] Circular navigation check completed
- [ ] Entry/exit balance reviewed
