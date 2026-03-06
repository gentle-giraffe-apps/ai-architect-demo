# Architect Mode

## The Deeper Shift

In assistant mode, you write prompts. In orchestrator mode, you write specs. In architect mode, you design the system that governs how AI agents operate across all tasks.

The engineer's output is no longer code. It's constraints, patterns, quality standards, and operating boundaries.

## What Architects Define

### Boundaries

What is the agent allowed to do? What is it forbidden from doing?

This lives in `.claude/settings.json`. For example:

```json
{
  "permissions": {
    "allow": ["Bash(git *)", "Bash(npm *)", "Read", "Write", "Edit"],
    "deny": ["Read(.env)", "Read(secrets/**)"]
  }
}
```

This is a security architecture decision. It determines the blast radius of an autonomous agent. Get it wrong, and a prompt injection in a dependency could exfiltrate secrets. Get it right, and the agent can work freely within safe bounds.

### Quality Standards

What does "done" mean? Architects define this through:

- Test suites that must pass before completion
- Linting rules that enforce code style
- Type checking that catches errors at build time
- Review criteria embedded in `CLAUDE.md`

The agent doesn't decide when it's done. The quality gates do.

### Patterns and Conventions

How should code be structured? What patterns should the agent follow?

```markdown
# From a CLAUDE.md file
- Use repository pattern for database access
- All endpoints return JSON with consistent error format
- Keep functions under 30 lines
- Write tests before implementation
```

These instructions persist across sessions. Every time the agent works in this repo, it follows these patterns. The architect shapes behavior at scale, not one prompt at a time.

### Operating Instructions

A `CLAUDE.md` file (see [CLAUDE.md](./CLAUDE.md) in this directory) acts as standing orders for an AI agent. It includes:

- Project purpose and context
- Coding standards
- Testing expectations
- Commit behavior
- Safety rules
- Completion conditions

This is the equivalent of onboarding documentation for a new team member — except the team member is an AI that reads it every time it starts working.

## Why This Matters

When AI can generate implementation, the differentiator is no longer "can you write the code." It's:

- **Can you define what good looks like?**
- **Can you set boundaries that prevent harm?**
- **Can you design systems that produce reliable output without constant supervision?**

These are architecture skills. They've always mattered. But now they're the primary output of senior engineering work, not a side activity.

## The Repo Is the Architecture

In an AI-accelerated workflow, the repo itself becomes the architecture document:

- `.claude/settings.json` defines permissions
- `CLAUDE.md` defines behavior
- Test suites define quality
- Specs define goals
- Directory structure defines boundaries

The engineer who shapes these artifacts is the architect. The AI that operates within them is the builder.
