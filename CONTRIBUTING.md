# Contributing to steelprompt

## Ways to contribute

- **Bug reports** — open an issue with the prompt that behaved unexpectedly and what you got vs. what you expected
- **New patterns** — if Anthropic's docs describe a technique not yet covered, open an issue or PR
- **Translations** — new language READMEs are welcome; follow the structure of `docs/README.it.md`
- **Prompt improvements** — if a principle's implementation can be made more accurate or effective, open a PR with before/after examples

## Ground rules

- Changes to `prompts/steelprompt-full.md`, `prompts/steelprompt-web.md`, and `skills/steelprompt/SKILL.md` must stay in sync — the same principles apply across all three files
- Tier 2 (Ask) threshold stays high: the framework should do the work, not the user
- Questions to the user must be plain language — no prompt engineering terminology
- Principle additions must be traceable to Anthropic's official docs (link in PR)
- `raw/` is gitignored — local reference only, not committed

## Testing a change

1. Install locally: `claude plugin install --local .`
2. Switch to preview mode: `/steelprompt mode preview`
3. Test with 3–5 representative prompts across Tier 1, Tier 2, and Tier 3
4. Verify chain detection still triggers correctly
5. Verify destructive operation safety constraints still inject

## Commit style

Conventional Commits: `feat:`, `fix:`, `docs:`, `refactor:`

Keep subject under 50 chars. Body only when the why isn't obvious from the diff.
