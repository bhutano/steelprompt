<picture>
  <source media="(prefers-color-scheme: dark)" srcset="../assets/banner-dark.svg">
  <img src="../assets/banner-light.svg" alt="steelprompt" width="100%">
</picture>

<div align="center">

🌐 [English](../README.md) · [中文](README.zh.md) · **Español** · [PT-BR](README.pt-BR.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Deutsch](README.de.md) · [Français](README.fr.md) · [Italiano](README.it.md)

[![Version](https://img.shields.io/badge/version-0.3.0-4a9eff?style=flat-square)](https://github.com/bhutano/steelprompt/releases/tag/v0.3.0)
[![License](https://img.shields.io/badge/license-MIT-22c55e?style=flat-square)](https://github.com/bhutano/steelprompt/blob/master/LICENSE)
[![Python](https://img.shields.io/badge/python-3.8+-f59e0b?style=flat-square)](https://python.org)
[![Claude Code](https://img.shields.io/badge/claude_code-2.0.22+-a78bfa?style=flat-square)](https://claude.ai/code)

![demo](../steel_demo.gif)

**Cada prompt reestructurado según los 10 principios oficiales de Anthropic — automáticamente en Claude Code, bajo demanda en Claude.ai.**

✦ Sin API keys · ✦ Claude Code + Claude.ai web · ✦ Cero latencia adicional · ✦ 4 modos seleccionables

</div>

---

## El problema

Claude es tan bueno como los prompts que le das. La mayoría de los prompts carecen de asignación de rol, contexto estructurado, restricciones explícitas, especificación del formato de salida y ejemplos — todo lo que las propias guías de Anthropic dicen que mejora drásticamente la calidad de las respuestas.

Podrías dedicar 10 minutos a diseñar cada prompt manualmente. O usar steelprompt — automático en Claude Code, bajo demanda en Claude.ai.

---

## Cómo funciona

steelprompt funciona en dos superficies:

- **Claude Code (CLI)** — un hook `UserPromptSubmit` intercepta cada prompt automáticamente antes de que Claude lo procese.
- **Claude.ai (web)** — pega `prompts/steelprompt-web.md` en las Instrucciones personalizadas una sola vez, luego usa `/sp "prompt"` para diseñar cualquier prompt bajo demanda.

En ambos casos se aplica el mismo protocolo de decisión de 3 niveles:

```
Tu prompt
    │
    ▼
┌─────────────────────────────────────────────────┐
│  NIVEL 1 — BYPASS                               │
│  Comandos slash · < 5 palabras · tareas atómicas│
│  → Pasar sin cambios                            │
└─────────────────────────────────────────────────┘
    │ no bypassado
    ▼
┌─────────────────────────────────────────────────┐
│  NIVEL 2 — PREGUNTAR                            │
│  ¿Falta información crítica?                    │
│  → AskUserQuestion (1–2 preguntas específicas)  │
└─────────────────────────────────────────────────┘
    │ prompt claro
    ▼
┌─────────────────────────────────────────────────┐
│  NIVEL 3 — APLICAR FRAMEWORK   ← predeterminado │
│  Reestructurar con 10 principios Anthropic      │
│  silenciosamente, antes de que Claude responda  │
└─────────────────────────────────────────────────┘
```

Sin llamadas a APIs externas. Claude reestructura inline durante su inferencia normal — cero latencia adicional, cero tokens extra facturados.

---

## Nivel 3 en acción

Este es el núcleo de steelprompt. Cada prompt claro y no atómico lo atraviesa automáticamente.

**Escribes:**
```
add rate limiting to the auth endpoints
```

**Lo que steelprompt inyecta internamente** (visible en modo `preview` antes de la ejecución):
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

**Lo que produce Claude:** una implementación completa y lista para producción con tests — no una descripción genérica de las opciones de rate limiting.

---

## Patrones avanzados

steelprompt extiende el framework central con patrones específicos de contexto de la documentación completa de Anthropic — aplicados automáticamente cuando el prompt los requiere:

### Detección de cadena

Cuando una tarea abarca múltiples operaciones secuenciales, steelprompt detecta la cadena y muestra un plan antes de ejecutar.

**Escribes:**
```
refactoriza auth.py, agrega tests, actualiza la documentación
```

**steelprompt detecta una cadena de múltiples pasos y pausa para confirmación:**
```
Cadena detectada (3 prompts):
→ Prompt 1: Refactorizar auth.py siguiendo principios SOLID
             Produce: auth.py refactorizado
→ Prompt 2: Escribir tests pytest para el código refactorizado
             Usa: output del Prompt 1
→ Prompt 3: Actualizar docs/auth.md
             Usa: output del Prompt 1 + 2
```

Luego pregunta: **Ejecutar en secuencia · Enviar como prompt único · Cancelar**

---

### Seguridad agéntica

Cuando una tarea involucra operaciones irreversibles, steelprompt inyecta automáticamente restricciones de seguridad.

**Escribes:**
```
elimina todos los registros obsoletos de la base de datos de producción
```

**steelprompt agrega automáticamente a `<constraints>`:**
```
- Show COUNT of affected rows before executing DELETE
- Scope: only rows matching the explicit filter condition
- Require explicit confirmation before the irreversible action
- Do not touch tables or columns not explicitly mentioned
```

---

### Prefill para formatos críticos

Cuando el formato de salida es estrictamente crítico (JSON, YAML, SQL), steelprompt agrega un ancla de prefill: comenzar la respuesta con el carácter de apertura (`{`, `---`, `SELECT`) para fijar a Claude en el formato correcto desde el primer token.

```
Escribes: "analiza esta config y devuelve JSON"
steelprompt agrega a <output_format>: comenzar respuesta con {
```

---

### Ejemplos negativos

Para tareas ambiguas donde el formato de salida correcto no es obvio, steelprompt genera bloques `<bad_example>` junto a los bloques `<example>` — mostrar lo que **no** se debe producir reduce las alucinaciones en tareas sensibles al formato.

```
<example>
Input: user object → Output: {id, name, email} (no password field)
</example>
<bad_example>
Input: user object → Output: {id, name, email, password_hash} ← never expose this
</bad_example>
```

---

### Motivación / POR QUÉ

Claude generaliza a partir de explicaciones — steelprompt añade la razón detrás de una solicitud, no solo la solicitud en sí. Una restricción con un POR QUÉ se asimila mejor que una regla sola.

| Sin steelprompt | Con steelprompt |
|---|---|
| `NUNCA uses puntos suspensivos` | `Nunca uses puntos suspensivos — el motor de texto a voz no puede pronunciarlos` |
| `Mantén las respuestas cortas` | `Mantén las respuestas en menos de 3 oraciones — la salida se muestra en un tooltip móvil con espacio limitado` |

---

### Control de formato (encuadre positivo)

Cuando se especifica un formato de salida, steelprompt le dice a Claude qué PRODUCIR — no qué evitar. Las instrucciones positivas son más confiables que las negativas.

```
Escribes: "responde en texto plano, sin markdown"
steelprompt agrega a <output_format>: Escribe en párrafos de prosa fluida.
                                      Sin encabezados, listas ni bloques de código.
```

Para salida sin preámbulo:
```
steelprompt agrega: Responde directamente sin preámbulo.
                    No comiences con 'Aquí está...', 'Basándome en...', etc.
```

---

### Uso de herramientas y llamadas paralelas

Cuando un prompt es para un agente o sistema con herramientas, steelprompt inyecta orientación sobre ejecución paralela y valor predeterminado de acción.

**Escribes:**
```
build an agent that searches our docs, reads the top 3 results, and summarizes them
```

**steelprompt agrega a `<constraints>`:**
```
Make all independent tool calls in parallel — search + read all 3 results simultaneously.
Never use placeholders or guess missing parameters.
By default, implement changes rather than only suggesting them.
```

---

### Pensamiento y autocomprobación

Para tareas que requieren razonamiento de múltiples pasos o verificación, steelprompt añade pensamiento estructurado y una instrucción de autocomprobación.

```
Escribes: "calculate the optimal batch size for our embedding pipeline"

steelprompt agrega:
  Reason through the problem in <thinking> tags.
  Consider: throughput, memory, API rate limits, cost per token.
  Then provide your answer in <answer> tags.
  Before finishing, verify your recommendation satisfies all constraints above.
```

---

### Ordenamiento de contexto largo

Cuando la tarea hace referencia a archivos o documentos largos, steelprompt los mueve **antes** de la descripción de la tarea dentro de `<context>` — siguiendo la guía de Anthropic de que los datos largos deben preceder a la consulta (hasta un 30% de ganancia en precisión en entradas complejas).

```
steelprompt también agrega: Cita las secciones relevantes antes de responder.
```

| Sin steelprompt | Con steelprompt |
|---|---|
| `<task>` primero, luego el contenido del archivo | contenido del archivo dentro de `<context>` primero, luego `<task>` |
| Consulta antes de la evidencia | Evidencia antes de la consulta |

---

## Nivel 2 en acción

Cuando falta información crítica, steelprompt pregunta antes de adivinar.

| Escribes | steelprompt pregunta |
|---|---|
| `"mejora el código"` | ¿Qué archivo? ¿Qué tipo de mejora — legibilidad, rendimiento, corrección? |
| `"arregla el bug"` | ¿Cuál bug? ¿Hay pasos para reproducirlo o mensaje de error? |
| `"refactoriza auth"` | ¿Cuál es el objetivo? ¿Es API pública o interna? ¿Debe mantenerse idéntico el comportamiento? |
| `"cambia el color del ícono a rojo"` | *(Nivel 1 — atómico, respuesta directa)* |

---

## Modos

| Modo | Comportamiento |
|---|---|
| `full` (predeterminado) | Protocolo de 3 niveles activo: bypass → preguntar → aplicar 10 principios Anthropic |
| `preview` | Muestra el prompt diseñado antes de ejecutarlo — revisar, editar o cancelar |
| `ask-only` | Solo hace preguntas de aclaración; no aplica el framework completo |
| `off` | Hook completamente deshabilitado |

```bash
/steelprompt mode full
/steelprompt mode preview
/steelprompt mode ask-only
/steelprompt mode off
```

Configuración guardada por usuario en `$CLAUDE_PLUGIN_ROOT/.steelpromptrc`. Sin configuración = predeterminado `full`.

---

## Modo preview

¿Quieres ver el prompt diseñado antes de que se ejecute? Cambia a `preview`:

```
/steelprompt mode preview
```

Luego escribe cualquier prompt normalmente. En lugar de responder silenciosamente, Claude te mostrará el prompt reestructurado y preguntará: **Ejecutar · Editar · Cancelar**.

Si escribes en un idioma distinto al inglés, la vista previa se muestra traducida a tu idioma — pero **Run** siempre ejecuta la versión en inglés, que Claude procesa con mayor precisión.

---

## Skill manual: `/steelprompt`

Úsalo para diseñar manualmente cualquier prompt — o para cambiar de modo.

```
/steelprompt "migrar la tabla users para agregar soft deletes"
```

**Salida:**
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

## Instalación

```bash
claude plugin marketplace add bhutano/bhutano-marketplace
claude plugin install steelprompt
```

**Requisitos:** Claude Code 2.0.22+ · Python 3.8+

```bash
claude --version   # verificar versión de Claude Code
python --version   # verificar versión de Python
```

---

## Usar en Claude.ai (web)

¿No usas Claude Code? Puedes obtener el mismo framework de ingeniería de prompts directamente en [claude.ai](https://claude.ai) — sin instalación, sin CLI.

**Configuración (una sola vez):**
1. Abre [claude.ai](https://claude.ai) en tu navegador
2. Haz clic en el ícono de perfil → **Configuración** → **Perfil**
3. Encuentra **"Instrucciones personalizadas"** (o *"¿Cómo te gustaría que Claude respondiera?"*)
4. Copia el contenido de [`prompts/steelprompt-web.md`](https://raw.githubusercontent.com/bhutano/steelprompt/master/prompts/steelprompt-web.md) y pégalo allí → Guardar

Listo. Cada prompt que escribas en Claude.ai será reestructurado silenciosamente usando el mismo protocolo de 3 niveles antes de que Claude responda.

**Activación manual:** `/sp "tu prompt"` · **Modo preview:** `/sp mode preview`

> La versión web no tiene hooks ni llamadas a herramientas — funciona como system prompt dentro de las instrucciones personalizadas nativas de Claude.ai.

---

## Bypass

steelprompt nunca intercepta estos:

| Prefijo | Comportamiento |
|---|---|
| `/comando` | Los comandos slash pasan sin cambios |
| `* prompt` | Bypass explícito — omitir este prompt |
| `# prompt` | Bypass explícito — omitir este prompt |
| < 5 palabras | Tratado como atómico — respuesta directa |

---

## Los 10 principios Anthropic

steelprompt los aplica a cada prompt claro y no bypassado:

| # | Principio | Aplicado como |
|---|---|---|
| 1 | **Rol** | `You are a senior [dominio] engineer...` |
| 2 | **Contexto + Motivación** | `<context>` — todo el fondo relevante antes de la tarea, incluyendo el POR QUÉ detrás de la solicitud; archivos/documentos largos colocados **antes** de la descripción de la tarea |
| 3 | **Tarea** | `<task>` — modo imperativo, pasos numerados; explícito sobre acción vs. sugerencia |
| 4 | **Estructura XML** | Cada sección envuelta en etiquetas descriptivas (`<context>`, `<task>`, `<constraints>`, `<output_format>`, `<examples>`) para un análisis sin ambigüedad |
| 5 | **Restricciones** | `<constraints>` — qué NO hacer, límites, reglas de estilo; restricciones de seguridad agéntica inyectadas automáticamente para operaciones destructivas; anti-exceso y anti-alucinación para tareas de código |
| 6 | **Formato de salida** | `<output_format>` — encuadre positivo (decir qué PRODUCIR); estructura exacta, longitud, secciones; carácter de prefill para JSON/YAML/SQL; control de LaTeX y preámbulo |
| 7 | **Pensamiento** | `Think through this step by step` + etiquetas `<thinking>/<answer>` para tareas complejas; instrucción de autocomprobación; `<thinking>` en ejemplos few-shot para agentes |
| 8 | **Ejemplos** | `<examples>` — pares entrada/salida; `<bad_example>` agregado para tareas ambiguas para mostrar qué NO producir; 3–5 ejemplos diversos para mejores resultados |
| 9 | **Uso de herramientas** | Instrucción de llamadas paralelas a herramientas; valor predeterminado de acción proactiva vs. conservadora; para prompts dirigidos a agentes o sistemas con herramientas |
| 10 | **Contexto largo** | Datos colocados antes de la consulta; envoltorio XML de múltiples documentos; instrucción de citar antes de responder; para prompts que referencian archivos o documentos grandes |

Fuente: [Anthropic Prompting Best Practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices)

---

## Contribuir

steelprompt mejora cuando las personas lo usan y reportan lo que no funciona.

**¿Encontraste un bug o comportamiento inesperado?** [Abre un issue](https://github.com/bhutano/steelprompt/issues) — describe el prompt que escribiste y qué obtuviste vs. qué esperabas.

**¿Tienes una idea?** Abre un issue con la etiqueta `enhancement`. Son bienvenidas las sugerencias de nuevos patrones, mejores ejemplos o casos extremos que el framework no contempla.

**¿Quieres contribuir con código?** Consulta [CONTRIBUTING.md](../CONTRIBUTING.md) para las reglas básicas y los pasos de prueba.

---

## Agradecimientos

Arquitectura inspirada en [severity1/claude-code-prompt-improver](https://github.com/severity1/claude-code-prompt-improver). Sin código compartido.

## Licencia

MIT
