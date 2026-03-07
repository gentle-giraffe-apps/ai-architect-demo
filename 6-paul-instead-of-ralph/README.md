# PAUL Instead of Ralph

**Repo:** [github.com/ChristopherKahler/paul](https://github.com/ChristopherKahler/paul)

PAUL (Plan-Apply-Unify Loop) is a structured project management framework for Claude Code. Instead of running a simple recurring prompt, PAUL breaks work into milestones, phases, and plans — each with explicit acceptance criteria, boundaries, and verification steps. The result is predictable, trackable AI-assisted development with clear progress visibility.

## Installation

### Prerequisites

- [Claude Code CLI](https://docs.anthropic.com/en/docs/claude-code) installed and authenticated
- A project directory (new or existing)

### Setup

1. Run the installer (works on Mac, Windows, and Linux):

```bash
npx paul-framework
```

The installer will prompt you to choose:
- **Global installation** — installs to `~/.claude/` for use across all projects
- **Local installation** — installs to `./.claude/` for the current project only

For non-interactive installs:

```bash
npx paul-framework --global    # Install globally
npx paul-framework --local     # Install locally
```

2. Verify installation by running `/paul:help` in Claude Code.

> **Note:** You may need to restart Claude Code to reload the slash commands after initial installation.

To update to the latest version:

```bash
npx paul-framework@latest
```

## What is a Ralph Loop?

A Ralph loop is a simple recurring execution pattern for Claude Code. You give it a prompt and an interval, and it re-runs that prompt repeatedly:

```
/ralph-loop 5m "Check test results and fix any failures"
```

Ralph loops are useful for:
- Polling for status changes (CI/CD, deployments)
- Babysitting long-running processes
- Simple repetitive tasks on a timer

The key characteristic: **Ralph loops have no memory between iterations.** Each cycle starts fresh with the same prompt. There is no planning, no state tracking, and no progress measurement.

## PAUL vs Ralph Loop

| Aspect | Ralph Loop | PAUL |
|--------|-----------|------|
| **Structure** | Single prompt, repeated | Milestones > Phases > Plans > Tasks |
| **Planning** | None — just runs a prompt | Explicit plans with acceptance criteria |
| **State** | No persistent state | `STATE.md`, `ROADMAP.md`, `PROJECT.md` |
| **Scope control** | Can drift — no boundaries | Boundaries section prevents scope creep |
| **Progress** | No tracking | Percentage bars, phase/plan completion |
| **Verification** | None built-in | Every task has a verify step |
| **Session continuity** | Lost on restart | `STATE.md` enables `/paul:resume` |
| **Complexity** | Minimal — one command | More setup, but scales to large projects |
| **Best for** | Monitoring, polling, simple fixes | Multi-step features, full project builds |

### When to use Ralph Loop

- You need to poll something on an interval (deploy status, test runner)
- The task is simple and self-contained each cycle
- You don't need to track progress across cycles
- Quick one-off automation

### When to use PAUL

- You're building something with multiple steps or files
- You want to track what's done and what's next
- You need to resume work across sessions
- You want acceptance criteria before execution starts
- The project has phases that depend on each other

## Using PAUL in a Sample Project

Here's what happens when you use PAUL on a real project — say you're building a CLI tool.

### 1. Initialize (`/paul:init`)

PAUL asks you three questions conversationally:
- What's the core value?
- What are you building?
- Project name?

Then it creates the `.paul/` directory:

```
.paul/
  PROJECT.md    # What you're building and why
  ROADMAP.md    # Phases and milestones
  STATE.md      # Current position in the loop
  phases/       # Plan files live here
```

### 2. Plan (`/paul:plan`)

PAUL reads your project context and creates a `PLAN.md` with:
- **Objective** — what this plan accomplishes
- **Acceptance criteria** — testable Given/When/Then conditions
- **Tasks** — specific actions with files, verify steps, and done criteria
- **Boundaries** — files and areas that must NOT be changed

You review and approve before any code is written.

### 3. Apply (`/paul:apply`)

PAUL executes tasks in order:
- Creates/modifies the specified files
- Runs verification after each task
- Stops at checkpoints if human input is needed
- Reports pass/fail for each task

### 4. Unify (`/paul:unify`)

PAUL compares plan vs actual:
- Did all tasks complete?
- Were there deviations from the plan?
- What decisions were made?
- Updates `STATE.md` and `ROADMAP.md`
- Routes to the next plan or milestone

The loop then repeats: **PLAN > APPLY > UNIFY > PLAN > ...**

## Step-by-Step Tutorial

Let's walk through PAUL with a tiny project: adding a "hello world" Python script with tests.

### Step 1: Initialize

Open Claude Code in your project directory and run:

```
/paul:init
```

PAUL asks:

```
What's the core value this project delivers?
```

You answer: "A simple hello world script with passing tests."

```
What are you building? (1-2 sentences)
```

You answer: "A Python hello.py script and test_hello.py with pytest."

PAUL confirms the project name and creates `.paul/`.

### Step 2: Plan

Run:

```
/paul:plan
```

PAUL creates a plan like:

```
Phase 1: Create Hello World
  Task 1: Create hello.py with a greet() function
  Task 2: Create test_hello.py with pytest tests

  Acceptance Criteria:
    AC-1: greet("World") returns "Hello, World!"
    AC-2: pytest runs with all tests passing
```

You see the full plan and approve it.

### Step 3: Apply

Run:

```
/paul:apply
```

PAUL executes:
- Creates `hello.py` with the `greet()` function
- Verifies the function exists
- Creates `test_hello.py` with pytest tests
- Runs `pytest` to verify tests pass
- Reports: "APPLY complete. 2/2 tasks passed."

### Step 4: Unify

Run:

```
/paul:unify
```

PAUL reconciles:
- Confirms both tasks completed as planned
- No deviations detected
- Updates `STATE.md` progress to 100%
- Creates a `SUMMARY.md` recording what was built

### Step 5: Check Progress

Run:

```
/paul:progress
```

PAUL shows:

```
Milestone: v0.1 Initial Release
Phase: 1 of 1 (Create Hello World) — Complete
Progress: [██████████] 100%

Next action: All phases complete. Consider /paul:complete-milestone.
```

That's it. For larger projects, you'd have multiple phases and plans, but the loop is always the same: **PLAN > APPLY > UNIFY**.

## Available PAUL Commands

| Command | Description |
|---------|-------------|
| `/paul:init` | Initialize PAUL in a new project |
| `/paul:plan` | Create a plan for the next phase |
| `/paul:apply` | Execute an approved plan |
| `/paul:unify` | Reconcile plan vs actual, close the loop |
| `/paul:progress` | Show status and suggest next action |
| `/paul:resume` | Restore context from a previous session |
| `/paul:pause` | Save state for session break |
| `/paul:handoff` | Generate comprehensive handoff document |
| `/paul:verify` | Guide manual acceptance testing |
| `/paul:plan-fix` | Plan fixes for issues found during verify |
| `/paul:discuss` | Explore phase vision before planning |
| `/paul:research` | Research a topic using subagents |
| `/paul:discover` | Research technical options before planning |
| `/paul:add-phase` | Add a new phase to current milestone |
| `/paul:remove-phase` | Remove a future phase |
| `/paul:milestone` | Create a new milestone |
| `/paul:complete-milestone` | Mark current milestone complete |
| `/paul:help` | Show all available commands |
