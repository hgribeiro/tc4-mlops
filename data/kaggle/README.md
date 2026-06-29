# Base pública — Bank Marketing como proxy

## 1. Escolha da base

A base pública principal do MVP é **Bank Marketing**, tratada como proxy de resposta a campanha bancária e enriquecida com contexto sintético de **Empréstimos com Garantia**.

A base não é uma base de crédito com garantia. Ela não contém clientes reais do projeto, decisões de concessão, garantias, limites, taxas, propostas ou contratações. Seu uso no MVP é restrito a apoiar uma demonstração de experimentação e avaliação offline com dados públicos e sintéticos.

## 2. Fonte e referência

| Item | Definição para o MVP |
| --- | --- |
| Nome | Bank Marketing |
| Fonte canônica | UCI Machine Learning Repository — dataset ID 222 |
| Link UCI | https://archive.ics.uci.edu/dataset/222/bank |
| Link de download UCI | https://archive.ics.uci.edu/static/public/222/bank+marketing.zip |
| Espelho Kaggle recomendado | https://www.kaggle.com/datasets/marfrancolopez/bank-marketing |
| Arquivo recomendado | `bank-full.csv` quando disponível |
| Licença | UCI lista a base como **CC BY 4.0**. Espelhos Kaggle podem ter metadados próprios; verificar antes de redistribuir. |
| Citação original | Moro, Cortez e Rita — estudo de campanhas de marketing bancário direto. |
| Data de acesso documental | 2026-06-29 |

## 3. Target original

O target original é:

- `y`: indica se o cliente assinou um depósito a prazo (`yes`/`no`).

No MVP, `y` **não representa aprovação de crédito, contratação de empréstimo, limite, taxa ou proposta real**. Ele pode ser usado apenas como proxy histórico fraco de resposta a uma campanha bancária para experimentos offline ou geração de sinais sintéticos.

## 4. Colunas originais do arquivo `bank-full.csv`

| Coluna | Tipo original | Significado original | Uso no MVP |
| --- | --- | --- | --- |
| `age` | numérico | idade | Não usar para decisão. Pode induzir discriminação ou segmentação indevida. |
| `job` | categórico | ocupação | Não usar para decisão do MVP. Pode funcionar como proxy socioeconômico. |
| `marital` | categórico | estado civil | Proibido para decisão. Não é necessário para próximo passo responsável. |
| `education` | categórico | escolaridade | Não usar para decisão. Pode funcionar como proxy sensível/socioeconômico. |
| `default` | binário | inadimplência declarada | Não usar como regra de crédito real. Se usado em análise exploratória, documentar como proxy público e sintético. |
| `balance` | numérico | saldo médio anual em euros | Não usar como renda ou patrimônio. Proibido tratar como dado financeiro real do MVP. |
| `housing` | binário | possui financiamento habitacional | Não usar como regra de elegibilidade real. Pode ser descartado na primeira versão. |
| `loan` | binário | possui empréstimo pessoal | Não usar como regra de elegibilidade real. Pode ser descartado na primeira versão. |
| `contact` | categórico | tipo de contato | Pode inspirar `channel`, com mapeamento sintético e documentação de limitações. |
| `day` | numérico | dia do último contato | Não usar para decisão pré-interação sem validação temporal. |
| `month` | categórico | mês do último contato | Não usar para decisão pré-interação sem validação temporal. |
| `duration` | numérico | duração do último contato em segundos | **Remover ou ignorar sempre para decisão pré-interação por vazamento temporal.** |
| `campaign` | numérico | contatos na campanha atual | Pode inspirar `contact_repetition_count`, com limites sintéticos. |
| `pdays` | numérico | dias desde campanha anterior | Pode inspirar recência sintética, se disponível antes da decisão. |
| `previous` | numérico | contatos antes da campanha atual | Pode inspirar histórico sintético de contato. |
| `poutcome` | categórico | resultado da campanha anterior | Pode inspirar engajamento sintético, se tratado como histórico anterior. |
| `y` | binário | assinou depósito a prazo | Target original; não usar como feature de decisão. |

