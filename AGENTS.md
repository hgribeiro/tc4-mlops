# AGENTS.md — Guia para agentes neste repositório

## 1. Propósito do repositório

Este repositório documenta e implementa uma plataforma demonstrável de MLE/MLOps e IA generativa para **personalização responsável em jornadas de empréstimos com garantia**.

O produto de trabalho é uma plataforma de experimentação adaptativa capaz de decidir o **melhor próximo passo responsável** para um cliente sintético elegível, considerando:

- tipo de garantia;
- canal;
- elegibilidade sintética;
- risco;
- delayed rewards;
- explicabilidade;
- governança;
- avaliação offline;
- operação em ambiente financeiro regulado simulado.

A solução não deve ser apresentada como sistema bancário real pronto para produção regulada.

## 2. Persona principal

A persona principal é **Lary**, documentada em:

- `personas/lary-cto-bu-loan/SOUL.md`

Documentos de produto já consolidados:

- `docs/product/mvp-lary.md`
- `docs/product/offer-arms.md`

Lary é a **CTO da unidade de negócio de Empréstimos com Garantia** de um banco digital.

Sempre que houver dúvida de produto, canal, métrica, risco ou plausibilidade bancária, priorize a visão de Lary.

Lary valoriza:

- rastreabilidade;
- governança;
- valor mensurável;
- logs auditáveis;
- reason codes;
- humano no loop;
- diferenciação entre simulação, oferta, proposta e aprovação;
- cuidado com crédito colateralizado;
- comparação contra baseline simples.

Lary rejeita:

- promessa de aprovação automática de crédito;
- maximização cega de clique;
- ausência de explicabilidade;
- dados sensíveis ou proxies indevidos;
- ausência de rollback;
- narrativa de produção regulada sem evidência.

## 3. Decisions e ADRs

Use dois tipos de registro:

- `docs/decisions/`: decisões de produto, domínio, planejamento, escopo, narrativa e checklist.
- `docs/adr/`: decisões arquiteturais ou estruturantes difíceis de reverter, especialmente quando afetam implementação, contratos, fronteiras de responsabilidade ou tecnologia.

As decisions ficam em `docs/decisions/` e devem ser numeradas com prefixo de três dígitos.

Arquivos atuais:

- `docs/decisions/001-fundacao-produto-plataforma-experimentacao-adaptativa.md`
- `docs/decisions/002-enriquecimento-contexto-bancario-emprestimos-garantia.md`
- `docs/decisions/003-checklist-planejamento-mvp-lary.md`

ADR atual:

- `docs/adr/0001-modelo-de-termos-canonicos-e-decisoes.md`

Ao criar novas decisions, use o próximo número disponível, por exemplo:

```text
docs/decisions/004-nome-da-decisao.md
```

Ao criar novas ADRs, use o próximo número disponível em `docs/adr/`, por exemplo:

```text
docs/adr/0002-nome-da-decisao-arquitetural.md
```

## 4. Direção de produto aprovada

A vertical inicial é **Empréstimos com Garantia**.

Tipos de garantia no MVP inicial:

- veículo;
- imóvel;
- investimentos.

Fora do MVP inicial:

- recebíveis sintéticos, como evolução futura.

A plataforma não escolhe apenas “qual oferta vender”. Ela escolhe o **próximo passo responsável**, por exemplo:

- iniciar simulação de crédito com garantia;
- apresentar conteúdo educativo;
- solicitar documentação;
- encaminhar para especialista/agência;
- não ofertar nem simular naquele momento.

## 5. Escopo inicial recomendado

Seguir o checklist em:

- `docs/decisions/003-checklist-planejamento-mvp-lary.md`

Ordem recomendada atual:

1. manter `docs/product/mvp-lary.md` alinhado às decisões aprovadas;
2. manter `docs/product/offer-arms.md` alinhado ao foco em simulação/próximo passo;
3. documentar a base pública em `data/kaggle/README.md`;
4. criar `docs/data/synthetic-schema.md`;
5. criar `data/golden_set/evaluation_cases.jsonl`;
6. implementar baseline determinístico;
7. implementar política adaptativa;
8. expor CLI/API/notebook/app;
9. documentar governança;
10. montar narrativa de demo.

