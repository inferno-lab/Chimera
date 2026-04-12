---
id: TASK-11
title: Refactor vuln-web header controls to absorb bottom-left toolbar actions
status: Done
assignee:
  - codex
created_date: '2026-03-12 09:54'
updated_date: '2026-03-12 10:08'
labels:
  - feature
  - vuln-web
  - ui
dependencies: []
references:
  - >-
    /Users/nferguson/Developer/Security Lab
    Suite/Chimera/apps/vuln-web/src/components/Layout.tsx
  - >-
    /Users/nferguson/Developer/Security Lab
    Suite/Chimera/apps/vuln-web/src/components/KillChainTracker.tsx
  - >-
    /Users/nferguson/Developer/Security Lab
    Suite/Chimera/apps/vuln-web/src/components/AiAssistant.tsx
  - >-
    /Users/nferguson/Developer/Security Lab
    Suite/Chimera/apps/vuln-web/src/components/RedTeamConsole.tsx
  - >-
    /Users/nferguson/Developer/Security Lab
    Suite/Chimera/apps/vuln-web/src/components/XRayInspector.tsx
  - >-
    /Users/nferguson/Developer/Security Lab
    Suite/Chimera/apps/vuln-web/src/components/WafVisualizer.tsx
priority: medium
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Rework the Chimera portal header so the existing utility controls no longer rely on the floating bottom-left launcher cluster. Keep exploit hints as a top-level header toggle, keep kill chain status visible from the left side of the header, preserve the AI assistant as a bottom-right floating control, and move the remaining tool entry points into header pills or dropdown menus where they fit cleanly.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 The shared header exposes kill chain status on the left side and keeps the exploit hints toggle as a top-level control.
- [x] #2 The bottom-left floating launcher cluster is reduced so non-chat utility tools are reachable from header pills and/or dropdown menus instead of separate floating buttons.
- [x] #3 The AI assistant launcher and panel are repositioned to the bottom-right corner without regressing existing open/close behavior.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Refactor the shared header in apps/vuln-web/src/components/Layout.tsx into a taller two-row layout that keeps the portal identity and current route title while adding a persistent kill chain trigger on the left and a top-level hints toggle on the right.
2. Introduce grouped header actions for the remaining utility surfaces (connectivity, exploit tour, theme/profile, red team console, X-Ray inspector, WAF visualizer) using pills and dropdown menus so the bottom-left floating launcher cluster can be removed without losing access.
3. Update the individual utility components so their floating closed-state launch buttons can be hidden or suppressed when the header owns discovery, while preserving their open panels and keyboard shortcuts.
4. Reposition the AI assistant launcher and panel to the bottom-right corner and keep its open/minimize/close behavior intact.
5. Run targeted frontend verification on the touched files, capture any residual issues, and record the results in the task notes/final summary.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Implemented header-driven utility controls in apps/vuln-web/src/components/Layout.tsx so kill chain stays top-left, hints remain top-level, the non-chat tool launchers live under a Lab Tools dropdown, and the chatbot launcher stays bottom-right.

Follow-up polish from user feedback: collapsed the desktop header back to a single-row layout, removed the non-functional user profile button, and restored a smaller inline Chimera Portals wordmark next to the logo.

Verification: `pnpm --dir apps/vuln-web test src/components/AiAssistant.test.tsx src/components/Connectivity.test.tsx` passed (17 tests). `pnpm --dir apps/vuln-web exec eslint src/components/Layout.tsx src/components/KillChainTracker.tsx src/components/RedTeamConsole.tsx src/components/XRayInspector.tsx src/components/WafVisualizer.tsx src/components/AiAssistant.tsx src/components/AiAssistant.test.tsx` passed with no output. `pnpm --dir apps/vuln-web build` passed.

Independent review artifact: `.agents/reviews/review-20260312-060534.md` via agent-loops specialist-review. Artifact reported generic concerns (relative API paths, global events, hardcoded colors) that do not appear actionable for this intentionally vulnerable proxied frontend slice, so no follow-up code changes were made from that review.

User requested a final header alignment tweak after review: move the kill chain control from the left cluster into the right-side control rail, and visually separate the API status pill from the actionable controls.

Final user-requested polish pass on Layout.tsx: moved kill chain into the right-side control rail, kept the API status pill at the left edge of that rail with extra visual separation, restored the tour label to `Exploit Tour`, ensured the dark/light toggle is the right-most control, and reduced the Chimera logo size again so the wordmark stays dominant.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Refactored the shared Chimera header so the former bottom-left tool cluster is absorbed into header controls: kill chain status now sits on the left side of the header, hints remain a top-level toggle, connectivity/tour/theme stay reachable inline, and Red Team / X-Ray / WAF launch from a Lab Tools dropdown. The AI assistant launcher and panel were moved to the bottom-right, the dead user profile button was removed, and the header branding was tightened back into a compact single-row desktop layout. Validation completed with targeted Vitest coverage for AI assistant/connectivity, targeted ESLint on the touched components, a successful vuln-web production build, and an independent specialist review artifact for the touched files.

Follow-up UI polish after live feedback moved the kill chain pill into the right control group, increased the API status pill spacing, renamed the tour button to `Exploit Tour`, kept the theme toggle as the right-most control, and reduced the logo size so the title remains visible without overpowering the header.
<!-- SECTION:FINAL_SUMMARY:END -->