## 5. Regra obrigatória contra vazamento temporal

A coluna `duration` mede a duração do último contato da campanha. Essa informação só é conhecida **depois** da interação acontecer. Portanto, ela vaza informação sobre o resultado e não pode orientar uma decisão tomada antes do contato.

Regras do MVP:

1. `duration` deve ser removida de qualquer dataset de features pré-interação.
2. `duration` não pode alimentar baseline, política adaptativa, seleção de braço, guardrail ou reason code.
3. Se preservada no arquivo bruto, deve ficar apenas em área raw, nunca em dataset preparado para decisão.
4. Testes, notebooks e documentação devem tratar `duration` como campo proibido para decisão pré-interação.

## 6. Limitações da base

- A base é sobre marketing de depósito a prazo, não sobre crédito com garantia.
- O target `y` mede assinatura de depósito, não proposta qualificada simulada.
- A base não contém garantias como veículo, imóvel ou investimentos.
- A base não contém canal SuperApp, especialista/agência ou fluxo híbrido como definidos no MVP.
- A base pode conter atributos que não devem ser usados para decisão responsável, como idade, ocupação, estado civil, escolaridade e saldo.
- O contexto temporal da campanha original não representa uma jornada moderna de crédito digital.
- A base não deve ser usada para inferir risco de crédito real, renda, patrimônio, propensão individual real ou política bancária privada.

## 7. Enriquecimento sintético permitido

A base pública pode ser enriquecida com campos sintéticos definidos em `docs/data/synthetic-schema.md`, incluindo:

- `collateral_type`: `vehicle`, `home`, `investment`;
- `channel`: `superapp`, `branch`, `specialist`, `hybrid`;
- `journey_stage`;
- `synthetic_risk_level`;
- `policy_confidence`;
- `engagement_level`;
- `context_completeness`;
- `synthetic_segment` não sensível;
- `relationship_tier`;
- `contact_repetition_count`;
- campos mínimos de auditoria e linhagem.

Esse enriquecimento deve ser reproduzível por semente aleatória e não pode afirmar que os campos sintéticos vieram da instituição original.

## 8. Dados proibidos

Não incluir no MVP:

- CPF, nome, e-mail, telefone, endereço ou identificadores pessoais reais;
- dados reais de cliente, renda, patrimônio, investimentos, veículo ou imóvel;
- gênero, raça, religião, saúde, orientação sexual ou outros atributos sensíveis;
- proxies indevidos para atributos sensíveis;
- regras comerciais privadas de bancos;
- decisões reais de aprovação, limite, taxa, contratação ou cobrança.

## 9. Recebíveis sintéticos

`synthetic_receivables` e fluxos de recebíveis ficam **fora do MVP inicial**. Eles podem ser estudados como evolução futura, por exigirem contexto de pessoa jurídica, fluxo de caixa sintético e novas regras de governança.

## 10. Instruções de download

### Opção A — UCI canônico

```bash
mkdir -p data/kaggle/raw
curl -L "https://archive.ics.uci.edu/static/public/222/bank+marketing.zip" \
  -o data/kaggle/raw/bank-marketing.zip
unzip data/kaggle/raw/bank-marketing.zip -d data/kaggle/raw/bank-marketing
```

### Opção B — Kaggle CLI

Antes, configurar credenciais do Kaggle conforme a documentação oficial do Kaggle.

```bash
mkdir -p data/kaggle/raw
kaggle datasets download \
  -d marfrancolopez/bank-marketing \
  -p data/kaggle/raw \
  --unzip
```

## 11. Convenção de armazenamento

- `data/kaggle/raw/`: arquivos baixados sem alteração, não necessários para commit.
- `data/kaggle/processed/`: datasets preparados sem `duration` e sem campos proibidos.
- `data/kaggle/README.md`: documentação de fonte, limitações e regras de uso.

O repositório deve conseguir explicar a decisão sem versionar dados brutos grandes ou dados que possam induzir uso indevido.
