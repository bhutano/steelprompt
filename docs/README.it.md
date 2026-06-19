<picture>
  <source media="(prefers-color-scheme: dark)" srcset="../assets/banner-dark.svg">
  <img src="../assets/banner-light.svg" alt="steelprompt" width="100%">
</picture>

<div align="center">

🌐 [English](../README.md) · [中文](README.zh.md) · [Español](README.es.md) · [PT-BR](README.pt-BR.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Deutsch](README.de.md) · [Français](README.fr.md) · **Italiano**

[![Version](https://img.shields.io/badge/version-0.3.0-4a9eff?style=flat-square)](https://github.com/bhutano/steelprompt/releases/tag/v0.3.0)
[![License](https://img.shields.io/badge/license-MIT-22c55e?style=flat-square)](https://github.com/bhutano/steelprompt/blob/master/LICENSE)
[![Python](https://img.shields.io/badge/python-3.8+-f59e0b?style=flat-square)](https://python.org)
[![Claude Code](https://img.shields.io/badge/claude_code-2.0.22+-a78bfa?style=flat-square)](https://claude.ai/code)

![demo](../steel_demo.gif)

**Ogni prompt ristrutturato secondo i 10 principi ufficiali Anthropic — automaticamente in Claude Code, su richiesta in Claude.ai.**

✦ Nessuna API key · ✦ Claude Code + Claude.ai web · ✦ Zero latenza aggiuntiva · ✦ 4 modalità selezionabili

</div>

---

## Il problema

Claude è efficace quanto i prompt che gli dai. La maggior parte dei prompt manca di assegnazione del ruolo, contesto strutturato, vincoli espliciti, specifica del formato di output ed esempi — tutti elementi che le linee guida ufficiali di Anthropic indicano come determinanti per la qualità delle risposte.

Potresti dedicare 10 minuti a ingegnerizzare ogni prompt manualmente. Oppure usare steelprompt — automatico in Claude Code, su richiesta in Claude.ai.

---

## Come funziona

steelprompt funziona su due superfici:

- **Claude Code (CLI)** — un hook `UserPromptSubmit` intercetta ogni prompt automaticamente prima che Claude lo elabori.
- **Claude.ai (web)** — incolla `prompts/steelprompt-web.md` nelle Istruzioni personalizzate una volta sola, poi usa `/sp "prompt"` per ingegnerizzare qualsiasi prompt su richiesta.

In entrambi i casi si applica lo stesso protocollo decisionale a 3 livelli:

```
Il tuo prompt
    │
    ▼
┌─────────────────────────────────────────────────┐
│  LIVELLO 1 — BYPASS                             │
│  Comandi slash · < 5 parole · task atomici      │
│  → Passa direttamente a Claude                  │
└─────────────────────────────────────────────────┘
    │ non bypassato
    ▼
┌─────────────────────────────────────────────────┐
│  LIVELLO 2 — CHIEDI                             │
│  Mancano informazioni critiche?                 │
│  → AskUserQuestion (1–2 domande mirate)         │
└─────────────────────────────────────────────────┘
    │ prompt chiaro
    ▼
┌─────────────────────────────────────────────────┐
│  LIVELLO 3 — APPLICA IL FRAMEWORK   ← default   │
│  Ristruttura con i 10 principi Anthropic        │
│  silenziosamente, prima che Claude risponda     │
└─────────────────────────────────────────────────┘
```

Nessuna chiamata API esterna. Claude ristruttura inline durante la normale inferenza — zero latenza aggiuntiva, zero token extra fatturati.

---

## Livello 3 in azione

Questo è il cuore di steelprompt. Ogni prompt chiaro e non atomico lo attraversa automaticamente.

**Scrivi:**
```
aggiungi rate limiting agli endpoint di autenticazione
```

**Cosa steelprompt inietta internamente** (in modalità `preview` puoi vederlo prima dell'esecuzione):
```
You are a senior backend security engineer.

<context>
Progetto: API Express.js con autenticazione JWT
Endpoint interessati: POST /auth/login, POST /auth/refresh, POST /auth/register
Ambiente: Node.js 20, middleware esistente in src/middleware/
Vincoli noti dalla conversazione: Redis già in uso per lo storage di sessione
</context>

<task>
Implementa il rate limiting sugli endpoint di autenticazione:
1. Rate limiting per IP: max 5 richieste/minuto su /login e /register
2. Rate limiting per utente: max 20 richieste/ora su /refresh
3. Restituisci 429 con header Retry-After al superamento del limite
4. Non modificare gli endpoint non-auth
</task>

<constraints>
- Riutilizza la connessione Redis esistente, non introdurre un nuovo client
- Non modificare la logica di validazione JWT
- Lo stato del rate limit deve sopravvivere ai riavvii del server
- Segui i pattern middleware esistenti in src/middleware/
</constraints>

<output_format>
1. Nuovo file middleware con l'implementazione
2. Diff con le modifiche alle route auth
3. Due test Jest: limite raggiunto + flusso normale
</output_format>

Think through this step by step before answering.
```

**Risultato:** un'implementazione completa e production-ready con test — non una panoramica generica delle opzioni di rate limiting.

---

## Pattern avanzati

steelprompt estende il framework con pattern specifici per contesto tratti dalla documentazione Anthropic completa — applicati automaticamente quando il prompt li richiede:

### Rilevamento catena

Quando un task copre più operazioni sequenziali, steelprompt rileva la catena e mostra un piano prima di eseguire.

**Scrivi:**
```
refactora auth.py, aggiungi test, aggiorna la documentazione
```

**steelprompt rileva una catena multi-step e si ferma per conferma:**
```
Catena rilevata (3 prompt):
→ Prompt 1: Refactora auth.py secondo i principi SOLID
             Produce: auth.py ristrutturato
→ Prompt 2: Scrivi test pytest per il codice ristrutturato
             Usa: output di Prompt 1
→ Prompt 3: Aggiorna docs/auth.md
             Usa: output di Prompt 1 + 2
```

Poi chiede: **Esegui in sequenza · Invia come prompt unico · Annulla**

---

### Sicurezza agentica

Quando un task coinvolge operazioni irreversibili, steelprompt inietta automaticamente vincoli di sicurezza.

**Scrivi:**
```
cancella tutti i record obsoleti dal database di produzione
```

**steelprompt aggiunge automaticamente a `<constraints>`:**
```
- Mostra COUNT delle righe interessate prima di eseguire DELETE
- Scope: solo le righe che corrispondono alla condizione del filtro esplicita
- Richiedi conferma esplicita prima dell'azione irreversibile
- Non toccare tabelle o colonne non menzionate esplicitamente
```

---

### Prefill per formati critici

Quando il formato di output è rigidamente critico (JSON, YAML, SQL), steelprompt aggiunge un'ancora di prefill: inizia la risposta con il carattere di apertura del formato (`{`, `---`, `SELECT`) per ancorare Claude al formato corretto dal primo token.

```
Scrivi: "analizza questa config e restituisci JSON"
steelprompt aggiunge a `<output_format>`: inizia la risposta con {
```

---

### Esempi negativi

Per task ambigui dove il formato di output corretto non è ovvio, steelprompt genera blocchi `<bad_example>` accanto ai blocchi `<example>` — mostrare cosa **non** produrre riduce le allucinazioni su task format-sensitive.

```
<example>
Input: oggetto user → Output: {id, name, email} (nessun campo password)
</example>
<bad_example>
Input: oggetto user → Output: {id, name, email, password_hash} ← non esporre mai questo
</bad_example>
```

---

### Motivazione / PERCHÉ

Claude generalizza dalle spiegazioni — steelprompt aggiunge il motivo dietro a una richiesta, non solo la richiesta stessa. Un vincolo con un PERCHÉ è più efficace di una regola senza contesto.

| Senza steelprompt | Con steelprompt |
|---|---|
| `NON usare mai le ellissi` | `Non usare mai le ellissi — il motore di sintesi vocale non riesce a pronunciarle` |
| `Mantieni le risposte brevi` | `Mantieni le risposte sotto i 3 periodi — l'output viene visualizzato in un tooltip mobile con spazio limitato` |

---

### Controllo del formato (formulazione positiva)

Quando viene specificato un formato di output, steelprompt dice a Claude cosa PRODURRE — non cosa evitare. Le istruzioni positive sono più affidabili di quelle negative.

```
Scrivi: "rispondi in testo semplice, niente markdown"
steelprompt aggiunge a <output_format>: Scrivi in paragrafi di prosa fluente.
                                         Nessun titolo, elenco puntato o blocco di codice.
```

Per output senza preambolo:
```
steelprompt aggiunge: Rispondi direttamente senza preambolo.
                      Non iniziare con 'Ecco...', 'In base a...', ecc.
```

---

### Tool use e chiamate parallele

Quando un prompt è destinato a un agente o sistema con strumenti, steelprompt inietta indicazioni sull'esecuzione parallela e sull'azione predefinita.

**Scrivi:**
```
build an agent that searches our docs, reads the top 3 results, and summarizes them
```

**steelprompt aggiunge a `<constraints>`:**
```
Make all independent tool calls in parallel — search + read all 3 results simultaneously.
Never use placeholders or guess missing parameters.
By default, implement changes rather than only suggesting them.
```

---

### Thinking e auto-verifica

Per task che richiedono ragionamento multi-step o verifica, steelprompt aggiunge thinking strutturato e un'istruzione di auto-verifica.

```
Scrivi: "calculate the optimal batch size for our embedding pipeline"

steelprompt aggiunge:
  Reason through the problem in <thinking> tags.
  Consider: throughput, memory, API rate limits, cost per token.
  Then provide your answer in <answer> tags.
  Before finishing, verify your recommendation satisfies all constraints above.
```

---

### Ordinamento del contesto lungo

Quando il task fa riferimento a file o documenti lunghi, steelprompt li sposta **prima** della descrizione del task dentro `<context>` — seguendo le linee guida Anthropic: i dati lunghi devono precedere la query (fino al 30% di guadagno in accuratezza su input complessi).

```
steelprompt aggiunge anche: Quote the relevant sections before answering.
```

| Senza steelprompt | Con steelprompt |
|---|---|
| `<task>` prima, poi il contenuto del file | contenuto del file dentro `<context>` prima, poi `<task>` |
| Query prima dell'evidenza | Evidenza prima della query |

---

## Livello 2 in azione

Quando mancano informazioni critiche, steelprompt chiede prima di indovinare.

| Scrivi | steelprompt chiede |
|---|---|
| `"migliora il codice"` | Quale file? Che tipo di miglioramento — leggibilità, performance, correttezza? |
| `"fixa il bug"` | Quale bug? Passi per riprodurlo o messaggio di errore? |
| `"refactora l'auth"` | Qual è l'obiettivo? È API pubblica o interna? Il comportamento deve restare identico? |
| `"cambia colore icona in rosso"` | *(Livello 1 — atomico, risposta diretta)* |

---

## Modalità

| Modalità | Comportamento |
|---|---|
| `full` (default) | Protocollo 3-livelli attivo: bypass → chiedi → applica i 10 principi Anthropic |
| `preview` | Mostra il prompt ingegnerizzato prima di eseguirlo — rivedi, modifica o annulla |
| `ask-only` | Fa solo domande di chiarimento; non applica il framework completo |
| `off` | Hook completamente disabilitato |

```bash
/steelprompt mode full
/steelprompt mode preview
/steelprompt mode ask-only
/steelprompt mode off
```

Configurazione salvata per utente in `$CLAUDE_PLUGIN_ROOT/.steelpromptrc`. Zero config = default `full`.

---

## Modalità preview

Vuoi vedere il prompt ingegnerizzato prima che venga eseguito? Passa a `preview`:

```
/steelprompt mode preview
```

Poi scrivi qualsiasi prompt normalmente. Invece di rispondere silenziosamente, Claude ti mostrerà il prompt ristrutturato e chiederà: **Esegui · Modifica · Annulla**.

Se scrivi in una lingua diversa dall'inglese, l'anteprima viene mostrata tradotta nella tua lingua — ma **Run** esegue sempre la versione in inglese, che Claude elabora con maggiore precisione.

---

## Skill manuale: `/steelprompt`

Usala per ingegnerizzare manualmente qualsiasi prompt — o per cambiare modalità.

```
/steelprompt "migra la tabella users per aggiungere soft delete"
```

**Output:**
```
You are a senior database engineer specializing in PostgreSQL migrations.

<context>
Progetto: applicazione Rails 7 con PostgreSQL
Tabella: users (id, email, created_at, updated_at)
Sistema di migrazione: ActiveRecord
Vincoli noti: deploy zero-downtime richiesto, tabella con ~2M righe
</context>

<task>
Aggiungi il supporto soft delete alla tabella users:
1. Aggiungi colonna timestamp deleted_at (nullable, default null)
2. Aggiungi indice su deleted_at per le performance delle query
3. Aggiorna il modello User con default_scope che esclude i record eliminati
4. Aggiungi metodi User#soft_delete e User#restore
</task>

<examples>
<example>
Input: User.destroy(42)
Output (dopo): imposta deleted_at = now(), non esegue DELETE sulla riga
</example>
<example>
Input: User.all
Output (dopo): restituisce solo i record con deleted_at IS NULL
</example>
</examples>

<constraints>
- Non usare gem (acts_as_paranoid, discard) — implementa direttamente
- La migrazione deve essere reversibile (metodo down obbligatorio)
- Non modificare indici o chiavi esterne esistenti
- Mantieni disponibile il percorso hard-delete tramite User.unscoped.destroy
</constraints>

<output_format>
1. File di migrazione con up/down
2. Modifiche al modello (3–5 righe max)
3. Due unit test: soft delete imposta la colonna, default scope esclude i cancellati
</output_format>

Think through this step by step before answering.
```

---

## Installazione

```bash
claude plugin marketplace add bhutano/bhutano-marketplace
claude plugin install steelprompt
```

**Requisiti:** Claude Code 2.0.22+ · Python 3.8+

```bash
claude --version   # verifica versione Claude Code
python --version   # verifica versione Python
```

---

## Usa su Claude.ai (web)

Non usi Claude Code? Puoi ottenere lo stesso framework di prompt engineering direttamente su [claude.ai](https://claude.ai) — nessuna installazione, nessuna CLI.

**Configurazione (una volta sola):**
1. Apri [claude.ai](https://claude.ai) nel tuo browser
2. Clicca sull'icona del profilo → **Impostazioni** → **Profilo**
3. Trova **"Istruzioni personalizzate"** (o *"Come vorresti che Claude rispondesse?"*)
4. Copia il contenuto di [`prompts/steelprompt-web.md`](https://raw.githubusercontent.com/bhutano/steelprompt/master/prompts/steelprompt-web.md) e incollalo lì → Salva

Fatto. Ogni prompt che scrivi su Claude.ai verrà silenziosamente ristrutturato usando lo stesso protocollo a 3 livelli prima che Claude risponda.

**Trigger manuale:** `/sp "il tuo prompt"` · **Modalità preview:** `/sp mode preview`

> La versione web non ha hook né chiamate a strumenti — funziona come system prompt nelle istruzioni personalizzate native di Claude.ai.

---

## Bypass

steelprompt non intercetta mai questi:

| Prefisso | Comportamento |
|---|---|
| `/comando` | I comandi slash passano direttamente |
| `* prompt` | Bypass esplicito — salta questo prompt |
| `# prompt` | Bypass esplicito — salta questo prompt |
| < 5 parole | Trattato come atomico — risposta diretta |

---

## I 10 principi Anthropic

steelprompt li applica a ogni prompt chiaro e non bypassato:

| # | Principio | Applicato come |
|---|---|---|
| 1 | **Ruolo** | `You are a senior [dominio] engineer...` |
| 2 | **Contesto + Motivazione** | `<context>` — tutto il background rilevante prima del task, incluso il PERCHÉ della richiesta; file/documenti lunghi collocati **prima** della descrizione del task |
| 3 | **Task** | `<task>` — imperativo, steps numerati; esplicito su azione vs. suggerimento |
| 4 | **Struttura XML** | Ogni sezione racchiusa in tag descrittivi (`<context>`, `<task>`, `<constraints>`, `<output_format>`, `<examples>`) per un parsing non ambiguo |
| 5 | **Vincoli** | `<constraints>` — cosa NON fare, limiti, regole di stile; vincoli di sicurezza agentica iniettati automaticamente per operazioni distruttive; anti-eccessiva-proattività e anti-allucinazione per task di codice |
| 6 | **Formato output** | `<output_format>` — formulazione positiva (dire cosa PRODURRE); struttura esatta, lunghezza, sezioni; carattere di prefill per JSON/YAML/SQL; controllo LaTeX e preambolo |
| 7 | **Thinking** | `Think through this step by step` + tag `<thinking>/<answer>` per task complessi; istruzione di auto-verifica; `<thinking>` negli esempi few-shot per agenti |
| 8 | **Esempi** | `<examples>` — coppie input/output; `<bad_example>` aggiunto per task ambigui per mostrare cosa NON produrre; 3–5 esempi diversificati per risultati ottimali |
| 9 | **Tool use** | Istruzione di chiamata strumenti parallela; azione predefinita proattiva vs. conservativa; per prompt destinati ad agenti o sistemi con strumenti |
| 10 | **Contesto lungo** | Dati collocati prima della query; wrapping XML multi-documento; istruzione cita-prima-di-rispondere; per prompt che fanno riferimento a file o documenti di grandi dimensioni |

Fonte: [Anthropic Prompting Best Practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices)

---

## Contribuire

steelprompt migliora quando le persone lo usano e segnalano cosa non funziona.

**Trovato un bug o un comportamento inatteso?** [Apri un'issue](https://github.com/bhutano/steelprompt/issues) — descrivi il prompt che hai digitato e cosa hai ottenuto rispetto a cosa ti aspettavi.

**Hai un'idea?** Apri un'issue con l'etichetta `enhancement`. Sono benvenuti suggerimenti per nuovi pattern, esempi migliori o casi limite che il framework non gestisce.

**Vuoi contribuire con del codice?** Consulta [CONTRIBUTING.md](../CONTRIBUTING.md) per le regole di base e i passaggi di test.

---

## Ringraziamenti

Architettura ispirata da [severity1/claude-code-prompt-improver](https://github.com/severity1/claude-code-prompt-improver). Nessun codice condiviso.

## Licenza

MIT
