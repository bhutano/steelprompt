<picture>
  <source media="(prefers-color-scheme: dark)" srcset="../assets/banner-dark.svg">
  <img src="../assets/banner-light.svg" alt="steelprompt" width="100%">
</picture>

<div align="center">

🌐 [English](../README.md) · [中文](README.zh.md) · [Español](README.es.md) · [PT-BR](README.pt-BR.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · **Deutsch** · [Français](README.fr.md) · [Italiano](README.it.md)

[![Version](https://img.shields.io/badge/version-0.2.0-4a9eff?style=flat-square)](https://github.com/bhutano/steelprompt)
[![License](https://img.shields.io/badge/license-MIT-22c55e?style=flat-square)](https://github.com/bhutano/steelprompt/blob/master/LICENSE)
[![Python](https://img.shields.io/badge/python-3.8+-f59e0b?style=flat-square)](https://python.org)
[![Claude Code](https://img.shields.io/badge/claude_code-2.0.22+-a78bfa?style=flat-square)](https://claude.ai/code)

![demo](../steel_demo.gif)

**Jeder Prompt, den du eingibst, wird still nach Anthropics 7 offiziellen Prompt-Engineering-Prinzipien umstrukturiert, bevor Claude ihn sieht.**

✦ Kein Setup · ✦ Keine API-Schlüssel · ✦ Läuft inline · ✦ 4 wechselbare Modi

</div>

---

## Das Problem

Claude Code ist nur so gut wie die Prompts, die du ihm gibst. Den meisten Prompts fehlen Rollenzuweisung, strukturierter Kontext, explizite Einschränkungen, Ausgabeformat-Spezifikation und Beispiele — all das, was Anthropics eigene Richtlinien als entscheidend für die Antwortqualität bezeichnen.

Du könntest 10 Minuten damit verbringen, jeden Prompt manuell zu optimieren. Oder steelprompt installieren.

---

## Wie es funktioniert

steelprompt fängt jeden Prompt über einen `UserPromptSubmit`-Hook ab und wendet ein 3-stufiges Entscheidungsprotokoll an, bevor Claude ihn verarbeitet:

```
Dein Prompt
    │
    ▼
┌─────────────────────────────────────────────────┐
│  STUFE 1 — BYPASS                               │
│  Slash-Befehle · < 5 Wörter · atomare Aufgaben  │
│  → Unverändert weiterleiten                     │
└─────────────────────────────────────────────────┘
    │ nicht bypasst
    ▼
┌─────────────────────────────────────────────────┐
│  STUFE 2 — FRAGEN                               │
│  Kritische Infos fehlen?                        │
│  → AskUserQuestion (1–2 gezielte Fragen)        │
└─────────────────────────────────────────────────┘
    │ Prompt ist klar
    ▼
┌─────────────────────────────────────────────────┐
│  STUFE 3 — FRAMEWORK ANWENDEN      ← Standard   │
│  Umstrukturieren mit 7 Anthropic-Prinzipien     │
│  still, bevor Claude antwortet                  │
└─────────────────────────────────────────────────┘
```

Keine externen API-Aufrufe. Claude strukturiert inline während der normalen Inferenz um — null zusätzliche Latenz, null extra abgerechnete Token.

---

## Stufe 3 in Aktion

Dies ist das Herzstück von steelprompt. Jeder klare, nicht-atomare Prompt wird automatisch durchgeleitet.

**Du tippst:**
```
add rate limiting to the auth endpoints
```

**Was steelprompt intern einfügt** (im `preview`-Modus vor der Ausführung sichtbar):
```
You are a senior backend security engineer.

<context>
Project: Express.js API with JWT authentication
Endpoints affected: POST /auth/login, POST /auth/refresh, POST /auth/register
Environment: Node.js 20, existing middleware stack in src/middleware/
Known constraints from conversation: Redis already in use for session storage
</context>

<task>
Implement rate limiting on authentication endpoints:
1. Add per-IP rate limiting: max 5 requests/minute on /login and /register
2. Add per-user rate limiting: max 20 requests/hour on /refresh
3. Return 429 with Retry-After header on limit exceeded
4. Do not affect non-auth endpoints
</task>

<constraints>
- Reuse existing Redis connection, do not introduce a new client
- Do not modify JWT validation logic
- Rate limit state must survive server restarts
- Follow existing middleware patterns in src/middleware/
</constraints>

<output_format>
1. New middleware file with implementation
2. Diff showing changes to auth routes
3. Two Jest test cases: limit hit + normal flow
</output_format>

Think through this step by step before answering.
```

**Was Claude produziert:** eine vollständige, produktionsreife Implementierung mit Tests — keine allgemeine Übersicht über Rate-Limiting-Optionen.

---

## Erweiterte Muster

steelprompt erweitert die 7 Kernprinzipien um 5 kontextspezifische Muster aus der vollständigen Anthropic-Dokumentation — automatisch angewendet, wenn der Prompt sie signalisiert:

### Ketten-Erkennung

Wenn eine Aufgabe mehrere aufeinanderfolgende Operationen umfasst, erkennt steelprompt die Kette und zeigt einen Plan vor der Ausführung.

**Du tippst:**
```
refactor auth.py, add tests, update the documentation
```

**steelprompt erkennt eine mehrstufige Kette und hält für eine Bestätigung an:**
```
Chain detected (3 prompts):
→ Prompt 1: Refactor auth.py following SOLID principles
             Produces: refactored auth.py
→ Prompt 2: Write pytest tests for the refactored code
             Uses: output of Prompt 1
→ Prompt 3: Update docs/auth.md
             Uses: output of Prompt 1 + 2
```

Dann fragt es: **Sequenziell ausführen · Als einzelnen Prompt senden · Abbrechen**

---

### Agentensicherheit

Wenn eine Aufgabe irreversible Operationen beinhaltet, fügt steelprompt automatisch Sicherheitseinschränkungen ein.

**Du tippst:**
```
delete all obsolete records from the production database
```

**steelprompt fügt automatisch zu `<constraints>` hinzu:**
```
- Show COUNT of affected rows before executing DELETE
- Scope: only rows matching the explicit filter condition
- Require explicit confirmation before the irreversible action
- Do not touch tables or columns not explicitly mentioned
```

---

### Langkontext-Sortierung

Wenn die Aufgabe auf lange Dateien oder Dokumente verweist, verschiebt steelprompt diese **vor** die Aufgabenbeschreibung innerhalb von `<context>` — entsprechend Anthropics Richtlinie, dass lange Daten der Anfrage vorangestellt werden sollen.

| Ohne steelprompt | Mit steelprompt |
|---|---|
| `<task>` zuerst, dann Dateiinhalt | Dateiinhalt in `<context>` zuerst, dann `<task>` |

---

### Prefill für kritische Formate

Wenn das Ausgabeformat streng kritisch ist (JSON, YAML, SQL), fügt steelprompt einen Prefill-Anker hinzu: die Antwort mit dem öffnenden Zeichen (`{`, `---`, `SELECT`) zu beginnen, um Claude vom ersten Token an auf das korrekte Format festzulegen.

```
Du tippst: "parse this config and return JSON"
steelprompt fügt zu <output_format> hinzu: begin response with {
```

---

### Negative Beispiele

Für mehrdeutige Aufgaben, bei denen das korrekte Ausgabeformat nicht offensichtlich ist, generiert steelprompt `<bad_example>`-Blöcke neben `<example>`-Blöcken — das Zeigen, was **nicht** produziert werden soll, reduziert Halluzinationen bei formatsensitiven Aufgaben.

```
<example>
Input: user object → Output: {id, name, email} (no password field)
</example>
<bad_example>
Input: user object → Output: {id, name, email, password_hash} ← never expose this
</bad_example>
```

---

## Stufe 2 in Aktion

Wenn kritische Informationen fehlen, fragt steelprompt zuerst, bevor es rät.

| Du tippst | steelprompt fragt |
|---|---|
| `"improve the code"` | Welche Datei? Welche Art von Verbesserung — Lesbarkeit, Performance, Korrektheit? |
| `"fix the bug"` | Welcher Bug? Reproduktionsschritte oder Fehlermeldung? |
| `"refactor auth"` | Was ist das Ziel? Ist das eine öffentliche API oder intern? Soll das Verhalten identisch bleiben? |
| `"change icon color to red"` | *(Stufe 1 — atomar, direkte Antwort)* |

---

## Modi

| Modus | Verhalten |
|---|---|
| `full` (Standard) | 3-stufiges Protokoll aktiv: bypass → fragen → 7 Anthropic-Prinzipien anwenden |
| `preview` | Zeigt den optimierten Prompt vor der Ausführung — überprüfen, bearbeiten oder abbrechen |
| `ask-only` | Stellt nur Klärungsfragen; wendet das vollständige Framework nicht an |
| `off` | Hook vollständig deaktiviert |

```bash
/steelprompt mode full
/steelprompt mode preview
/steelprompt mode ask-only
/steelprompt mode off
```

Konfiguration wird pro Benutzer in `$CLAUDE_PLUGIN_ROOT/.steelpromptrc` gespeichert. Keine Konfiguration = Standard ist `full`.

---

## Vorschaumodus

Möchtest du den optimierten Prompt vor der Ausführung sehen? Wechsle zu `preview`:

```
/steelprompt mode preview
```

Dann gib einen beliebigen Prompt normal ein. Anstatt still zu antworten, zeigt Claude dir den umstrukturierten Prompt und fragt: **Ausführen · Bearbeiten · Abbrechen**.

---

## Manueller Skill: `/steelprompt`

Verwende ihn, um jeden Prompt manuell zu optimieren — oder um Modi zu wechseln.

```
/steelprompt "migrate the users table to add soft deletes"
```

**Ausgabe:**
```
You are a senior database engineer specializing in PostgreSQL migrations.

<context>
Project: Rails 7 application with PostgreSQL
Table: users (id, email, created_at, updated_at)
Migration system: ActiveRecord
Known constraints: zero-downtime deployment required, table has ~2M rows
</context>

<task>
Add soft delete support to the users table:
1. Add deleted_at timestamp column (nullable, default null)
2. Add index on deleted_at for query performance
3. Update User model with default_scope excluding deleted records
4. Add User#soft_delete and User#restore methods
</task>

<examples>
<example>
Input: User.destroy(42)
Output (after): sets deleted_at = now(), does not DELETE the row
</example>
<example>
Input: User.all
Output (after): returns only records where deleted_at IS NULL
</example>
</examples>

<constraints>
- Do not use a gem (acts_as_paranoid, discard) — implement directly
- Migration must be reversible (down method required)
- Do not alter existing indexes or foreign keys
- Keep existing hard-delete path available via User.unscoped.destroy
</constraints>

<output_format>
1. Migration file with up/down
2. Model changes (3–5 lines max)
3. Two unit tests: soft delete sets column, default scope excludes deleted
</output_format>

Think through this step by step before answering.
```

---

## Installation

```bash
claude plugin marketplace add bhutano/bhutano-marketplace
claude plugin install steelprompt
```

**Voraussetzungen:** Claude Code 2.0.22+ · Python 3.8+

```bash
claude --version   # Claude Code Version prüfen
python --version   # Python Version prüfen
```

---

## Bypass

steelprompt fängt diese niemals ab:

| Präfix | Verhalten |
|---|---|
| `/befehl` | Slash-Befehle werden unverändert weitergeleitet |
| `* prompt` | Expliziter Bypass — diesen Prompt überspringen |
| `# prompt` | Expliziter Bypass — diesen Prompt überspringen |
| < 5 Wörter | Wird als atomar behandelt — direkte Antwort |

---

## Die 7 Anthropic-Prinzipien

steelprompt wendet diese auf jeden nicht-bypastten, klaren Prompt an:

| # | Prinzip | Angewendet als |
|---|---|---|
| 1 | **Rolle** | `You are a senior [Domäne] engineer...` |
| 2 | **Kontext** | `<context>` — alle relevanten Hintergrundinformationen vor der Aufgabe; lange Dateien/Dokumente in `<context>` **vor** der Aufgabenbeschreibung |
| 3 | **Aufgabe** | `<task>` — imperativischer Ton, nummerierte Schritte für mehrstufige Arbeit |
| 4 | **Einschränkungen** | `<constraints>` — was NICHT zu tun ist, Grenzen, Stilregeln; Agentensicherheits-Einschränkungen werden automatisch für destruktive Operationen eingefügt |
| 5 | **Ausgabeformat** | `<output_format>` — genaue Struktur, Länge, Abschnitte; Prefill-Zeichen für JSON/YAML/SQL verankert |
| 6 | **Gedankengang** | `Think through this step by step before answering` |
| 7 | **Beispiele** | `<examples>` — Eingabe/Ausgabe-Paare; `<bad_example>` für mehrdeutige Aufgaben hinzugefügt, um zu zeigen, was NICHT produziert werden soll |

Quelle: [Anthropic Prompt Engineering Docs](https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/overview)

---

## Danksagungen

Architektur inspiriert von [severity1/claude-code-prompt-improver](https://github.com/severity1/claude-code-prompt-improver). Kein gemeinsamer Code.

## Lizenz

MIT
