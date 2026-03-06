# Orchestrator Mode

## The Next Level

In orchestrator mode, you stop being the loop. You define what needs to happen, and an AI agent executes it — running code, reading output, fixing errors, and iterating until the task is done.

The shift: instead of asking "write me a function," you write a spec and say "build this."

## What Changes

| Assistant Mode | Orchestrator Mode |
|---|---|
| You paste errors back into chat | The agent runs tests and reads failures itself |
| You decide when to stop | Completion criteria decide when to stop |
| One prompt at a time | A spec drives multiple iterations |
| You copy code into files | The agent writes files directly |
| You are the loop | The agent is the loop |

## How It Works in Practice

1. You write a spec (see [spec.md](./spec.md) for an example)
2. You start an agent loop (e.g., `ralph-loop` for Claude Code)
3. The agent reads the spec, creates files, runs tests, and iterates
4. You watch, and intervene only when judgment is needed

## What a Loop Looks Like

```
[Loop iteration 1] Agent reads spec, creates project structure
[Loop iteration 2] Agent writes implementation files
[Loop iteration 3] Agent runs tests — 3 of 7 fail
[Loop iteration 4] Agent reads failures, fixes two bugs
[Loop iteration 5] Agent runs tests — 1 of 7 fails
[Loop iteration 6] Agent fixes edge case, all tests pass
[Loop iteration 7] Agent reviews code quality, cleans up
[Complete] Completion criteria met
```

No human intervention required for any of those steps.

## The Human's Role Changes

You're no longer writing code or managing the back-and-forth. You're:

- **Defining the goal** clearly enough that an agent can execute it
- **Setting constraints** so the agent doesn't go off track
- **Choosing when to intervene** vs. when to let it run
- **Reviewing the output** with the judgment that comes from experience

This is orchestration. You're conducting, not playing every instrument.

## Tools That Enable This

- **Claude Code** with agent loops like `ralph-loop`
- **Spec files** that define goals, scope, and completion criteria
- **Test suites** that act as automated quality gates
- **Permission configs** that bound what the agent can do

## The Spec Is the New Unit of Work

In assistant mode, the unit of work is a prompt. In orchestrator mode, it's a spec. A good spec includes:

- What to build
- What files to create or modify
- What constraints to follow
- How to know when it's done

See [spec.md](./spec.md) for a concrete example.
