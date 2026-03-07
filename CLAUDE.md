# CLAUDE.md

## Bash Commands

- **Never chain or pipe commands.** No `&&`, `||`, `;`, or `|`. Run each command as a separate Bash tool call. Combined commands don't match individual permission patterns in `.claude/settings.json` and will trigger permission prompts, which stalls unattended ralph loops.
- Before running any shell command, consider whether it matches an entry in `.claude/settings.json`. If unsure, run commands individually.

## Commands to Avoid (will stall ralph loops)

These commands are **not** in the permission allowlist and will trigger a prompt. Use the workaround instead.

| Avoid | Why | Workaround |
|-------|-----|------------|
| `curl`, `wget` | Network/exfiltration risk | Use `WebFetch` or `WebSearch` tools |
| `ssh`, `scp` | Remote execution risk | Ask user to run manually |
| `docker`, `docker-compose` | Arbitrary container risk | Ask user to run manually |
| `git reset --hard` | Destroys uncommitted work | Use `git reset HEAD *` (soft) or `git restore` |
| `git clean` | Deletes untracked files permanently | Delete specific files with `rm` (only allowed for safe paths) |
| `git push --force` | Overwrites remote history | Use `git push` (non-force) |
| `kill` | Can terminate arbitrary processes | Ask user to run manually |
| `ssh-keygen` | Can overwrite SSH keys | Ask user to run manually |
| `rm` (arbitrary paths) | Only specific safe paths allowed | Use the allowlisted `rm -rf` entries (node_modules, dist, etc.) |
| `chmod`, `chown` | Can change permissions on sensitive files | Ask user to run manually |

### General rules for unattended loops

- **Prefer dedicated tools over Bash.** Use `Read` not `cat`, `Grep` not `grep`, `Glob` not `find`, `Edit` not `sed`.
- **When in doubt, don't run it.** If a command might prompt, skip it and note what you would have run so the user can approve it later.
- **Never guess at permissions.** If you need a command that's not clearly in the allowlist, ask the user first rather than risking a stall.

## Ralph Loop

- When a ralph loop completes, run `say 'Ralph loop finished. Ralph loop finished. Ralph loop finished.'` before outputting the completion promise.
