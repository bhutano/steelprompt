<picture>
  <source media="(prefers-color-scheme: dark)" srcset="../assets/banner-dark.svg">
  <img src="../assets/banner-light.svg" alt="steelprompt" width="100%">
</picture>

<div align="center">

🌐 [English](../README.md) · [中文](README.zh.md) · [Español](README.es.md) · [PT-BR](README.pt-BR.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · **Deutsch** · [Français](README.fr.md) · [Italiano](README.it.md)

[![Version](https://img.shields.io/badge/version-0.3.0-4a9eff?style=flat-square)](https://github.com/bhutano/steelprompt/releases/tag/v0.3.0)
[![License](https://img.shields.io/badge/license-MIT-22c55e?style=flat-square)](https://github.com/bhutano/steelprompt/blob/master/LICENSE)
[![Python](https://img.shields.io/badge/python-3.8+-f59e0b?style=flat-square)](https://python.org)
[![Claude Code](https://img.shields.io/badge/claude_code-2.0.22+-a78bfa?style=flat-square)](https://claude.ai/code)

![demo](../steel_demo.gif)

**Jeder Prompt nach Anthropics 10 offiziellen Prinzipien umstrukturiert — automatisch in Claude Code, auf Abruf in Claude.ai.**

✦ Keine API-Schlüssel · ✦ Claude Code + Claude.ai Web · ✦ Keine zusätzliche Latenz · ✦ 4 wechselbare Modi

</div>

---

## Das Problem

Claude ist nur so gut wie die Prompts, die du ihm gibst. Den meisten Prompts fehlen Rollenzuweisung, strukturierter Kontext, explizite Einschränkungen, Ausgabeformat-Spezifikation und Beispiele — all das, was Anthropics eigene Richtlinien als entscheidend für die Antwortqualität bezeichnen.

Du könntest 10 Minuten damit verbringen, jeden Prompt manuell zu optimieren. Oder steelprompt verwenden — automatisch in Claude Code, auf Abruf in Claude.ai.

---

## Wie es funktioniert

steelprompt läuft auf zwei Oberflächen:

- **Claude Code (CLI)** — ein `UserPromptSubmit`-Hook fängt jeden Prompt automatisch ab, bevor Claude ihn verarbeitet.
- **Claude.ai (Web)** — füge `prompts/steelprompt-web.md` einmalig in die benutzerdefinierten Anweisungen ein und verwende dann `/sp "Prompt"` um jeden Prompt auf Abruf zu optimieren.

In beiden Fällen gilt dasselbe 3-Stufen-Entscheidungsprotokoll:

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
│  Umstrukturieren mit 10 Anthropic-Prinzipien    │
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

steelprompt erweitert das Kernframework um kontextspezifische Muster aus der vollständigen Anthropic-Dokumentation — automatisch angewendet, wenn der Prompt sie signalisiert:

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

### Motivation / WARUM

Claude verallgemeinert aus Erklärungen — steelprompt fügt den Grund hinter einer Anfrage hinzu, nicht nur die Anfrage selbst. Eine Einschränkung mit einem WARUM bleibt besser als eine bloße Regel.

| Ohne steelprompt | Mit steelprompt |
|---|---|
| `NEVER use ellipses` | `Never use ellipses — the text-to-speech engine can't pronounce them` |
| `Keep responses short` | `Keep responses under 3 sentences — output is rendered in a mobile tooltip with limited space` |

---

### Formatkontrolle (positive Formulierung)

Wenn ein Ausgabeformat angegeben ist, teilt steelprompt Claude mit, was es produzieren SOLL — nicht was es vermeiden soll. Positive Anweisungen sind zuverlässiger als negative.

```
Du tippst: "answer in plain text, no markdown"
steelprompt fügt zu <output_format> hinzu: Write in smoothly flowing prose paragraphs.
                                           No headers, bullets, or code blocks.
```

Für Ausgaben ohne Präambel:
```
steelprompt fügt hinzu: Respond directly without preamble.
                        Do not start with 'Here is...', 'Based on...', etc.
```

---

### Tool-Nutzung & parallele Aufrufe

Wenn ein Prompt für einen Agenten oder ein System mit Tools bestimmt ist, injiziert steelprompt Anleitungen zur parallelen Ausführung und zum Aktions-Standard.

**Du tippst:**
```
build an agent that searches our docs, reads the top 3 results, and summarizes them
```

**steelprompt fügt zu `<constraints>` hinzu:**
```
Make all independent tool calls in parallel — search + read all 3 results simultaneously.
Never use placeholders or guess missing parameters.
By default, implement changes rather than only suggesting them.
```

---

### Denken & Selbstprüfung

Für Aufgaben, die mehrstufiges Denken oder Überprüfung erfordern, fügt steelprompt strukturiertes Denken und eine Selbstprüfungs-Anweisung hinzu.

```
Du tippst: "calculate the optimal batch size for our embedding pipeline"

steelprompt fügt hinzu:
  Reason through the problem in <thinking> tags.
  Consider: throughput, memory, API rate limits, cost per token.
  Then provide your answer in <answer> tags.
  Before finishing, verify your recommendation satisfies all constraints above.
```

---

### Langkontext-Sortierung

Wenn die Aufgabe auf lange Dateien oder Dokumente verweist, verschiebt steelprompt diese **vor** die Aufgabenbeschreibung innerhalb von `<context>` — entsprechend Anthropics Richtlinie, dass lange Daten der Anfrage vorangestellt werden sollen (bis zu 30% Genauigkeitsgewinn bei komplexen Eingaben).

```
steelprompt fügt außerdem hinzu: Quote the relevant sections before answering.
```

| Ohne steelprompt | Mit steelprompt |
|---|---|
| `<task>` zuerst, dann Dateiinhalt | Dateiinhalt in `<context>` zuerst, dann `<task>` |
| Anfrage vor dem Beleg | Beleg vor der Anfrage |

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
| `full` (Standard) | 3-stufiges Protokoll aktiv: bypass → fragen → 10 Anthropic-Prinzipien anwenden |
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

## Auf Claude.ai (Web) verwenden

Kein Claude Code? Das gleiche Prompt-Engineering-Framework steht dir direkt auf [claude.ai](https://claude.ai) zur Verfügung — keine Installation, keine CLI.

**Einrichtung (einmalig):**
1. Öffne [claude.ai](https://claude.ai) im Browser
2. Klicke auf das Profilsymbol → **Einstellungen** → **Profil**
3. Finde **„Benutzerdefinierte Anweisungen"** (oder *„Wie soll Claude antworten?"*)
4. Kopiere den Inhalt von [`prompts/steelprompt-web.md`](https://raw.githubusercontent.com/bhutano/steelprompt/master/prompts/steelprompt-web.md) und füge ihn dort ein → Speichern

Das war's. Jeder Prompt, den du in Claude.ai eingibst, wird mit demselben 3-Stufen-Protokoll still umstrukturiert, bevor Claude antwortet.

**Manueller Auslöser:** `/sp "dein Prompt"` · **Vorschaumodus:** `/sp mode preview`

> Die Web-Version hat keine Hooks oder Tool-Aufrufe — sie läuft als System-Prompt in den nativen benutzerdefinierten Anweisungen von Claude.ai.

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

## Die 10 Anthropic-Prinzipien

steelprompt wendet diese auf jeden nicht-bypastten, klaren Prompt an:

| # | Prinzip | Angewendet als |
|---|---|---|
| 1 | **Rolle** | `You are a senior [Domäne] engineer...` |
| 2 | **Kontext + Motivation** | `<context>` — alle relevanten Hintergrundinformationen vor der Aufgabe, einschließlich des WARUM hinter der Anfrage; lange Dateien/Dokumente **vor** der Aufgabenbeschreibung platziert |
| 3 | **Aufgabe** | `<task>` — imperativischer Ton, nummerierte Schritte; explizit über Aktion vs. Vorschlag |
| 4 | **XML-Struktur** | Jeder Abschnitt in beschreibende Tags eingeschlossen (`<context>`, `<task>`, `<constraints>`, `<output_format>`, `<examples>`) für eindeutiges Parsen |
| 5 | **Einschränkungen** | `<constraints>` — was NICHT zu tun ist, Grenzen, Stilregeln; Agentensicherheits-Einschränkungen werden automatisch für destruktive Operationen eingefügt; Anti-Übereifer und Anti-Halluzination für Code-Aufgaben |
| 6 | **Ausgabeformat** | `<output_format>` — positive Formulierung (sagen, was zu produzieren IST); genaue Struktur, Länge, Abschnitte; Prefill-Zeichen für JSON/YAML/SQL; LaTeX- und Präambel-Kontrolle |
| 7 | **Denken** | `Think through this step by step` + `<thinking>/<answer>`-Tags für komplexe Aufgaben; Selbstprüfungs-Anweisung; `<thinking>` in Few-Shot-Beispielen für Agenten |
| 8 | **Beispiele** | `<examples>` — Eingabe/Ausgabe-Paare; `<bad_example>` für mehrdeutige Aufgaben hinzugefügt, um zu zeigen, was NICHT produziert werden soll; 3–5 diverse Beispiele für beste Ergebnisse |
| 9 | **Tool-Nutzung** | Anweisung zu parallelen Tool-Aufrufen; proaktiver vs. konservativer Aktions-Standard; für Prompts, die auf Agenten oder Systeme mit Tools abzielen |
| 10 | **Langkontext** | Daten vor der Anfrage platziert; Multi-Dokument-XML-Einbettung; Zitat-vor-Antwort-Anweisung; für Prompts, die auf große Dateien oder Dokumente verweisen |

Quelle: [Anthropic Prompting Best Practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices)

---

## Mitwirken

steelprompt verbessert sich, wenn Menschen es nutzen und berichten, was nicht funktioniert.

**Einen Bug oder unerwartetes Verhalten gefunden?** [Issue erstellen](https://github.com/bhutano/steelprompt/issues) — beschreibe den Prompt, den du eingegeben hast, und was du bekommen hast im Vergleich zu dem, was du erwartet hast.

**Eine Idee?** Erstelle ein Issue mit dem Label `enhancement`. Vorschläge für neue Muster, bessere Beispiele oder Randfälle, die das Framework übersieht, sind alle willkommen.

**Code beitragen?** Siehe [CONTRIBUTING.md](../CONTRIBUTING.md) für Grundregeln und Testschritte.

---

## Danksagungen

Architektur inspiriert von [severity1/claude-code-prompt-improver](https://github.com/severity1/claude-code-prompt-improver). Kein gemeinsamer Code.

## Lizenz

MIT
