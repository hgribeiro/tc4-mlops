# Roteiro de pitch — Demo Day em até cinco minutos

## Objetivo e preparação

Apresentar a Lary e à banca um laboratório reproduzível de **Próximo Passo Responsável**, distinguindo recomendação, Simulação, Proposta Qualificada Simulada, Aprovação e Contratação, sem prometer taxa ou limite real. Tempo planejado: **4min50s**, deixando 10 segundos de margem.

Antes de gravar:

1. instalar o projeto com `python -m pip install -e .`;
2. regenerar o experimento com as seeds declaradas;
3. confirmar `5/5` no Golden Set e executar `uv run --with pytest pytest` (ou `python -m pytest` em um ambiente que tenha pytest);
4. abrir o MLflow em `http://127.0.0.1:5000`;
5. deixar três terminais prontos para veículo, imóvel e caso adversarial;
6. manter `docs/demo/saidas-contingencia.md` e `artifacts/experiment/report.json` abertos.

## Roteiro timeboxed

### 0:00–0:35 — Problema e limite

**Fala:**

> Regras fixas aprendem devagar e podem recomendar uma ação inadequada. Nosso laboratório escolhe o Próximo Passo Responsável para Clientes Sintéticos em jornadas de empréstimos com garantia. Ele pode iniciar uma Simulação, educar, pedir documentos, chamar um especialista ou não ofertar. A recomendação não é Proposta Qualificada Simulada, não aprova crédito, não contrata e não calcula taxa ou limite real.

**Tela:** objetivo e não-objetivos no `README.md`.

### 0:35–1:15 — Dados e preparação

**Fala:**

> Usamos a Bank Marketing, referenciada no Kaggle e na UCI, somente como proxy público de resposta. A base não descreve empréstimos com garantia. A preparação remove `duration`, conhecida apenas depois do contato, e também exclui atributos pessoais, sensíveis ou financeiros proibidos. O notebook reutiliza o mesmo módulo da CLI e registra fonte, hash e seed.

**Tela:** seção de dados do README e resumo executado do notebook. Não aguardar download ou execução completa durante o pitch.

### 1:15–2:05 — Baseline versus Política Adaptativa

**Fala:**

> Comparamos um baseline experimental fixo com Thompson Sampling contextual e priors Beta um-um. Guardrails definem primeiro quais Braços são seguros; a política só explora dentro desse conjunto. No artefato reproduzível de demonstração, em três seeds e 400 decisões por seed, a recompensa simulada média passou de 206,67 para 303,67: uplift absoluto de 97, com exploração de 8,22%. Todas as recompensas são sintéticas, offline e não causais.

**Tela:** `artifacts/experiment/report.json`, destacando `seeds`, `reward_contract` e `metrics`.

### 2:05–2:35 — Evidência MLOps

**Fala:**

> O MLflow registra dataset, algoritmo, priors, horizonte, seeds, recompensa, uplift, regret, exploração e exposição por Braço. O run também preserva o relatório e o `policy.json` versionado. Não existe promoção automática: testes, Golden Set e aprovação humana antecedem o uso; rollback restaura o Baseline Determinístico.

**Tela:** um run já aberto na UI do MLflow, nas abas de parâmetros, métricas e artefatos.

### 2:35–4:20 — Interface e três cenas

Executar ou mostrar as saídas preparadas.

**Cena 1 — veículo digital simples:**

```bash
PYTHONPATH=src python -m responsible_next_step decide \
  --input examples/synthetic-customers/vehicle-simple.json \
  --audit-log-dir logs/decisions --pretty
```

**Fala:**

> O baseline recomenda `simulate_vehicle_secured_loan` no SuperApp. A saída traz `baseline_deterministic_v0.1`, Reason Codes, ausência de Guardrails, `requires_human_review = false` e referência para o log auditável.

**Cena 2 — imóvel complexo e Humano no Loop:**

```bash
PYTHONPATH=src python -m responsible_next_step decide \
  --input examples/synthetic-customers/home-complex.json \
  --audit-log-dir logs/decisions --pretty
```

**Fala:**

