# Domain Docs

How the engineering skills should consume this repo's domain documentation when exploring the codebase.

## Layout

This is a **single-context** repo.

Read:

- `CONTEXT.md` at the repo root for canonical domain vocabulary.
- `docs/adr/` for architectural or structural decisions.
- `docs/decisions/` for product, domain, planning, scope, narrative and checklist decisions.
- `AGENTS.md` for repository-specific instructions.

If any optional file does not exist, proceed silently. Do not suggest creating it upfront unless the current task resolves a term or decision that belongs there.

## Use the glossary's vocabulary

When output names a domain concept — in an issue title, refactor proposal, hypothesis, test name, CLI command or documentation — use the term as defined in `CONTEXT.md`.

Important canonical terms in this repo include:

- `Próximo Passo Responsável`
- `Cliente Sintético`
- `Braço`
- `Simulação`
- `Proposta Qualificada Simulada`
- `Guardrail`
- `Reason Code`
- `Humano no Loop`
- `Delayed Reward`
- `LLM/RAG`

Avoid drifting to synonyms that the glossary rejects, especially "oferta direta", "aprovação", "contratação" or "cliente real".

## Respect ADRs and decisions

Before implementing or changing behavior, read relevant ADRs in `docs/adr/`.

If an output contradicts an existing ADR or product decision, surface it explicitly rather than silently overriding it. Example:

> Contradicts ADR-0001 because it lets the LLM choose a braço directly; reopen the decision only if that trade-off is intentional.

## Domain boundary reminders

- The MVP is demonstrable and synthetic; it is not a real regulated banking production system.
- Guardrails run before baseline or policy adaptation.
- The policy chooses only among eligible and safe braços.
- LLM/RAG explains, consults documentation and supports governance; it does not decide braços or approve credit.
- Recebíveis sintéticos are outside the initial MVP.
