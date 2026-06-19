<picture>
  <source media="(prefers-color-scheme: dark)" srcset="../assets/banner-dark.svg">
  <img src="../assets/banner-light.svg" alt="steelprompt" width="100%">
</picture>

<div align="center">

🌐 [English](../README.md) · [中文](README.zh.md) · [Español](README.es.md) · [PT-BR](README.pt-BR.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Deutsch](README.de.md) · **Français** · [Italiano](README.it.md)

[![Version](https://img.shields.io/badge/version-0.3.0-4a9eff?style=flat-square)](https://github.com/bhutano/steelprompt/releases/tag/v0.3.0)
[![License](https://img.shields.io/badge/license-MIT-22c55e?style=flat-square)](https://github.com/bhutano/steelprompt/blob/master/LICENSE)
[![Python](https://img.shields.io/badge/python-3.8+-f59e0b?style=flat-square)](https://python.org)
[![Claude Code](https://img.shields.io/badge/claude_code-2.0.22+-a78bfa?style=flat-square)](https://claude.ai/code)

![demo](../steel_demo.gif)

**Chaque prompt restructuré selon les 10 principes officiels d'Anthropic — automatiquement dans Claude Code, à la demande dans Claude.ai.**

✦ Aucune clé API · ✦ Claude Code + Claude.ai web · ✦ Zéro latence supplémentaire · ✦ 4 modes commutables

</div>

---

## Le problème

Claude Code n'est efficace qu'à la hauteur des prompts que vous lui donnez. La plupart des prompts sont dépourvus d'attribution de rôle, de contexte structuré, de contraintes explicites, de spécification du format de sortie et d'exemples — autant d'éléments que les directives officielles d'Anthropic indiquent comme déterminants pour la qualité des réponses.

Vous pourriez passer 10 minutes à peaufiner chaque prompt manuellement. Ou utiliser steelprompt — automatique dans Claude Code, à la demande dans Claude.ai.

---

## Comment ça fonctionne

steelprompt fonctionne sur deux surfaces :

- **Claude Code (CLI)** — un hook `UserPromptSubmit` intercepte chaque prompt automatiquement avant que Claude ne le traite.
- **Claude.ai (web)** — collez `prompts/steelprompt-web.md` dans les Instructions personnalisées une seule fois, puis utilisez `/sp "prompt"` pour optimiser n'importe quel prompt à la demande.

Dans les deux cas, le même protocole de décision à 3 niveaux s'applique :

```
Votre prompt
    │
    ▼
┌─────────────────────────────────────────────────┐
│  NIVEAU 1 — BYPASS                              │
│  Commandes slash · < 5 mots · tâches atomiques  │
│  → Passer sans modification                     │
└─────────────────────────────────────────────────┘
    │ non contourné
    ▼
┌─────────────────────────────────────────────────┐
│  NIVEAU 2 — DEMANDER                            │
│  Informations critiques manquantes ?            │
│  → AskUserQuestion (1–2 questions ciblées)      │
└─────────────────────────────────────────────────┘
    │ prompt clair
    ▼
┌─────────────────────────────────────────────────┐
│  NIVEAU 3 — APPLIQUER LE FRAMEWORK  ← défaut    │
│  Restructurer avec 10 principes Anthropic       │
│  silencieusement, avant que Claude réponde      │
└─────────────────────────────────────────────────┘
```

Aucun appel API externe. Claude restructure inline pendant son inférence normale — zéro latence supplémentaire, zéro token facturé en plus.

---

## Niveau 3 en action

C'est le cœur de steelprompt. Chaque prompt clair et non atomique le traverse automatiquement.

**Vous saisissez :**
```
add rate limiting to the auth endpoints
```

**Ce que steelprompt injecte en interne** (visible en mode `preview` avant l'exécution) :
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

**Ce que Claude produit :** une implémentation complète et prête pour la production avec des tests — pas un aperçu générique des options de rate limiting.

---

## Modèles avancés

steelprompt étend le framework de base avec des modèles spécifiques au contexte tirés de la documentation Anthropic complète — appliqués automatiquement lorsque le prompt les signale :

### Détection de chaîne

Lorsqu'une tâche couvre plusieurs opérations séquentielles, steelprompt détecte la chaîne et affiche un plan avant d'exécuter.

**Vous saisissez :**
```
refactor auth.py, add tests, update the documentation
```

**steelprompt détecte une chaîne multi-étapes et marque une pause pour confirmation :**
```
Chain detected (3 prompts):
→ Prompt 1: Refactor auth.py following SOLID principles
             Produces: refactored auth.py
→ Prompt 2: Write pytest tests for the refactored code
             Uses: output of Prompt 1
→ Prompt 3: Update docs/auth.md
             Uses: output of Prompt 1 + 2
```

Puis demande : **Run in sequence · Run as single prompt · Cancel**

---

### Sécurité agentique

Lorsqu'une tâche implique des opérations irréversibles, steelprompt injecte automatiquement des contraintes de sécurité.

**Vous saisissez :**
```
delete all obsolete records from the production database
```

**steelprompt ajoute automatiquement à `<constraints>` :**
```
- Show COUNT of affected rows before executing DELETE
- Scope: only rows matching the explicit filter condition
- Require explicit confirmation before the irreversible action
- Do not touch tables or columns not explicitly mentioned
```

---

### Préfill pour les formats critiques

Lorsque le format de sortie est rigoureusement critique (JSON, YAML, SQL), steelprompt ajoute une ancre de préfill : commencer la réponse par le caractère d'ouverture (`{`, `---`, `SELECT`) pour verrouiller Claude dans le bon format dès le premier token.

```
Vous saisissez : "parse this config and return JSON"
steelprompt ajoute à <output_format>: begin response with {
```

---

### Exemples négatifs

Pour les tâches ambiguës où le format de sortie correct n'est pas évident, steelprompt génère des blocs `<bad_example>` aux côtés des blocs `<example>` — montrer ce qu'il ne faut **pas** produire réduit les hallucinations sur les tâches sensibles au format.

```
<example>
Input: user object → Output: {id, name, email} (no password field)
</example>
<bad_example>
Input: user object → Output: {id, name, email, password_hash} ← never expose this
</bad_example>
```

---

### Motivation / POURQUOI

Claude généralise à partir des explications — steelprompt ajoute la raison derrière une demande, pas seulement la demande elle-même. Une contrainte avec un POURQUOI s'ancre mieux qu'une règle brute.

| Sans steelprompt | Avec steelprompt |
|---|---|
| `NEVER use ellipses` | `Never use ellipses — the text-to-speech engine can't pronounce them` |
| `Keep responses short` | `Keep responses under 3 sentences — output is rendered in a mobile tooltip with limited space` |

---

### Contrôle du format (formulation positive)

Lorsqu'un format de sortie est spécifié, steelprompt indique à Claude ce qu'il doit produire — pas ce qu'il doit éviter. Les instructions positives sont plus fiables que les négatives.

```
Vous saisissez : "answer in plain text, no markdown"
steelprompt ajoute à <output_format>: Write in smoothly flowing prose paragraphs.
                                      No headers, bullets, or code blocks.
```

Pour une sortie sans préambule :
```
steelprompt ajoute : Respond directly without preamble.
                     Do not start with 'Here is...', 'Based on...', etc.
```

---

### Utilisation d'outils & appels parallèles

Lorsqu'un prompt cible un agent ou un système avec des outils, steelprompt injecte des instructions d'exécution parallèle et de comportement par défaut.

**Vous saisissez :**
```
build an agent that searches our docs, reads the top 3 results, and summarizes them
```

**steelprompt ajoute à `<constraints>` :**
```
Make all independent tool calls in parallel — search + read all 3 results simultaneously.
Never use placeholders or guess missing parameters.
By default, implement changes rather than only suggesting them.
```

---

### Réflexion & auto-vérification

Pour les tâches nécessitant un raisonnement multi-étapes ou une vérification, steelprompt ajoute une réflexion structurée et une instruction d'auto-vérification.

```
Vous saisissez : "calculate the optimal batch size for our embedding pipeline"

steelprompt ajoute :
  Reason through the problem in <thinking> tags.
  Consider: throughput, memory, API rate limits, cost per token.
  Then provide your answer in <answer> tags.
  Before finishing, verify your recommendation satisfies all constraints above.
```

---

### Ordonnancement de contexte long

Lorsque la tâche référence de longs fichiers ou documents, steelprompt les déplace **avant** la description de la tâche dans `<context>` — conformément aux directives d'Anthropic stipulant que les données longues doivent précéder la requête (jusqu'à 30% de gain de précision sur les entrées complexes).

```
steelprompt ajoute également : Quote the relevant sections before answering.
```

| Sans steelprompt | Avec steelprompt |
|---|---|
| `<task>` en premier, puis le contenu du fichier | contenu du fichier dans `<context>` en premier, puis `<task>` |
| Requête avant les données | Données avant la requête |

---

## Niveau 2 en action

Lorsque des informations critiques manquent, steelprompt demande avant de deviner.

| Vous saisissez | steelprompt demande |
|---|---|
| `"improve the code"` | Quel fichier ? Quel type d'amélioration — lisibilité, performance, exactitude ? |
| `"fix the bug"` | Quel bug ? Des étapes de reproduction ou un message d'erreur ? |
| `"refactor auth"` | Quel est l'objectif ? Est-ce public via API ou interne ? Le comportement doit-il rester identique ? |
| `"change icon color to red"` | *(Niveau 1 — atomique, réponse directe)* |

---

## Modes

| Mode | Comportement |
|---|---|
| `full` (défaut) | Protocole 3 niveaux actif : bypass → demander → appliquer les 10 principes Anthropic |
| `preview` | Affiche le prompt restructuré avant l'exécution — réviser, modifier ou annuler |
| `ask-only` | Pose uniquement des questions de clarification ; n'applique pas le framework complet |
| `off` | Hook complètement désactivé |

```bash
/steelprompt mode full
/steelprompt mode preview
/steelprompt mode ask-only
/steelprompt mode off
```

Configuration enregistrée par utilisateur dans `$CLAUDE_PLUGIN_ROOT/.steelpromptrc`. Zéro config = défaut `full`.

---

## Mode aperçu

Vous souhaitez voir le prompt restructuré avant qu'il ne s'exécute ? Passez en mode `preview` :

```
/steelprompt mode preview
```

Saisissez ensuite n'importe quel prompt normalement. Au lieu de répondre silencieusement, Claude vous montrera le prompt restructuré et demandera : **Run · Edit · Cancel**.

---

## Skill manuelle : `/steelprompt`

Utilisez-la pour restructurer manuellement n'importe quel prompt — ou pour changer de mode.

```
/steelprompt "migrate the users table to add soft deletes"
```

**Sortie :**
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

**Prérequis :** Claude Code 2.0.22+ · Python 3.8+

```bash
claude --version   # vérifier la version de Claude Code
python --version   # vérifier la version de Python
```

---

## Utiliser sur Claude.ai (web)

Vous n'utilisez pas Claude Code ? Vous pouvez obtenir le même framework d'ingénierie de prompts directement sur [claude.ai](https://claude.ai) — sans installation, sans CLI.

**Configuration (une seule fois) :**
1. Ouvrez [claude.ai](https://claude.ai) dans votre navigateur
2. Cliquez sur l'icône de profil → **Paramètres** → **Profil**
3. Trouvez **« Instructions personnalisées »** (ou *« Comment souhaitez-vous que Claude réponde ? »*)
4. Copiez le contenu de [`prompts/steelprompt-web.md`](https://raw.githubusercontent.com/bhutano/steelprompt/master/prompts/steelprompt-web.md) et collez-le là → Enregistrer

C'est tout. Chaque prompt que vous écrivez dans Claude.ai sera silencieusement restructuré selon le même protocole à 3 niveaux avant que Claude ne réponde.

**Déclencheur manuel :** `/sp "votre prompt"` · **Mode aperçu :** `/sp mode preview`

> La version web n'a pas de hooks ni d'appels d'outils — elle fonctionne comme un system prompt dans les instructions personnalisées natives de Claude.ai.

---

## Contournement

steelprompt n'intercepte jamais ces éléments :

| Préfixe | Comportement |
|---|---|
| `/commande` | Les commandes slash passent sans modification |
| `* prompt` | Contournement explicite — ignorer ce prompt |
| `# prompt` | Contournement explicite — ignorer ce prompt |
| < 5 mots | Traité comme atomique — réponse directe |

---

## Les 10 principes Anthropic

steelprompt les applique à chaque prompt clair et non contourné :

| # | Principe | Appliqué comme |
|---|---|---|
| 1 | **Rôle** | `You are a senior [domaine] engineer...` |
| 2 | **Contexte + Motivation** | `<context>` — tout le contexte pertinent avant la tâche, incluant le POURQUOI derrière la demande ; longs fichiers/documents placés **avant** la description de la tâche |
| 3 | **Tâche** | `<task>` — mode impératif, étapes numérotées ; explicite sur l'action vs. la suggestion |
| 4 | **Structure XML** | Chaque section encapsulée dans des balises descriptives (`<context>`, `<task>`, `<constraints>`, `<output_format>`, `<examples>`) pour un parsing non ambigu |
| 5 | **Contraintes** | `<constraints>` — ce qu'il NE FAUT PAS faire, limites, règles de style ; contraintes de sécurité agentique injectées automatiquement pour les opérations destructives ; anti-excès et anti-hallucination pour les tâches de code |
| 6 | **Format de sortie** | `<output_format>` — formulation positive (indiquer ce qu'il FAUT produire) ; structure exacte, longueur, sections ; caractère de préfill pour JSON/YAML/SQL ; contrôle LaTeX et préambule |
| 7 | **Réflexion** | `Think through this step by step` + balises `<thinking>/<answer>` pour les tâches complexes ; instruction d'auto-vérification ; `<thinking>` dans les exemples few-shot pour les agents |
| 8 | **Exemples** | `<examples>` — paires entrée/sortie ; `<bad_example>` ajouté pour les tâches ambiguës afin de montrer ce qu'il NE FAUT PAS produire ; 3–5 exemples variés pour de meilleurs résultats |
| 9 | **Utilisation d'outils** | Instruction d'appels d'outils parallèles ; comportement par défaut proactif vs. conservateur ; pour les prompts ciblant des agents ou systèmes avec des outils |
| 10 | **Contexte long** | Données placées avant la requête ; encapsulation XML multi-documents ; instruction de citation avant réponse ; pour les prompts référençant de grands fichiers ou documents |

Source : [Anthropic Prompting Best Practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices)

---

## Contribuer

steelprompt s'améliore quand les gens l'utilisent et signalent ce qui ne fonctionne pas.

**Vous avez trouvé un bug ou un comportement inattendu ?** [Ouvrez un ticket](https://github.com/bhutano/steelprompt/issues) — décrivez le prompt que vous avez saisi et ce que vous avez obtenu vs. ce que vous attendiez.

**Vous avez une idée ?** Ouvrez un ticket avec le label `enhancement`. Les suggestions de nouveaux modèles, de meilleurs exemples ou de cas limites que le framework manque sont toutes les bienvenues.

**Vous souhaitez contribuer du code ?** Consultez [CONTRIBUTING.md](../CONTRIBUTING.md) pour les règles de base et les étapes de test.

---

## Remerciements

Architecture inspirée de [severity1/claude-code-prompt-improver](https://github.com/severity1/claude-code-prompt-improver). Aucun code partagé.

## Licence

MIT
