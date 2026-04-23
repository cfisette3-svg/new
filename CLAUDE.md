# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Status

This repository is currently a scaffold. It contains no source code, no package manifest, and no build/test/lint tooling. The only tracked files are `README.md` (placeholder) and `.github/copilot-instructions.md` (guardrails below).

Because there is no established toolchain yet, there are no project-specific build, test, or lint commands to document. When code is added, update this file with the commands and architecture that actually exist — do not invent conventions ahead of the code.

## Guardrails (from `.github/copilot-instructions.md`)

These apply to all code added to this repository:

- Prefer composition over inheritance.
- Maintain strict type safety.
- Use Server Components by default. (Implies a React Server Components environment, e.g. Next.js App Router — confirm the framework choice before adding client-side patterns.)

## Branching

Development for this task happens on `claude/add-claude-documentation-CxW4d`. `main` is the default branch.
