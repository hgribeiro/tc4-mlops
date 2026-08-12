# Encerramento seguro da demo AWS

A demo AWS é efêmera: os recursos temporários recebem `ExpiresAt` com quatro horas por padrão. O bootstrap persistente fica no bucket de state, na chave `bootstrap/terraform.tfstate`, e inclui provider OIDC, roles GitHub `plan`/`deploy`, permissions boundary e AWS Budget. O encerramento nunca executa Terraform no diretório `bootstrap`.

## Evidência minimizada antes do destroy

`scripts/export-demo-evidence.sh` deriva somente o bucket canônico de auditoria da conta (`tc4-mlops-demo-<account>-audit`); não depende de outputs Terraform, que podem estar vazios após um destroy parcial. Antes de qualquer remoção, ele valida conta, região e tags de demo, projeta os objetos de auditoria para campos de decisão permitidos e produz métricas agregadas, versões e inventário de presença.

O diretório `artifacts/teardown-evidence-<UTC>` não contém state Terraform, credenciais, logs CloudWatch, objetos brutos de auditoria, `context_minimized` ou payload de cenário. `manifest.json` contém SHA-256 e tamanho de cada arquivo; o script verifica o manifesto antes de esvaziar o bucket. O bundle final também retém `manifest-before-destroy.json` e a verificação física/pós-state.

O workflow [demo-teardown.yml](../.github/workflows/demo-teardown.yml) publica o diretório como GitHub Actions Artifact por sete dias. Uma execução local não cria artifact no GitHub: ela retém somente a evidência local hash-verificada, fora do Git.

## Teardown manual e failsafe

Após a apresentação, execute o workflow manual e informe exatamente `DESTROY_DEMO`. Ele usa o mesmo environment `demo`, role OIDC de deploy e grupo de concorrência `tc4-mlops-demo-lifecycle` usados pelo deploy; operações não são canceladas, portanto deploy e destroy não disputam o state.

Para uma execução local guardada, com perfil humano autorizado:

```bash
export AWS_PROFILE=coding-agent
export DESTROY_APPROVED=DESTROY_DEMO
scripts/teardown-demo-aws.sh --confirm-destroy
```

O cron horário chama `--expired-only`. Ele só atua com `ExpiresAt` válido no bucket de auditoria canônico (comparado ao state quando o recurso ainda é rastreado); sem state nem bucket ele é no-op, e sem expiração verificável ele falha. É um failsafe de custo, não substitui o encerramento deliberado e pode atrasar por suspensão do GitHub Actions ou proteção de environment.

O script aceita state parcial somente depois de validar os endereços permitidos. Ele exporta e verifica a evidência, esvazia versões e delete markers do bucket de auditoria, executa um plano Terraform somente de deletes e confirma resíduos físicos antes de remover o ponteiro ativo `demo/terraform.tfstate`. O lock não é apagado por suposição: se permanecer após Terraform, a execução falha. O versionamento do bucket persistente conserva versões anteriores para recuperação.

A verificação final exige ausência de presentation/audit S3, ECR, Lambda, API Gateway, CloudFront/OAC, log group, dashboard, alarmes, role runtime, state e lock da demo. Ela exige que sobrevivam bucket/chave bootstrap, OIDC, roles, boundary e Budget.

## Budget mensal

O bootstrap provisiona `tc4-mlops-demo-monthly-usd30`: custo mensal de **USD 30**, com notificações de custo **ACTUAL** em 80% e 100%. O e-mail operacional é definido uma única vez na variável Terraform do bootstrap e não é emitido em logs ou bundles de teardown.

Budget Alerts são avisos, **não são um hard stop de gasto**. Créditos promocionais, Free Tier, impostos, período de faturamento e latência de medição da AWS variam; não trate esse Budget como garantia de custo máximo. Após o apply, confira budget, notificações e subscriber efetivos via AWS Budgets/console com uma identidade autorizada.
