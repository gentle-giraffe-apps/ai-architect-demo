# From AI Assistant to AI Architect

**A meetup talk about what changes when AI can write the code.**

## The Thesis

Most engineers use AI as an assistant: ask a question, get an answer, copy-paste, repeat. This works, but it keeps the human as the bottleneck in every loop.

The next level isn't better prompting. It's changing your role.

## Three Levels of AI Usage

### 1. Assistant Mode

You ask. AI answers. You decide what to do with it.

This is where most people are today. The AI is reactive, and the human drives every step of the workflow manually.

### 2. Orchestrator Mode

You write a spec. AI executes it in a loop. You monitor and course-correct.

The human moves from doing the work to defining the work. Agent loops (like `ralph-loop` for Claude Code) handle the iteration. The human intervenes when judgment is needed.

### 3. Architect Mode

You define constraints, quality gates, permissions, and patterns. AI operates within those boundaries across tasks.

The human's output is no longer code — it's the system that governs how AI writes code. This includes files like `CLAUDE.md`, `.claude/settings.json`, specs, and test suites.

## The Key Insight

The `.claude/settings.json` file in this repo defines what an AI agent is allowed to do. The `CLAUDE.md` file defines how it should behave. These are not configuration trivia. **They are architecture.**

When AI can write the implementation, the engineer's job shifts to:

- **What** should the system do?
- **What** should it never do?
- **How** do I verify it got it right?

That's architectural thinking. And it matters more now than it ever has.

## Repo Structure

```
1-assistant-mode/              How most people use AI today
2-orchestrator-mode/           Driving AI with specs and loops
3-architect-mode/              Defining constraints and quality gates
4-tetroid-breakout-case-study/ Case study: Breakout × Tetris hybrid game
5-julia-surf-case-study/       Case study: Julia set fractal exploration game
6-paul-instead-of-ralph/       PAUL framework: structured AI project management
presentation/                  Slide deck and generator script
discussion-prompts.md          Questions for the group
.claude/                       Live example of AI architecture
```

## Case Studies

### [Tetroid Breakout](4-tetroid-breakout-case-study/)

A Breakout × Tetris hybrid arcade game built with Python and pygame. Tetromino pieces spawn and stack in the grid while you bounce a ball off a paddle to destroy them. This project demonstrates iterative AI-assisted development — the entire game was built through successive Ralph Loop iterations, each adding a composable feature (paddle, ball physics, tetromino spawning, row clearing, scoring, difficulty scaling).

### [Fractal Surfer](5-julia-surf-case-study/)

An arcade-style exploration game where the player navigates a continuously evolving Julia set fractal field. Stable fractal regions restore energy, chaotic regions drain it, and the fractal boundary offers high scoring potential. The fractal slowly zooms and morphs over time, creating an environment that never repeats. Another case study in iterative AI-assisted development, this time with a more visually ambitious target.

## PAUL: Structured AI Project Management

### [PAUL Instead of Ralph](6-paul-instead-of-ralph/)

Ralph loops are simple: give Claude Code a prompt and an interval, and it repeats. PAUL (Plan-Apply-Unify Loop) is the next level — it breaks work into milestones, phases, and plans with explicit acceptance criteria, boundaries, and verification steps. The loop is always **PLAN → APPLY → UNIFY**, and state persists across sessions via `STATE.md`.

Key differences from Ralph loops:
- **Planning before execution** — every task has acceptance criteria before code is written
- **Scope control** — boundaries prevent the agent from drifting
- **Progress tracking** — percentage bars, phase completion, milestone status
- **Session continuity** — resume where you left off with `/paul:resume`

Install: `npx paul-framework` · Repo: [github.com/ChristopherKahler/paul](https://github.com/ChristopherKahler/paul)

## About This Repo

This repo was built during a live conversation between a human and Claude Code. The human defined the structure and goals. The AI executed. The permissions in `.claude/settings.json` were designed interactively, with security tradeoffs discussed in real time.

This repo is itself an example of the shift it describes.
