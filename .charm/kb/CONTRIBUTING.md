# Contributing to the Knowledge Base

This is a **durable** knowledge base -- it survives between charm runs and across sessions.
Keep it accurate: a note the next agent trusts but that lies is worse than no note at all.

## How to add a note

1. Pick the right root: `architecture`, `decisions`, `conventions`, `gotchas`, or `domain`.
   Only add a new root directory if nothing genuinely fits -- and if you do, give it an
   `_index.md` and add a row to `INDEX.md`.
2. Write **one concept per note** (atomic). Filename is lowercase-kebab (`spawn-model.md`);
   decisions use a zero-padded numeric prefix (`0001-single-git-tree.md`).
3. Add the frontmatter below. `summary` is the most important field -- one self-contained
   sentence a reader can judge *without opening the note*.
4. Add a row for the note in that root's `_index.md`, and bump the count in `INDEX.md`.

## Frontmatter schema

```yaml
---
id: <kebab-slug>          # matches the filename without .md
root: architecture        # architecture | decisions | conventions | gotchas | domain
type: architecture | decision | convention | gotcha | domain
status: current | stale | superseded
summary: "One self-contained sentence -- the navigation surface."
related:                  # KB-relative paths, no .md extension; optional
  - decisions/0001-single-git-tree
created: YYYY-MM-DD        # set once, immutable
updated: YYYY-MM-DD
---
```

## Updating notes

- Reversed a decision? Set the old note to `status: superseded`, point its `related` at the
  replacement -- do **not** delete it (keep the audit trail).
- Suspect a note is out of date but haven't reverified? Mark it `status: stale`.
- Any edit: bump `updated`.

## Links

Use ordinary markdown relative links in note bodies, and KB-relative paths in `related`.
Not Obsidian `[[wikilinks]]` -- this KB is read with file tools, not a graph UI.

## Navigation (how the KB is meant to be read)

Read `INDEX.md` -> the relevant root's `_index.md` -> only the 1-2 notes whose summary
matches the task. Never bulk-read the KB. If you can't find what you need from summaries,
the summaries need fixing.
