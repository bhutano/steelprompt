<picture>
  <source media="(prefers-color-scheme: dark)" srcset="../assets/banner-dark.svg">
  <img src="../assets/banner-light.svg" alt="steelprompt" width="100%">
</picture>

<div align="center">

🌐 [English](../README.md) · [中文](README.zh.md) · [Español](README.es.md) · [PT-BR](README.pt-BR.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Deutsch](README.de.md) · **Français** · [Italiano](README.it.md)

[![Version](https://img.shields.io/badge/version-0.2.0-4a9eff?style=flat-square)](https://github.com/bhutano/steelprompt)
[![License](https://img.shields.io/badge/license-MIT-22c55e?style=flat-square)](https://github.com/bhutano/steelprompt/blob/master/LICENSE)
[![Python](https://img.shields.io/badge/python-3.8+-f59e0b?style=flat-square)](https://python.org)
[![Claude Code](https://img.shields.io/badge/claude_code-2.0.22+-a78bfa?style=flat-square)](https://claude.ai/code)

**Chaque prompt que vous saisissez est silencieusement restructuré selon les 7 principes officiels de prompt engineering d'Anthropic, avant que Claude ne le voie.**

✦ Zéro configuration · ✦ Aucune clé API · ✦ Exécution inline · ✦ 4 modes commutables

</div>

---

## Le problème

Claude Code n'est efficace qu'à la hauteur des prompts que vous lui donnez. La plupart des prompts sont dépourvus d'attribution de rôle, de contexte structuré, de contraintes explicites, de spécification du format de sortie et d'exemples — autant d'éléments que les directives officielles d'Anthropic indiquent comme déterminants pour la qualité des réponses.

Vous pourriez passer 10 minutes à peaufiner chaque prompt manuellement. Ou installer steelprompt.

---

## Comment ça fonctionne

steelprompt intercepte chaque prompt via un hook `UserPromptSubmit` et applique un protocole de décision à 3 niveaux avant que Claude ne le traite :

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
│  Restructurer avec 7 principes Anthropic        │
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

steelprompt étend les 7 principes fondamentaux avec 5 modèles spécifiques au contexte tirés de la documentation Anthropic complète — appliqués automatiquement lorsque le prompt les signale :

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

### Ordonnancement de contexte long

Lorsque la tâche référence de longs fichiers ou documents, steelprompt les déplace **avant** la description de la tâche dans `<context>` — conformément aux directives d'Anthropic stipulant que les données longues doivent précéder la requête.

| Sans steelprompt | Avec steelprompt |
|---|---|
| `<task>` en premier, puis le contenu du fichier | contenu du fichier dans `<context>` en premier, puis `<task>` |

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
| `full` (défaut) | Protocole 3 niveaux actif : bypass → demander → appliquer les 7 principes Anthropic |
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

## Contournement

steelprompt n'intercepte jamais ces éléments :

| Préfixe | Comportement |
|---|---|
| `/commande` | Les commandes slash passent sans modification |
| `* prompt` | Contournement explicite — ignorer ce prompt |
| `# prompt` | Contournement explicite — ignorer ce prompt |
| < 5 mots | Traité comme atomique — réponse directe |

---

## Les 7 principes Anthropic

steelprompt les applique à chaque prompt clair et non contourné :

| # | Principe | Appliqué comme |
|---|---|---|
| 1 | **Rôle** | `You are a senior [domaine] engineer...` |
| 2 | **Contexte** | `<context>` — tout le contexte pertinent avant la tâche ; longs fichiers/documents placés dans `<context>` **avant** la description de la tâche |
| 3 | **Tâche** | `<task>` — mode impératif, étapes numérotées pour le travail multi-étapes |
| 4 | **Contraintes** | `<constraints>` — ce qu'il NE FAUT PAS faire, limites, règles de style ; contraintes de sécurité agentique injectées automatiquement pour les opérations destructives |
| 5 | **Format de sortie** | `<output_format>` — structure exacte, longueur, sections ; caractère de préfill ancré pour JSON/YAML/SQL |
| 6 | **Chaîne de pensée** | `Think through this step by step before answering` |
| 7 | **Exemples** | `<examples>` — paires entrée/sortie ; `<bad_example>` ajouté pour les tâches ambiguës afin de montrer ce qu'il NE FAUT PAS produire |

Source : [Anthropic Prompt Engineering Docs](https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/overview)

---

## Remerciements

Architecture inspirée de [severity1/claude-code-prompt-improver](https://github.com/severity1/claude-code-prompt-improver). Aucun code partagé.

## Licence

MIT
