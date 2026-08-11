# Experimento offline — baseline e Thompson Sampling contextual

## Objetivo e limite de validade

Este experimento compara um **baseline experimental fixo** com uma **Política Adaptativa Thompson Sampling** em um ambiente sintético reproduzível. Ele demonstra aprendizado técnico sob um contrato conhecido; **não** estima efeito causal, propensão real a crédito com garantia nem desempenho em produção bancária.

A Bank Marketing fornece apenas features públicas minimizadas e o target `y` como proxy factual de resposta. A base não contém resultados contrafactuais por Braço. Por isso, contextos de Empréstimos com Garantia e recompensas multi-Braço são simulados de forma explícita.

`duration`, dados pessoais, atributos sensíveis e variáveis financeiras proibidas não entram nas features preparadas nem no contexto da política.

## Interface executável

```bash
PYTHONPATH=src python -m responsible_next_step experiment \
  --input data/kaggle/raw/bank-marketing/bank-full.csv \
  --output-dir artifacts/official-experiment \
  --seeds 11,29,47,71,97 \
  --horizon 45211 \
  --tracking-uri sqlite:///mlflow.db \
  --omit-evaluation-decisions \
  --pretty
```

A publicação oficial gera:

- `report.json`: configuração, linhagem, métricas agregadas e resultados por seed;
- `policy.json`: versão, schema, Braços, contexto, priors e posteriors da última seed declarada;
- `provenance.json`: fonte, hash, preparação, configuração, cobertura e hashes dos artefatos;
- um run no experimento MLflow `responsible-next-step-offline`.

O run registra base/versão/hash, seeds, horizonte, baseline, algoritmo, priors, métricas comparativas e exposição por Braço. A opção `--omit-evaluation-decisions` evita publicar ou versionar o log volumoso; sem ela, execuções locais também produzem `evaluation_decisions.jsonl`. Somente os três JSON derivados aprovados em `artifacts/official-experiment/` entram no Git. A UI local pode ser aberta com:

```bash
mlflow ui --backend-store-uri sqlite:///mlflow.db --port 5000
```

O estado local (`mlflow.db`, `mlartifacts/` e `mlruns/`) e a base bruta não devem ser versionados. O conjunto oficial pode ser validado sem download ou rede:

```bash
PYTHONPATH=src python -m responsible_next_step validate-experiment-artifacts \
  --artifact-dir artifacts/official-experiment \
  --pretty
```

O validador confirma schemas atuais, hashes, 45.211 linhas, cinco seeds, horizonte, exclusão de `duration`, cobertura de contextos/Braços e classificação sintética, offline e não causal.

## Contexto sintético

A política usa somente:

- `collateral_type`;
- `channel`;
- `synthetic_segment`;
- `journey_stage`.

O enriquecimento é determinístico:

| Proxy preparado | Contexto sintético |
| --- | --- |
| `contact_channel_proxy = cellular` | veículo e SuperApp |
| `contact_channel_proxy = telephone` | imóvel e híbrido |
| outro contato | investimentos e especialista |
| `previous_outcome = success` | segmento `digital_simple`, estágio `simulation` |
| contatos anteriores sem sucesso | `documentation_needed`, estágio `documentation` |
| sem histórico anterior | `education_first`, estágio `awareness` |

Essas associações são hipóteses de laboratório, não fatos sobre clientes ou produtos reais.

## Guardrails e conjunto elegível

Guardrails são aplicados antes das duas políticas. `no_offer_now` permanece sempre disponível. Repetição sintética igual ou superior a 10 bloqueia exploração e deixa apenas `no_offer_now` elegível.

Nos demais casos:

- `awareness`: educação ou `no_offer_now`;
- `documentation`: educação, documentos, especialista ou `no_offer_now`;
- `simulation`: simulação compatível com a garantia, educação, eventual especialista e `no_offer_now`.

A escolha adaptativa é feita estritamente dentro desse conjunto.

## Ambiente de recompensa

A recompensa é binária e representa **avanço qualificado sintético da jornada**, não clique, aprovação ou contratação. O target público `y` adiciona `0,06` à probabilidade de ações diferentes de `no_offer_now`, mas é usado apenas pelo ambiente após a escolha; nunca é feature da política.

