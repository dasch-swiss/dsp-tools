Fixes DEV-

<!--
This repo squash-merges: the PR title becomes the commit subject on `main`.
Write the title as a Conventional Commit (`type(scope): subject`); the "Check PR Title" workflow enforces it.
Unless the type is chore, refactor, docs, test or fix, end the title in the Linear ticket: `(DEV-1234)`.
Describe the code and the diff, not the history of the branch.
-->

## Motivation

<!-- Why this change is necessary. What problem it solves for users or developers. -->

## Summary

<!-- What the PR changes, and why it takes this form. Name rejected alternatives if a reviewer would ask. -->

## Test Plan

<!-- How the change is verified: tests added or changed, commands run, manual checks. -->

## Checklist

- [ ] The items in `REVIEW.md` that apply to this change are satisfied
- [ ] Feature work: the blast radius is mapped (see the "dsp-tools subsystem inventory" in `CONVENTIONS.md`)
- [ ] User-facing behaviour changed: the docs under `docs/` are updated
