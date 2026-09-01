# ReviewAI — Frontend Architecture & UI Specification

## Overview

The ReviewAI Frontend is a modern, developer-centric Single Page Application (SPA) built with **React**, **TypeScript**, and **Tailwind CSS**.

---

## Planned Core Components (Target for Module 7)

- **Code Editor**: Monaco-powered code editor with inline line-highlighting of security and bug findings.
- **Review Findings Panel**: Real-time severity filter (Critical, High, Medium, Low, Info) with categorization badges.
- **AI Explanation & Refactoring**: Interactive drawer displaying root cause explanation, fix rationale, and diff preview.
- **Quality Score Gauge**: Interactive visual display of code quality score (0-100) and category ratings.
- **Review History**: Persistent local / server-side history of past reviews.
- **Settings Modal**: Configure local Ollama model names, static analyzer toggles, and UI preferences.

---

## Shared Type Contracts

Domain types matching the backend models are maintained in `src/types/index.ts`.