Probabilidades centrais:

| Contexto/Ação | Probabilidade sintética |
| --- | ---: |
| awareness + conteúdo educativo | 0,78 |
| awareness + demais Braços elegíveis | 0,10 |
| documentation + solicitar documentos | 0,82 |
| documentation + especialista | 0,48 |
| documentation + conteúdo educativo | 0,16 |
| documentation + demais Braços elegíveis | 0,04 |
| simulation/veículo + simulação de veículo | 0,86 |
| simulation/veículo + demais Braços elegíveis | 0,14 |
| simulation/imóvel + especialista | 0,82 |
| simulation/imóvel + demais Braços elegíveis | 0,28 |
| simulation/investimentos + especialista | 0,80 |
| simulation/investimentos + demais Braços elegíveis | 0,25 |
| repetição bloqueada + `no_offer_now` | 0,80 |
| `no_offer_now` sem bloqueio | 0,03 |
| fallback fora das condições anteriores | 0,03 |

Se `y = yes`, ações diferentes de `no_offer_now` recebem incremento de `0,06`. Toda probabilidade é limitada ao intervalo de `0,01` a `0,95`. O sorteio contrafactual é derivado de SHA-256 sobre seed, passo e Braço; baseline e adaptativo veem o mesmo contexto e o mesmo resultado potencial para uma mesma ação. Resultados forçados por guardrail são auditados, mas não atualizam o posterior adaptativo do contexto não bloqueado.

## Políticas

### Baseline experimental

O baseline escolhe conteúdo educativo quando elegível e usa o primeiro fallback seguro quando não está. Ele é deliberadamente simples e separado do Baseline Determinístico responsável da CLI `decide`.

### Thompson Sampling contextual

Cada combinação de contexto e Braço elegível mantém posterior Beta independente, iniciado em `Beta(1, 1)`. Em cada decisão:

1. calcula-se o conjunto elegível após guardrails;
2. amostra-se uma probabilidade de cada posterior elegível;
3. seleciona-se a maior amostra;
4. observa-se a recompensa binária simulada;
5. atualiza-se `alpha` em caso de sucesso ou `beta` em caso de insucesso.

### Uso do artefato na decisão demonstrável

O `policy.json` pode ser carregado pelo comando público `decide` com `--policy adaptive --policy-artifact <caminho>`. Antes do uso, a CLI valida schema, versão, Braços, contexto, priors, posteriors, seed e as declarações de segurança. A decisão aplica os Guardrails responsáveis da CLI primeiro e amostra somente entre os Braços resultantes como elegíveis. O `policy_version` do artefato é preservado tanto na resposta quanto no log auditável.

Artefatos ausentes, malformados ou incompatíveis falham explicitamente com status `2`; não há fallback silencioso nem desativação de Guardrails. O fallback seguro documentado é uma nova execução no modo baseline, que permanece o padrão quando `--policy` não é informado. O carregamento do artefato não realiza aprendizado online nem promove políticas automaticamente.

## Métricas

O relatório inclui, por seed e em agregado:

- recompensa do baseline e adaptativa;
- uplift absoluto;
- recompensa acumulada;
- regret acumulado contra a melhor ação elegível conhecida pelo simulador;
- taxa de exploração, definida como escolha diferente do maior valor médio posterior antes da amostragem;
- exposição por Braço.

A recompensa representa avanço qualificado sintético da jornada, mas não é chamada de Proposta Qualificada Simulada porque o ambiente simplificado não comprova simultaneamente conclusão de simulação e fornecimento de dados/documentação. A comparação usa múltiplas seeds declaradas e reporta média e dispersão do uplift. Não se escolhe apenas uma execução favorável.

## Não-objetivos

Ficam fora deste experimento: delayed rewards complexos, eventos censurados, fairness detalhada, tracking remoto, aprendizado online durante a decisão, promoção automática de políticas e qualquer alegação de prontidão regulada. Esses itens são tratados separadamente no backlog realinhado.
