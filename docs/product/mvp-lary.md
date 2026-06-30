# MVP Lary — Plataforma de Próximo Passo Responsável em Empréstimos com Garantia

## 1. Objetivo do documento

Este documento consolida a Etapa 1 do planejamento do MVP para **Lary**, CTO da unidade de negócio de **Empréstimos com Garantia**.

O objetivo é fechar o recorte inicial do produto antes de avançar para catálogo de braços, dados sintéticos, golden set, baseline e política adaptativa.

## 2. Visão resumida do MVP

O MVP deve ajudar a BU de Empréstimos com Garantia a decidir, em um fluxo híbrido com SuperApp e atendimento consultivo, qual é o **melhor próximo passo responsável** para cada cliente sintético elegível.

A plataforma não deve apenas rankear ofertas. Ela deve decidir entre simular, educar, solicitar dados, encaminhar para especialista ou não ofertar naquele momento.

Formulação do MVP:

> Ajudar a BU de Empréstimos com Garantia a aumentar propostas qualificadas simuladas, decidindo o próximo passo responsável para clientes pessoa física sintéticos em jornadas híbridas de crédito com garantia, com rastreabilidade, governança e comparação contra baseline determinístico.

## 3. Problema principal da BU de Lary

O problema principal do MVP é aumentar a geração de **propostas qualificadas simuladas** em jornadas de empréstimo com garantia.

A BU de Lary não quer apenas aumentar cliques ou impressões de campanha. Ela quer melhorar a qualidade da jornada até o ponto em que o cliente sintético:

1. conclui uma simulação; e
2. fornece dados mínimos ou documentação para pré-análise.

Essa definição preserva valor de negócio sem prometer aprovação, contratação ou concessão real de crédito.

## 4. Métrica principal

A métrica principal do MVP será:

> **propostas qualificadas simuladas por decisão.**

Uma proposta qualificada simulada ocorre quando o cliente sintético conclui a simulação e fornece dados mínimos/documentação para pré-análise.

Importante:

- não significa aprovação de crédito;
- não significa contratação;
- não define limite real;
- não define taxa real;
- não substitui análise de risco ou compliance.

## 5. Canal inicial

O canal inicial será um **fluxo híbrido**:

- **SuperApp** como canal principal de escala;
- **especialista/agência** como fallback consultivo para casos complexos, sensíveis ou de maior valor.

Essa decisão permite demonstrar três comportamentos importantes:

1. clientes digitais simples podem avançar pelo SuperApp;
2. clientes com garantias complexas podem ser encaminhados para atendimento humano;
3. clientes inelegíveis ou adversariais podem receber educação ou `no_offer_now`.

## 6. Público sintético inicial

O MVP será focado em **pessoa física**.

O público sintético terá:

- clientes pessoa física gerais;
- clientes de relacionamento alto como segmento especial;
- segmentos sintéticos não sensíveis para avaliação de exposição e fairness.

Ficam fora do público inicial:

- pessoa jurídica;
- fluxos com recebíveis reais;
- dados reais de renda, patrimônio ou relacionamento bancário;
- atributos sensíveis ou identificadores pessoais.

## 7. Garantias no MVP

Entram no MVP inicial:

| Garantia | Papel no MVP | Jornada esperada |
| --- | --- | --- |
| Veículo | Caso simples e digital | SuperApp, autosserviço, simulação rápida |
| Imóvel | Caso complexo e de maior valor | Simulação inicial e possível encaminhamento consultivo |
| Investimentos | Caso de relacionamento alto | Simulação cuidadosa, explicação clara e possível atendimento consultivo |

## 8. Garantias fora do MVP inicial

Fica fora do MVP inicial:

- recebíveis sintéticos.

Motivo: recebíveis introduzem complexidade de pessoa jurídica, fluxo de caixa, validação de recebíveis e critérios próprios de elegibilidade. Essa garantia pode entrar como evolução futura, depois que o MVP de pessoa física estiver demonstrável.

## 9. Objeto da decisão

A política do MVP deve escolher o **próximo passo da jornada**, não apenas uma oferta.

Braços candidatos em alto nível:

| Braço | Descrição |
| --- | --- |
| `simulate_vehicle_secured_loan` | Simular empréstimo com garantia de veículo no SuperApp |
| `simulate_home_equity` | Simular empréstimo com garantia de imóvel |
| `simulate_investment_secured_loan` | Simular crédito com garantia de investimentos |
| `educational_content_secured_credit` | Apresentar conteúdo educativo sobre crédito com garantia |
| `request_documents` | Solicitar dados mínimos/documentação para pré-análise |
| `route_to_specialist` | Encaminhar para especialista/agência |
| `no_offer_now` | Não ofertar naquele momento |

O detalhamento completo desses braços será feito em `docs/product/offer-arms.md`.

## 10. Métricas secundárias

Além da métrica principal, o MVP deve acompanhar:

1. simulação iniciada;
2. simulação concluída;
3. envio de dados mínimos/documentação;
4. encaminhamento efetivo para especialista;
5. uplift contra baseline determinístico;
6. fairness de exposição entre segmentos sintéticos;
7. taxa de guardrails acionados;
8. taxa de decisões com log auditável completo;
9. distribuição de braços selecionados;
10. delayed reward observado por tipo de garantia.

