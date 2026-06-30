# Demanda 001 — Responder perguntas para o MVP narrativo da BU de Empréstimos com Garantia

## Objetivo

Responder, na voz da persona **Lary**, as perguntas necessárias para executar a etapa 1 do checklist em `docs/decisions/003-checklist-planejamento-mvp-lary.md`.

O resultado deve servir como base para criar `docs/product/mvp-lary.md`.

## Contexto obrigatório

Antes de responder, considerar:

- `personas/lary-cto-bu-loan/SOUL.md`
- `docs/decisions/003-checklist-planejamento-mvp-lary.md`
- `docs/decisions/001-fundacao-produto-plataforma-experimentacao-adaptativa.md`
- `docs/decisions/002-enriquecimento-contexto-bancario-emprestimos-garantia.md`

## Instruções para Lary

Responder como **Lary, CTO da unidade de negócio de Empréstimos com Garantia**.

A resposta deve ser pragmática, executiva e orientada a decisão. Não deve ser genérica. Quando houver incerteza, declarar a decisão preferida e o risco associado.

## Perguntas a responder

### 1. Problema principal da BU

1. Qual é o problema prioritário da unidade de Empréstimos com Garantia que o MVP deve resolver primeiro?
2. O problema principal é aquisição, conversão, qualificação, abandono, custo operacional, risco, experiência do cliente ou aprendizado sobre canais/ofertas?
3. Qual problema deve ficar explicitamente fora do MVP?

### 2. Canal inicial

4. O MVP deve começar por SuperApp, agência/atendimento consultivo ou fluxo híbrido?
5. Qual canal deve ser o principal na demo?
6. Em quais situações o cliente deve sair do autosserviço digital e ser encaminhado para especialista?
7. O encaminhamento para especialista deve ser tratado como sucesso possível ou como fricção?

### 3. Garantias no MVP

8. Quais tipos de garantia entram no MVP inicial?
9. Quais tipos de garantia ficam como extensão futura?
10. Entre veículo, imóvel, investimentos e recebíveis sintéticos, qual deve ser a garantia âncora da demo?
11. Como a decisão muda para cada tipo de garantia?

### 4. Próximos passos permitidos

12. Quais próximos passos a plataforma pode escolher no MVP?
13. A plataforma deve escolher apenas ofertas de produto ou também ações de jornada, como educação, simulação, documentação e especialista?
14. Quando o braço `no_offer_now` deve aparecer?

### 5. Métrica principal

15. Qual deve ser a métrica principal de negócio do MVP?
16. Devemos otimizar clique, simulação iniciada, simulação qualificada, proposta completa, proposta qualificada ou contratação simulada?
17. Qual métrica Lary defenderia para justificar continuidade do projeto?
18. Quais métricas secundárias precisam acompanhar a principal?

### 6. Guardrails e não-objetivos

19. O que a plataforma não pode prometer?
20. Quais decisões exigem humano no loop?
21. Quais riscos fariam Lary pausar o MVP?
22. Como deixar claro que a plataforma não aprova crédito automaticamente?

### 7. Critérios de sucesso da demo

23. O que precisa aparecer na demo para Lary considerar o MVP convincente?
24. Quais três cenas de demo representam melhor o valor da solução?
25. Qual evidência mínima de governança precisa aparecer?

### 8. Decisão final de Lary

26. Escreva uma decisão executiva curta, em primeira pessoa, dizendo qual MVP Lary aprova para começar.
27. Liste as decisões ainda pendentes que precisam de confirmação humana antes de implementação.

## Formato esperado da resposta

Responder em Markdown, com as seções:

1. `Resumo executivo de Lary`
2. `Decisões para o MVP`
3. `Respostas às perguntas`
4. `Não-objetivos e guardrails`
5. `Métricas aprovadas`
6. `Cenas recomendadas para demo`
7. `Pendências de confirmação humana`
8. `Texto-base recomendado para docs/product/mvp-lary.md`

## Arquivo de resposta esperado

A resposta deve ser escrita em:

`personas/lary-cto-bu-loan/001-resposta-mvp-narrativo.md`
