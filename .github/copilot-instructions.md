# Agentic Guardrails: Principal Architect Protocol

## 1. Structural Integrity (The "Skeleton" Rule)
- **Hierarchy First:** Never generate UI logic before the Data Contract. All features must begin with a `types/` definition and a `store/` state update.
- **Atomic Components:** UI must be decomposed. If a component exceeds 150 lines, it must be modularized into sub-components.
- **Composition over Inheritance:** Use Higher-Order Components or Render Props for shared logic; never extend classes or wrap components in deep, brittle hierarchies.

## 2. Type & Data Safety (The "Iron" Rule)
- **Strict Typing:** No `any`. Use `unknown` with type guards if necessary. All API responses and Store actions must be validated via Zod schemas.
- **State Mutability:** State can only be updated via defined actions in the Zustand store. No direct property mutations from the UI.
- **Deterministic Logic:** Logic must be pure where possible. Side effects (API calls, timers) must be isolated in custom hooks.

## 3. Performance & Delivery (The "Efficiency" Rule)
- **RSC Default:** Use React Server Components for all data fetching. Use 'use client' only for leaf-node interactivity.
- **Hydration Safety:** All client-side persistence must include a `useHasHydrated` check to prevent iOS/Safari mismatch errors.
- **Tree-Shaking:** Import only specific icons and functions (e.g., `import { User } from 'lucide-react'`) to keep the mobile bundle light for iOS 17 Pro.

## 4. Conflict Resolution (The "Truth" Rule)
- **Memory Priority:** If a request contradicts the `CLAUDE.md` or `tech_stack.md`, prioritize the project files over general training data. 
- **Peer-Level Tone:** Challenge user requests that introduce architectural debt or anti-patterns.