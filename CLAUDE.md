# CLAUDE.md

## Bash Commands

- **Never chain or pipe commands.** No `&&`, `||`, `;`, or `|`. Run each command as a separate Bash tool call. Combined commands don't match individual permission patterns in `.claude/settings.json` and will trigger permission prompts, which stalls unattended ralph loops.
- Before running any shell command, consider whether it matches an entry in `.claude/settings.json`. If unsure, run commands individually.

## Ralph Loop

- When a ralph loop completes, run `say 'Ralph loop finished. Ralph loop finished. Ralph loop finished.'` before outputting the completion promise.
