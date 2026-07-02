# Responsible Next Step Lab — MLOps para Empréstimos com Garantia

Plataforma demonstrável de **MLE/MLOps e IA generativa** para decidir o **Próximo Passo Responsável** em jornadas sintéticas de **Empréstimos com Garantia**.

O projeto simula uma plataforma de experimentação adaptativa para a persona **Lary**, CTO da unidade de negócio de Empréstimos com Garantia de um banco digital. A solução compara um baseline determinístico com uma política adaptativa, mantendo governança, explicabilidade, logs auditáveis e limites claros de uso.

> Este repositório **não** implementa um sistema bancário real, não aprova crédito, não calcula limite, não precifica taxa e não usa dados reais de clientes.

## Sumário

- [Objetivo](#objetivo)
- [Escopo do MVP](#escopo-do-mvp)
- [Arquitetura conceitual](#arquitetura-conceitual)
- [Dados](#dados)
- [MLOps e governança](#mlops-e-governança)
- [Estrutura do repositório](#estrutura-do-repositório)
- [Como começar](#como-começar)
- [Qualidade de engenharia](#qualidade-de-engenharia)
- [Roadmap](#roadmap)
- [Limitações e não-objetivos](#limitações-e-não-objetivos)

## Objetivo

Ajudar uma unidade de Empréstimos com Garantia a aumentar **Propostas Qualificadas Simuladas** por decisão, escolhendo um próximo passo responsável para um **Cliente Sintético**, considerando:

- tipo de garantia: veículo, imóvel ou investimentos;
- canal: SuperApp, especialista/agência ou fluxo híbrido;
- estágio da jornada;
- risco sintético;
- completude de contexto;
- guardrails;
- humano no loop;
- delayed rewards;
- avaliação offline contra baseline.

A decisão não é “qual oferta vender”, mas sim qual ação de jornada tomar com segurança: simular, educar, solicitar documentação, encaminhar para especialista ou não ofertar naquele momento.

## Escopo do MVP

### Garantias no escopo

| Garantia | Papel no MVP |
| --- | --- |
| Veículo | Jornada digital simples, adequada ao SuperApp. |
| Imóvel | Jornada mais complexa, com maior chance de revisão humana. |
| Investimentos | Jornada para cliente sintético de maior relacionamento, com comunicação cuidadosa. |

### Fora do MVP inicial

- recebíveis sintéticos;
- pessoa jurídica;
- dados reais de clientes;
- aprovação, contratação, limite ou taxa real de crédito;
- operação produtiva regulada.

### Braços canônicos

- `simulate_vehicle_secured_loan`
- `simulate_home_equity`
- `simulate_investment_secured_loan`
- `educational_content_secured_credit`
- `request_documents`
- `route_to_specialist`
- `no_offer_now`

`no_offer_now` deve estar sempre disponível para impedir que a política seja forçada a simular ou vender quando não houver ação responsável.

## Arquitetura conceitual

```mermaid
flowchart LR
    A[Cliente Sintético] --> B[Validação de schema]
    B --> C[Guardrails]
    C --> D{Há ações seguras?}
    D -- não --> E[no_offer_now]
    D -- sim --> F[Baseline determinístico]
    D -- sim --> G[Política adaptativa]
    F --> H[Decisão auditável]
    G --> H
    E --> H
    H --> I[Log minimizado]
    H --> J[Avaliação offline]
    J --> K[Métricas de MLOps]
```

Contrato mínimo esperado de uma decisão:

```json
{
  "decision_id": "dec_001",
  "request_id": "req_001",
  "selected_action": "simulate_vehicle_secured_loan",
  "policy_version": "baseline_v0.1",
  "reason_codes": ["vehicle_collateral_anchor", "digital_channel_fit"],
  "guardrails_triggered": [],
  "requires_human_review": false,
  "audit_log_ref": "logs/decisions/2026-06-29.jsonl",
  "not_credit_approval": true,
  "requires_formal_credit_analysis": true
}
```

## Dados

A base pública inicial é **Bank Marketing**, usada apenas como proxy público de resposta a campanha bancária.

Documentação principal:

- [`data/kaggle/README.md`](data/kaggle/README.md): fonte, licença, target, colunas, limitações e download.
- [`docs/data/synthetic-schema.md`](docs/data/synthetic-schema.md): schema mínimo do Cliente Sintético e dados auxiliares.

Boas práticas adotadas:

- dados brutos ficam fora do versionamento sempre que possível;
- a coluna `duration` da Bank Marketing é removida/ignorada para decisão pré-interação por vazamento temporal;
- atributos sensíveis, identificadores pessoais, renda real, patrimônio real e regras comerciais privadas são proibidos;
- enriquecimento sintético deve ser reproduzível por semente aleatória;
- logs devem seguir minimização de dados.

Estrutura esperada de dados:

```text
data/
  kaggle/
    README.md
    raw/                 # não versionar dados brutos grandes
    processed/           # dados preparados sem vazamento temporal
  golden_set/
    evaluation_cases.jsonl
```

## MLOps e governança

O projeto deve tratar políticas de decisão como artefatos versionados.

Fluxo alvo:

1. definir ou atualizar catálogo de braços;
2. validar schema e guardrails;
3. rodar baseline determinístico;
4. rodar política adaptativa em avaliação offline;
5. comparar métricas contra baseline;
6. revisar fairness, exploração, regret e guardrails;
7. exigir aprovação humana antes de promoção;
8. monitorar decisões, recompensas e drift;
9. permitir pausa ou rollback.

Métricas esperadas:

- uplift contra baseline;
- recompensa acumulada;
- regret acumulado;
- taxa de exploração;
- conversão qualificada simulada;
- proposta qualificada simulada;
- exposição por braço;
- fairness por segmento sintético;
- taxa de guardrails acionados;
- cobertura de logs auditáveis.

LLM/RAG pode apoiar explicação, consulta documental e governança, mas **não** escolhe braço, não aprova crédito e não substitui guardrails ou reason codes.

## Estrutura do repositório

```text
.
├── CONTEXT.md                         # Linguagem canônica do domínio
├── AGENTS.md                          # Instruções para agentes neste repositório
├── data/
│   └── kaggle/
│       └── README.md                  # Documentação da base pública
├── docs/
│   ├── adr/                           # Decisões arquiteturais
│   ├── agents/                        # Operação com issues e agentes
│   ├── data/                          # Schemas e contratos de dados
│   ├── decisions/                     # Decisões de produto/domínio
│   ├── product/                       # PRD, MVP e catálogo de braços
│   └── research/                      # Pesquisa de mercado e domínio
└── personas/
    └── lary-cto-bu-loan/              # Persona principal do projeto
```

Documentos essenciais:

- [`docs/product/prd-proximo-passo-responsavel.md`](docs/product/prd-proximo-passo-responsavel.md)
- [`docs/product/mvp-lary.md`](docs/product/mvp-lary.md)
- [`docs/product/offer-arms.md`](docs/product/offer-arms.md)
- [`docs/decisions/003-checklist-planejamento-mvp-lary.md`](docs/decisions/003-checklist-planejamento-mvp-lary.md)
- [`personas/lary-cto-bu-loan/SOUL.md`](personas/lary-cto-bu-loan/SOUL.md)

## Como começar

### Pré-requisitos atuais

- Python 3.10+;
- opcional: ambiente virtual local;
- Kaggle CLI ou download direto da UCI para dados públicos, apenas quando os dados forem necessários.

A primeira interface executável é uma CLI Python sem dependências externas. Ela recebe um **Cliente Sintético** em JSON, aplica guardrails, usa um baseline determinístico inicial e grava log auditável minimizado.

### Executar a primeira decisão demonstrável

Sem instalar o pacote:

```bash
PYTHONPATH=src python -m responsible_next_step decide \
  --input examples/synthetic-customers/vehicle-simple.json \
  --audit-log-dir logs/decisions \
  --pretty
```

Opcionalmente, instalar em modo editável para usar o comando console:

```bash
python -m pip install -e .
responsible-next-step decide \
  --input examples/synthetic-customers/vehicle-simple.json \
  --audit-log-dir logs/decisions \
  --pretty
```

A documentação detalhada da primeira cena está em [`docs/demo/cena-1-veiculo-digital.md`](docs/demo/cena-1-veiculo-digital.md).

Exemplos adicionais:

```bash
PYTHONPATH=src python -m responsible_next_step decide \
  --input examples/synthetic-customers/home-complex.json \
  --audit-log-dir logs/decisions \
  --pretty

PYTHONPATH=src python -m responsible_next_step decide \
  --input examples/synthetic-customers/guardrail-sensitive.json \
  --audit-log-dir logs/decisions \
  --pretty
```

A saída inclui `decision_id`, `request_id`, `selected_action`, `policy_version`, `reason_codes`, `requires_human_review`, `guardrails_triggered`, `audit_log_ref` e flags explícitas de que a decisão **não é aprovação**, **não é contratação**, **não define taxa** e **não define limite real**.

### Baixar a base pública

Opção UCI:

```bash
mkdir -p data/kaggle/raw
curl -L "https://archive.ics.uci.edu/static/public/222/bank+marketing.zip" \
  -o data/kaggle/raw/bank-marketing.zip
unzip data/kaggle/raw/bank-marketing.zip -d data/kaggle/raw/bank-marketing
```

Opção Kaggle CLI:

```bash
mkdir -p data/kaggle/raw
kaggle datasets download \
  -d marfrancolopez/bank-marketing \
  -p data/kaggle/raw \
  --unzip
```

Antes de usar qualquer dado para decisão pré-interação, remover ou ignorar `duration`.

## Qualidade de engenharia

Padrões esperados para implementação futura:

### Software engineering

- contratos públicos estáveis para CLI/API;
- módulos pequenos, com fronteiras claras entre dados, política, guardrails, avaliação e interface;
- testes de aceitação no nível do contrato de decisão;
- versionamento semântico de políticas e schemas;
- logs estruturados e minimizados;
- configuração por ambiente, sem segredos no repositório.

### Data engineering

- separação entre `raw`, `processed` e dados sintéticos;
- validação explícita de schema;
- bloqueio de colunas com vazamento temporal;
- linhagem de dados e semente de geração sintética;
- documentação de limitações da fonte pública;
- datasets derivados reproduzíveis por comando.

### ML/MLOps

- baseline determinístico obrigatório antes da política adaptativa;
- avaliação offline reproduzível;
- golden set versionado;
- métricas além de clique ou conversão superficial;
- controle de exploração apenas entre braços elegíveis e seguros;
- aprovação humana, pausa e rollback antes de qualquer promoção de política.

## Roadmap

Estado atual:

- [x] persona Lary documentada;
- [x] MVP narrativo documentado;
- [x] catálogo de braços documentado;
- [x] base pública documentada;
- [x] schema mínimo do Cliente Sintético documentado.

Próximas entregas recomendadas:

- [ ] criar `data/golden_set/evaluation_cases.jsonl`;
- [x] implementar baseline determinístico inicial;
- [x] implementar CLI de decisão;
- [x] criar testes de aceitação do contrato da CLI;
- [ ] implementar avaliação offline;
- [ ] implementar Thompson Sampling contextual simplificado;
- [ ] criar `docs/model-card.md`, `docs/system-card.md` e `docs/lgpd-plan.md`;
- [ ] documentar arquitetura Azure e plano de MLOps;
- [ ] criar roteiro de demo para Lary.

## Limitações e não-objetivos

Este projeto não deve ser interpretado como:

- motor de aprovação automática de crédito;
- política real de concessão;
- precificador de taxa ou limite;
- recomendador de investimento;
- substituto de risco, jurídico ou compliance;
- integração com core bancário real;
- sistema pronto para produção regulada.

Todo resultado é sintético, demonstrativo e voltado a aprendizado, governança e avaliação offline.

## Licença e dados de terceiros

A licença do código deste repositório deve ser definida pelo mantenedor antes de qualquer distribuição ampla.

A base Bank Marketing pertence à sua fonte original e deve ser usada conforme a licença e termos indicados pela UCI/Kaggle. Consulte [`data/kaggle/README.md`](data/kaggle/README.md) antes de baixar, processar ou redistribuir dados.