## 6. Regras de escrita documental

Ao escrever documentação:

- use português claro e direto;
- mantenha tom executivo-técnico;
- diferencie hipótese, decisão e limitação;
- explique por que a decisão importa para Lary;
- evite promessas exageradas;
- explicite não-objetivos;
- sempre que falar de crédito, diferencie:
  - recomendação;
  - simulação;
  - proposta;
  - aprovação;
  - contratação.

## 7. Regras de domínio financeiro

Não use nem sugira uso de:

- dados reais de clientes;
- CPF;
- nome;
- e-mail;
- telefone;
- renda real sensível;
- patrimônio real;
- gênero;
- raça;
- religião;
- saúde;
- orientação sexual;
- regras comerciais privadas de bancos.

A base pública deve ser tratada como proxy e enriquecida com dados sintéticos.

Em bases de marketing bancário, atenção especial a vazamento temporal. A coluna `duration`, por exemplo, não deve ser usada para decisão antes da interação.

## 8. Algoritmos e avaliação

A abordagem principal deve comparar:

1. baseline determinístico simples;
2. política adaptativa, inicialmente Thompson Sampling contextual simplificado por segmento, garantia e canal.

Métricas importantes:

- uplift contra baseline;
- recompensa acumulada;
- regret acumulado;
- taxa de exploração;
- conversão qualificada;
- proposta qualificada;
- exposição por braço;
- fairness por segmento sintético;
- guardrails acionados;
- cobertura de logs auditáveis.

Não otimize apenas clique.

## 9. Interface e logs

Toda decisão demonstrável deve retornar, no mínimo:

- `decision_id`;
- `request_id`;
- `selected_action` com o próximo passo escolhido;
- `policy_version`;
- `reason_codes`;
- `requires_human_review`;
- `guardrails_triggered`;
- referência de log auditável.

Logs devem seguir minimização de dados.

## 10. Governança obrigatória

A solução deve documentar:

- intended use;
- usos fora de escopo;
- limitações;
- riscos conhecidos;
- humano no loop;
- aprovação de política;
- rollback;
- fairness;
- LGPD simulada;
- auditoria de decisão.

Arquivos esperados futuramente:

- `docs/model-card.md`
- `docs/system-card.md`
- `docs/lgpd-plan.md`
- `docs/architecture-azure.md`

## 11. Convenções para agentes de código

Antes de editar:

1. leia os documentos de decisão relevantes;
2. leia `personas/lary-cto-bu-loan/SOUL.md` se a tarefa envolver produto, domínio ou narrativa;
3. mantenha mudanças pequenas e coerentes;
4. prefira criar artefatos planejados no checklist antes de código complexo;
5. não invente requisitos bancários como fatos reais — marque como hipótese sintética.

Ao editar arquivos:

- preserve a numeração das decisions;
- não renomeie arquivos sem necessidade;
- use nomes kebab-case;
- mantenha documentação em Markdown;
- se criar código, inclua caminho claro de execução e validação.

## 12. Narrativa de demo esperada

A demo deve conseguir mostrar três cenas:

1. **Cliente digital simples** recebe simulação de veículo no SuperApp.
2. **Cliente com garantia complexa** é encaminhado para especialista/agência.
3. **Cliente inelegível ou adversarial** recebe `no_offer_now` ou conteúdo educativo, com guardrail registrado.

A demo falha se parecer apenas um ranking de ofertas sem explicação, canal, elegibilidade, risco e log auditável.

## Agent skills

### Issue tracker

Issues são rastreadas no GitHub Issues do repo; PRs externos não são superfície de triagem. See `docs/agents/issue-tracker.md`.

### Triage labels

Usar os labels padrão: `needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`. See `docs/agents/triage-labels.md`.

### Domain docs

Layout single-context: `CONTEXT.md` e `docs/adr/` na raiz do repo. See `docs/agents/domain.md`.
