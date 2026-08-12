# Runbook do operador — demonstração final

Este runbook permite repetir a demonstração sem inferir recursos ou credenciais. Use somente dados sintéticos. **Estado atual:** os recursos temporários AWS estão destruídos; persistem bootstrap/state, OIDC/roles/permissions boundary e Budget. Não execute `apply` ou `destroy` para esta revisão final.

## 1. Demo local e LocalStack

```bash
python -m pip install -e '.[test]'
./scripts/local-demo.sh start
# smoke automático: decisão, contrato e objeto S3 minimizado
./scripts/local-demo.sh cleanup
```

O LocalStack Community prova somente API Gateway REST → Lambda ZIP → S3. Não representa CloudFront, ECR/Lambda por imagem, CloudWatch ou IAM/OIDC AWS. Se o smoke falhar, registre o bloqueio; não o chame de smoke AWS.

Para executar o deck offline:

```bash
cd presentation
npm ci
npx playwright install chromium  # primeira execução, se necessário
npm test
npm run build
```

Abra `presentation/dist/index.html` sem rede. O modo **AO VIVO** do deck significa uma API publicada disponível (historicamente AWS); **CONTINGÊNCIA** é estática, versionada e exige confirmação. Nunca troque de modo silenciosamente.

## 2. Conta e bootstrap (somente operador autorizado)

O fluxo de conta exige MFA no root, nenhuma Access Key root, IAM Identity Center/SSO e AWS CLI v2. Configure um perfil SSO e confirme a identidade:

```bash
export AWS_PROFILE=tc4-bootstrap-admin
aws sso login --profile "$AWS_PROFILE"
aws sts get-caller-identity --profile "$AWS_PROFILE"
```

Aplique/recupere o bootstrap somente seguindo [`docs/aws-bootstrap.md`](../aws-bootstrap.md). Ele usa state separado (`bootstrap/terraform.tfstate`) e não deve ser destruído pelo ciclo da demo. O Budget `tc4-mlops-demo-monthly-usd30` alerta em 80%/100%; é consultivo, não bloqueia gastos.

## 3. Quality gates antes de qualquer deploy

```bash
PYTHONPATH=src python -m pytest
PYTHONPATH=src python -m responsible_next_step evaluate-golden-set \
  --input data/golden_set/evaluation_cases.jsonl --audit-log-dir /tmp/tc4-golden-set
PYTHONPATH=src python -m responsible_next_step validate-experiment-artifacts \
  --artifact-dir artifacts/official-experiment
cd presentation && npm test && cd ..
terraform fmt -check -recursive
for d in infrastructure/environments/bootstrap infrastructure/environments/demo infrastructure/modules/demo-api; do
  terraform -chdir="$d" init -backend=false
  terraform -chdir="$d" validate
  terraform -chdir="$d" test
 done
actionlint .github/workflows/*.yml
shellcheck scripts/*.sh
```

Comandos externos podem estar indisponíveis; registre `not run` em vez de converter validação parcial em evidência. Confira links Markdown, assets do deck e `git diff --check`.

## 4. Promoção e deploy AWS (não executar agora)

A integração oficial usa `develop` e um PR `develop` → `main`. O PR é a superfície de aprovação humana: qualidade e o Terraform plan não mutante devem passar, e o branch protection exige os contextos `quality / software, evidence, deck and Terraform` e `plan / non-mutating demo Terraform plan` com branch atualizada. O merge manual do PR gera um push em `main` e inicia automaticamente o deploy; PRs e pushes em `develop` nunca fazem deploy. O environment `demo` mantém OIDC e deployment branch policy apenas para `main`, sem uma segunda aprovação de reviewer.

Após a revisão humana e o merge do PR, o workflow cria o ambiente temporário. Não execute `apply` durante esta implementação; o script abaixo é somente referência operacional:

```bash
export AWS_PROFILE=coding-agent
COMMIT_SHA="$(git rev-parse HEAD)" LOW_QUOTA_MODE=true scripts/deploy-demo-aws.sh
```

O script exige a conta/região esperadas, imagem ECR imutável por SHA, tags de expiração e smoke. `LOW_QUOTA_MODE=true` é necessário enquanto `ConcurrentExecutions=10` e a solicitação `57e948cf306c4d08a0deb6927b2c85fauYwF6wh6` / case `178649843100746` estiver `CASE_OPENED`; após aumento aprovado, a reserva padrão pode ser restaurada. Não criar serviços adicionais nem usar `latest`.

## 5. Smoke e apresentação

O smoke AWS esperado cobre CloudFront HTTPS/redirect, `/health`, CORS somente da origem publicada, os três cenários nos dois modos, auditoria S3 e ausência de payload em CloudWatch. No pitch de até cinco minutos:

1. problema e limites (recomendação ≠ Simulação ≠ Proposta Qualificada Simulada; sem Aprovação/Contratação, taxa ou limite);
2. Bank Marketing como proxy, dados sintéticos, offline e não causal;
3. baseline versus adaptativa, Guardrails e métricas;
4. três cenas: veículo digital, imóvel com Humano no Loop, caso adversarial `no_offer_now`;
5. fechamento com AWS live somente quando houver URL publicada; LocalStack como integração local; contingência estática explicitamente confirmada.

O deck não deve conter e-mail, credencial ou segredo. Speaker notes estão em `presentation/src/index.html` e o roteiro completo em `roteiro-pitch-5-minutos.md`.

## 6. Exportação, teardown e residue check

Antes de remover uma demo futura, exporte apenas a projeção minimizada e hash-verifique:

```bash
export AWS_PROFILE=coding-agent
EVIDENCE_DIR="$(pwd)/artifacts/teardown-evidence-$(date -u +%Y%m%dT%H%M%SZ)" \
  scripts/export-demo-evidence.sh
```

Depois de uma apresentação, o caminho manual exige `DESTROY_APPROVED=DESTROY_DEMO scripts/teardown-demo-aws.sh --confirm-destroy`; no GitHub Actions, informe exatamente `DESTROY_DEMO` no workflow. O agendamento `--expired-only` é apenas failsafe. Nunca execute Terraform no diretório bootstrap.

```bash
scripts/verify-demo-destroyed.sh
```

A verificação deve encontrar zero recursos temporários e confirmar bootstrap, OIDC/roles/boundary e Budget. O workflow de teardown publica artifact por sete dias **somente quando for enviado e executado**; a execução local retém bundle fora do Git.

## 7. Estado e evidência desta execução

Para a consolidação atual, não rode AWS mutável. Consulte [`acceptance-final.md`](acceptance-final.md), que registra #25 smoke real e URLs históricas offline/destroyed, #27 teardown, #23 LocalStack, Golden Set, testes, hashes oficiais, quota baixa, advisories npm, self-review do GitHub environment e ausência de artifact GitHub do teardown.