Contratação simulada pode aparecer como métrica exploratória futura, mas não será a métrica principal do MVP.

## 11. Base pública inicial

A base pública inicial será **Bank Marketing**, do Kaggle, tratada como proxy de resposta a campanha bancária.

Uso pretendido:

- representar contexto de campanha, canal, contato e resposta;
- servir como base pública inicial para modelagem;
- receber enriquecimento sintético para empréstimos com garantia, braços, eventos e delayed rewards.

Cuidado obrigatório:

- a coluna `duration`, se presente, deve ser removida ou ignorada para decisão pré-interação por risco de vazamento temporal.

A documentação detalhada da base será feita em `data/kaggle/README.md`.

## 12. Política adaptativa principal

O MVP deve comparar:

1. baseline determinístico simples;
2. Thompson Sampling contextual simplificado.

O Thompson Sampling deve usar contexto sintético como:

- canal;
- tipo de garantia;
- segmento sintético;
- estágio da jornada.

UCB, LinUCB ou outras variações podem ser documentadas como alternativas futuras, mas não são obrigatórias como primeira implementação.

## 13. Delayed rewards

O MVP deve simular janelas de recompensa diferentes por tipo de garantia:

| Garantia | Janela sintética de delayed reward |
| --- | --- |
| Veículo | 2 a 20 dias |
| Imóvel | 7 a 45 dias |
| Investimentos | 1 a 15 dias |

Esse recorte permite demonstrar que a plataforma entende que crédito com garantia não possui recompensa instantânea e que cada colateral possui dinâmica própria.

## 14. Papel do LLM/RAG

No MVP, o LLM/RAG atua como camada de **explicação, governança e consulta documental**.

Ele pode apoiar:

- explicação de decisões;
- resumo de experimentos;
- recuperação de políticas sintéticas;
- consulta a reason codes;
- apoio à auditoria e governança.

Ele não deve:

- escolher braços;
- aprovar crédito;
- definir limite;
- definir taxa;
- substituir baseline, bandit ou política de elegibilidade;
- inventar política inexistente.

## 15. Governança mínima obrigatória

O MVP deve incluir, no mínimo:

- logs auditáveis por decisão;
- `policy_version`;
- `reason_codes`;
- `guardrails_triggered`;
- `requires_human_review`;
- braço `no_offer_now`;
- intended use documentado;
- usos fora de escopo documentados;
- lista de dados proibidos;
- política de pausa/rollback;
- aprovação humana antes de promover política;
- model card e system card, ainda que simples.

## 16. Não-objetivos do MVP

O MVP não deve:

1. aprovar crédito automaticamente;
2. calcular limite real de crédito;
3. precificar taxa real;
4. usar dados reais de clientes;
5. integrar com core bancário real;
6. usar atributos sensíveis;
7. substituir área de risco/compliance;
8. operar produção regulada;
9. prometer contratação final;
10. otimizar apenas clique ou conversão superficial.

## 17. Primeira interface demonstrável

A primeira interface demonstrável será uma **CLI**.

Exemplo futuro:

```bash
python -m adaptive_offer_lab decide examples/vehicle_simple.json
```

A CLI deve retornar uma decisão com:

- `decision_id`;
- `request_id`;
- próximo passo selecionado;
- `policy_version`;
- `reason_codes`;
- `requires_human_review`;
- `guardrails_triggered`;
- referência de log auditável.

Depois, a mesma lógica poderá evoluir para API REST e/ou app demonstrável.

## 18. Como o MVP será demonstrado para Lary

A demonstração deve conter três cenas mínimas:

### Cena 1 — Cliente digital simples

Cliente pessoa física com perfil sintético simples recebe recomendação para simulação de empréstimo com garantia de veículo no SuperApp.

Resultado esperado:

- próximo passo digital;
- baixa necessidade de revisão humana;
- reason codes compreensíveis;
- log auditável.

### Cena 2 — Garantia complexa

Cliente com contexto de imóvel ou relacionamento alto recebe encaminhamento para especialista/agência, em vez de oferta direta.

Resultado esperado:

- fluxo híbrido;
- `requires_human_review = true` quando aplicável;
- explicação de cautela;
- delayed reward mais longo.

### Cena 3 — Caso inelegível ou adversarial

Cliente com contexto incompleto, inelegível ou suspeito recebe `no_offer_now` ou conteúdo educativo.

Resultado esperado:

- guardrail registrado;
- ausência de promessa de crédito;
- decisão auditável.

## 19. Decisões futuras

Ficam para etapas posteriores:

- detalhamento completo dos braços em `docs/product/offer-arms.md`;
- schema sintético em `docs/data/synthetic-schema.md`;
- golden set em `data/golden_set/evaluation_cases.jsonl`;
- implementação do baseline determinístico;
- implementação do Thompson Sampling contextual simplificado;
- definição final do contrato da CLI;
- documentação de arquitetura Azure;
- model card, system card e plano LGPD;
- eventual inclusão de recebíveis sintéticos em versão futura.

## 20. Critério de pronto da Etapa 1

A Etapa 1 é considerada concluída porque este documento define:

- problema principal da BU de Lary;
- canal inicial;
- garantias dentro do MVP;
- garantias fora do MVP;
- métrica principal;
- métricas secundárias;
- braços candidatos em alto nível;
- não-objetivos;
- forma de demonstração;
- decisões futuras.
