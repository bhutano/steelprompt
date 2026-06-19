# Changelog

All notable changes to steelprompt are documented here.

---

## [0.3.0] — 2026-06-19

### Added
- **10 Anthropic principles** (up from 7) — now covers 100% of Anthropic's official prompt engineering docs
- **Principle 4 — XML Structure**: explicit principle for wrapping sections in descriptive XML tags
- **Principle 9 — Tool use**: parallel tool calling instruction, proactive vs. conservative action default
- **Principle 10 — Long context**: data-before-query ordering, multi-document XML wrapping, quote-before-answer
- **Principle 2 expanded**: context now includes motivation/WHY behind the request
- **Principle 5 expanded**: anti-overeagerness, anti-hallucination, anti-test-hardcoding constraints
- **Principle 6 expanded**: positive format framing, LaTeX control, no-prefill guidance
- **Principle 7 expanded**: adaptive thinking, effort hints, self-check, `<thinking>` in few-shot examples
- **Agentic system prompts section** in SKILL.md: autonomy/safety, long-horizon, state management, subagent orchestration
- **Model-specific notes** in SKILL.md: Claude Fable 5 and Claude Opus 4.8 guidance with prompt snippets
- **Raw docs** (gitignored): `claude-prompting-best-practices.md`, `prompting-claude-fable-5.md`, `prompting-claude-opus-4-8.md`
- **README Advanced Patterns**: 5 new sections (Motivation/WHY, Format control, Tool use & parallel calling, Thinking & self-check, Long context ordering)

### Changed
- **Tier 2 philosophy**: ask only when answer fundamentally changes the prompt AND cannot be inferred; single plain-language question; no prompt engineering jargon in questions
- plugin.json description updated to reflect 10 principles
- README tagline, flow diagram, modes table, principles table, source link all updated to v0.3.0

---

## [0.2.0] — 2026-06-17

### Added
- **Dual-mode support**: steelprompt now runs on both Claude Code (CLI hook) and Claude.ai (web custom instructions)
- `prompts/steelprompt-web.md` — pure copy-paste prompt for Claude.ai Custom Instructions
- Web section in all 9 language READMEs (en, it, zh, es, pt-BR, de, fr, ja, ko)
- `steel_demo.gif` added to all READMEs
- Raw GitHub URL for `steelprompt-web.md` (avoids markdown rendering on raw link)

### Changed
- README intro updated with dual-mode framing
- Setup block removed from `steelprompt-web.md` (file is now pure prompt, setup is in README only)

---

## [0.1.0] — 2026-06-12

### Added
- Initial release
- `UserPromptSubmit` hook for Claude Code — intercepts every prompt automatically
- 3-tier decision protocol: Bypass → Ask → Apply
- 7 Anthropic prompt engineering principles applied silently
- 4 switchable modes: `full`, `preview`, `ask-only`, `off`
- Manual `/steelprompt` skill with preview and Run/Edit/Cancel flow
- 5 advanced patterns: chain detection, agentic safety, long context ordering, prefill for critical formats, negative examples
- 9 language READMEs (en, it, zh, es, pt-BR, de, fr, ja, ko)
- MIT license
