---
id: doc-1
title: Educational Roadmap
type: other
created_date: '2026-03-12 04:10'
---
# Chimera Educational Roadmap

This document outlines the strategic initiatives to transform Chimera from a vulnerable application sandbox into a guided learning platform for security engineering.

## 1. Interactive "Remediation Sandbox"
**Goal:** Enable users to fix vulnerabilities in real-time and verify the fix.
- **Mechanism:** The UI provides a code editor where users can apply a remediation. The API supports switching between "Vulnerable" and "Patched" logic for specific endpoints based on user session or global state.
- **Value:** Reinforces the "Build" side of security, not just the "Break" side.

## 2. The "Payload Journey" Visualizer
**Goal:** Visualize how malicious data transforms as it moves through the stack.
- **Mechanism:** Propagate a unique Request ID across the system. Visualize the lifecycle: `Browser -> WAF -> Controller -> Data Sanitizer -> SQL Query -> Database`.
- **Value:** Demystifies the "magic" of security filters and sanitization.

## 3. Narrative "Scenario-Based" Missions
**Goal:** Shift focus from exploring pages to completing structured security missions.
- **Mechanism:** A `MissionProvider` tracks specific objectives (e.g., "Bypass the Insurance MFA"). Scenarios can dynamically reconfigure the API's vulnerability profile.
- **Value:** Provides context and narrative drive for learners.

## 4. Theory-to-Practice (Contextual Documentation)
**Goal:** Map practical exploits directly to industry standards.
- **Mechanism:** Link specific findings in `XRayInspector` and `VulnerabilityModal` to OWASP Top 10 and CWE entries.
- **Value:** Teaches the formal language of security during the practical experience.

## 5. Defensive Layers Control Panel
**Goal:** Allow comparison between secured and insecure system states.
- **Mechanism:** A central dashboard to toggle global security features (CSRF, CSP, SQLi sanitization, etc.) on or off.
- **Value:** Demonstrates the impact of specific defensive controls on the same exploit payload.