> Para imóvel complexo e baixa confiança, o próximo passo é `route_to_specialist`, com `requires_human_review = true`. A plataforma não força autosserviço em um contexto sensível.

**Cena 3 — caso adversarial:**

```bash
PYTHONPATH=src python -m responsible_next_step decide \
  --input examples/synthetic-customers/guardrail-sensitive.json \
  --audit-log-dir logs/decisions --pretty
```

**Fala:**

> Com risco crítico, o Guardrail `adversarial_or_unsafe_context` restringe a decisão a `no_offer_now`. O log registra por que nenhuma simulação foi exposta.

**Conexão com a Política Adaptativa:** mostrar `policy_version = contextual_thompson_sampling_v0.1` em uma saída adaptativa previamente preparada ou executar:

```bash
PYTHONPATH=src python -m responsible_next_step decide \
  --input examples/synthetic-customers/vehicle-simple.json \
  --policy adaptive \
  --policy-artifact artifacts/experiment/policy.json \
  --audit-log-dir logs/decisions --pretty
```

Explicar que baseline e adaptativo podem escolher ações diferentes, mas ambos preservam o conjunto elegível, Guardrails e auditoria. Não interpretar uma decisão individual como prova de uplift.

### 4:20–4:50 — Evidência de execução, limitações e fechamento

**Fala:**

> A prova cloud também tem três rótulos: AWS live foi executada no #25 e está hoje offline/destroyed após o #27; LocalStack reproduz apenas API Gateway REST, Lambda ZIP e S3; contingência é uma resposta estática versionada, sempre confirmada. Azure é equivalência conceitual, não deployment. EventBridge/SQS/worker de Delayed Rewards não foram provisionados e ficam para evolução futura.

**Tela:** apêndice de arquitetura AWS, `docs/demo/acceptance-final.md` e status AO VIVO/CONTINGÊNCIA do deck.

**Fala:**

> O Golden Set passa em cinco casos, mas tem cobertura pequena. A base é proxy de depósito a prazo e as recompensas são simuladas, offline e não causais; delayed rewards complexos e validação regulatória continuam fora do MVP. O resultado demonstra um ciclo MLOps auditável, não eficácia causal nem prontidão para produção bancária. Para Lary, o valor está em aprender contra um baseline sem perder explicação, Humano no Loop e rollback.

## Plano de contingência

Se uma execução ao vivo falhar:

1. não depurar durante o pitch;
2. mostrar as saídas versionadas em `docs/demo/saidas-contingencia.md`;
3. mostrar a comparação previamente salva em `docs/demo/saidas-contingencia.md`; se os artefatos locais estiverem disponíveis, complementar com `artifacts/experiment/report.json` e `artifacts/experiment/policy.json`;
4. usar uma captura ou gravação local da UI do MLflow preparada antes da apresentação;
5. explicar em uma frase que o material é uma execução previamente salva com a mesma versão e as mesmas seeds;
6. continuar a partir do timebox seguinte.

Se apenas o MLflow falhar, mostrar no JSON os parâmetros, as métricas e `experiment_ref`. Se a CLI falhar, usar as três saídas resumidas e apontar os campos `policy_version`, `reason_codes`, `guardrails_triggered`, `requires_human_review` e `audit_log_ref`. Se todo o ambiente local falhar, reproduzir o vídeo previamente gravado de até cinco minutos.

## Critério de pronto antes de enviar o vídeo

- duração final menor ou igual a cinco minutos;
- problema, dados, baseline, adaptativo, MLflow e interface aparecem;
- as três cenas responsáveis são visíveis;
- pelo menos uma saída mostra `policy_version`, Reason Codes e referência de auditoria;
- Humano no Loop e Guardrail aparecem em cenas distintas;
- recompensas são chamadas de simuladas;
- as falas distinguem recomendação, Simulação, Proposta Qualificada Simulada, Aprovação e Contratação;
- nenhuma fala promete Aprovação, Contratação, taxa ou limite real;
- AWS live, LocalStack e contingência são rotulados sem ambiguidade;
- contingência foi testada sem rede;
- arquitetura AWS e seus limites aparecem no apêndice.
