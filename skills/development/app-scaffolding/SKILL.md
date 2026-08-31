---
name: app-scaffolding
description: Use this skill when the user has decided to build a mobile app and needs a complete production blueprint — not brainstorming, not feature ideas, but an actual build brief. Covers both iOS and Android with exact tech stack, screen specs, monetization, and a 30-day sprint plan. Use when the user says things like "Scaffold this app" "Give me a build plan" "Write the PRD" "How do I build this?" "Create a technical spec" "Blueprint this idea" even if they don't mention "scaffolding" or the number of sections.
license: MIT
---

# Superhuman Mobile App Scaffolding

Take a validated mobile app candidate and produce a complete, production-ready build blueprint. A development agent or senior engineer should be able to build the complete iOS + Android app from this document alone — zero clarification questions needed.

## Input Required

- APP_NAME, APP_CATEGORY, PRIMARY_KEYWORD
- Scout summary (what was discovered, traction data)
- GEO/ASO competitive matrix (competitors, gaps, keyword data)
- Scrutiny winner rationale (why this app won)
- Killer differentiator (one sentence)
- Revenue model (tiers, price points)

## Output — 12 Sections

### Section 0: App Identity & Positioning
- ASO-optimized name + subtitle (30 chars each) with ranking rationale
- One-liner value proposition (toilet test)
- Visual identity: hex colors with psychology, typography (SF/Compose), icon set (8-10 icons), app icon description
- Screenshot strategy: 5 screenshots per platform with overlay copy

### Section 1: iOS Architecture (SwiftUI-First)
- Tech stack: Swift 6, SwiftData, CloudKit, RevenueCat, TelemetryDeck
- 6-screen spec with SwiftUI views, state management, animations, accessibility
- WidgetKit (3 sizes), App Intents/Siri, Live Activities, SharePlay, push notifications, privacy label

### Section 2: Android Architecture (Jetpack Compose-First)
- Tech stack: Kotlin 2.0, Room, Firestore, Hilt, Material 3
- Play Billing setup with offer tags, grace period, account hold
- Material You theming, predictive back, App Shortcuts, notification channels, WorkManager

### Section 3: SEO & GEO Optimization
- App Store keyword field (100 chars exact) with justification per keyword
- Title + subtitle keyword weighting strategy
- Play Store listing: title, short description, full description keyword density
- Landing page structure with Open Graph, schema.org markup
- GEO: FAQ section (8 Q&A blocks), query-style headings, answer-first phrasing, fact clusters
- Blog topic cluster (5 pillar posts with target keywords)

### Section 4: Behavioral Architecture (Hooked Model)
- External triggers: 4 push notifications with exact copy, timing, deep links
- Internal triggers: 3 negative-emotion-to-app-open associations
- Fogg Behavior Model scoring (Motivation, Ability, Trigger) — must exceed 6/9/9
- Variable rewards: Tribe (social), Hunt (discovery), Self (mastery) — specific mechanics
- Investment: data, social, financial, skill, reputation moats

### Section 5: Visual Design System
- 4 design principles
- 6 key animations with exact duration, spring damping, easing curves
- Haptic feedback map (light/medium/heavy/selection/notification)
- Accessibility as luxury: VoiceOver, Dynamic Type, Reduce Motion, color blindness

### Section 6: Financial Architecture
- Pricing tiers table with per-tier rationale
- Unit economics: CAC, LTV, payback period, churn targets, referral value
- Monetization flow: 8-step user journey from download to annual renewal
- Cancellation intercept: 5-step flow (pause, discount, frequency change, data promise)

### Section 7: Virality Engine
- 5 shareable moments with exact copy and visual card descriptions
- Invite mechanics: friction-free (native share sheet), sender/receiver incentive
- App Store rating protection: route sub-3-star to feedback form, 4-5 star to App Store
- Watermark strategy

### Section 8: Technical Specification
- DB schema (SQL DDL) with CloudKit/Firestore sync annotations
- REST API endpoints
- Push notification schema (JSON)
- Third-party dependency list (NO Facebook SDK, NO AdMob at launch)
- Local AI architecture where applicable (llama.cpp, MediaPipe, MLX Swift)

### Section 9: 30-Day MVP Sprint
- Week 1-4: day-by-day iOS + Android + shared tasks
- MVP feature cut list (DO NOT build in sprint 1)

### Section 10: Launch Checklist
- T-14 pre-launch (17 items)
- T=0 launch day (8 items)

### Section 11: Post-Launch Iteration
- Week 1: observe only
- Week 2-4: quick wins
- Month 2-3: feature expansion

### Section 12: Anti-Patterns
- 10 things you MUST NOT do (notification timing, splash screens, default paywalls, account requirements, ads in first 90 days, etc.)

## Quality Gate
Read the entire document. If YOU would have questions about implementation, add the missing detail. This is a production brief, not a brainstorming document.

Before generating any scaffold, read `references/corrections.md` — it documents real failures: scaffolding a non-mobile app (Forge), claiming unavailable tools (Runway/Luma), and missing local AI architecture (fixed after Joerg linked ai-agents-from-scratch).