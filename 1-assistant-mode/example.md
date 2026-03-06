# Assistant Mode

## How Most People Use AI Today

The typical workflow looks like this:

1. Open a chat window
2. Type: "Write me a function that parses CSV files and returns a list of dictionaries"
3. Read the output
4. Copy it into your editor
5. Run it — it fails
6. Paste the error back into the chat
7. Get a fix
8. Repeat until it works

This is useful. It saves time on boilerplate. It helps you learn unfamiliar APIs. But it has limits.

## What Assistant Mode Looks Like

```
You:    "Write a Python function that validates email addresses"
AI:     [generates function]
You:    "It doesn't handle edge cases with plus signs"
AI:     [generates updated function]
You:    "Now write tests for it"
AI:     [generates tests]
You:    "Two tests fail, here's the output: ..."
AI:     [generates fixes]
```

Every step requires the human to:
- Read the output
- Decide what to do next
- Copy context back into the conversation
- Maintain the mental model of what's been done

## The Limits

- **Reactive.** The AI only responds to what you ask. It doesn't anticipate next steps.
- **One prompt at a time.** There's no continuity between tasks unless you manually provide it.
- **Human is the workflow engine.** You are the loop. You run the tests, read the errors, paste them back. The AI never touches your codebase directly.
- **Context is fragile.** Long conversations drift. The AI forgets earlier decisions. You end up re-explaining things.

## When Assistant Mode Is Fine

- Quick one-off questions
- Learning a new library or language
- Generating boilerplate you'll heavily modify
- Rubber-ducking a design problem

## When It's Not Enough

- Multi-file changes that need to stay consistent
- Tasks that require running code, reading output, and iterating
- Any workflow where you're spending more time managing the AI than doing the work
- Projects where quality gates (tests, linting, type checks) need to pass before you're done
