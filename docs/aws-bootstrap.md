# Bootstrap AWS persistente e identidades GitHub OIDC

> **Estado desta documentação:** o bootstrap foi aplicado e permanece como fundação persistente da conta usada na validação. A demo temporária foi destruída; novas aplicações exigem uma pessoa autorizada, SSO e revisão humana.

Este bootstrap é a fundação persistente da demonstração temporária descrita no ADR-0002. Ele cria somente:

- um bucket S3 de state, com versionamento, SSE-S3 (`AES256`), Bucket Owner Enforced, Block Public Access e negação de transporte sem TLS;
- a configuração de backend que usa o lockfile nativo do S3 (`use_lockfile = true`), sem tabela DynamoDB;
- o provider OIDC de GitHub Actions e duas IAM Roles: `tc4-mlops-github-plan` e `tc4-mlops-github-deploy`;
- uma permissions boundary que, por enquanto, só permite o state e lockfile do **bootstrap**.

Não cria API, Lambda, ECR, CloudFront, bucket de apresentação, bucket de auditoria ou qualquer recurso da demo. Esses recursos continuam temporários e pertencem a state e ciclo de destruição próprios.

## Separação obrigatória de state e ciclo de vida

| Item | Bootstrap persistente | Demo temporária (futura) |
| --- | --- | --- |
| State key | `bootstrap/terraform.tfstate` | `demo/terraform.tfstate` ou backend dedicado, nunca a chave de bootstrap |
| Recursos | bucket de state e identidades OIDC | apresentação, API, auditoria, ECR e observabilidade |
| Destroy normal | bloqueado por `prevent_destroy` e `force_destroy = false` | obrigatório após a apresentação |
| Role atual | lê/grava somente a chave `bootstrap` conforme necessidade | sem permissão implícita: requer política e boundary revisadas |

A variável `state_key` é intencionalmente fixa em `bootstrap/terraform.tfstate`. Assim, a configuração deste diretório não pode acidentalmente apontar para o state da demo. O ambiente LocalStack de `infrastructure/environments/localstack` mantém state local e não é alterado por este fluxo.

## Pré-requisitos humanos obrigatórios

Antes de executar Terraform na conta AWS:

1. Proteja a conta root com MFA; use root somente para tarefas que exigem root.
2. Confirme que root não possui Access Keys e não crie nenhuma. Revogue chaves root existentes antes do bootstrap.
3. Habilite IAM Identity Center e crie/receba um permission set administrativo temporário para o operador do bootstrap. A concessão deve ser aprovada pelo dono da conta; não é uma política bancária ou de produção.
4. Configure AWS CLI v2 com SSO (`aws configure sso --profile tc4-bootstrap-admin`) e autentique-se com `aws sso login --profile tc4-bootstrap-admin`.
5. Confirme a conta e a identidade esperadas com `aws sts get-caller-identity --profile tc4-bootstrap-admin`.

Terraform usa a cadeia padrão de credenciais do AWS SDK e `AWS_PROFILE`; ele não aceita, gera ou grava `access_key`/`secret_key`. Não adicione Access Keys a GitHub Secrets: GitHub Actions deve usar OIDC.

## Aplicação inicial e migração para S3

O paradoxo do backend é tratado em dois estágios: o primeiro apply usa state local transitório para criar o bucket; em seguida, o próprio state é migrado ao S3 seguro. Execute a partir da raiz do repositório:

```bash
export AWS_PROFILE=tc4-bootstrap-admin
aws sso login --profile "$AWS_PROFILE"
aws sts get-caller-identity --profile "$AWS_PROFILE"

account_id="$(aws sts get-caller-identity --query Account --output text --profile "$AWS_PROFILE")"
# Escolha um sufixo não secreto e único; nomes de bucket são globais.
bucket="tc4-mlops-tfstate-${account_id}-bootstrap01"

terraform fmt -check -recursive
terraform -chdir=infrastructure/environments/bootstrap init -backend=false
terraform -chdir=infrastructure/environments/bootstrap validate
terraform -chdir=infrastructure/environments/bootstrap test
terraform -chdir=infrastructure/environments/bootstrap apply \
  -var="state_bucket_name=${bucket}"

# backend.hcl contém configuração, não credenciais, e é ignorado pelo Git.
terraform -chdir=infrastructure/environments/bootstrap output -raw backend_config \
  > infrastructure/environments/bootstrap/backend.hcl
terraform -chdir=infrastructure/environments/bootstrap init -migrate-state \
  -backend-config=backend.hcl
terraform -chdir=infrastructure/environments/bootstrap state pull >/dev/null
terraform -chdir=infrastructure/environments/bootstrap output github_actions_role_arns
```

Não remova o `terraform.tfstate` local manualmente antes de `init -migrate-state` concluir e `state pull` funcionar. Depois da verificação, ele deixa de ser a fonte de verdade. Não faça `apply` com `-backend=false` novamente depois da migração.

O arquivo gerado habilita explicitamente `encrypt = true` e `use_lockfile = true`. Versionamento do bucket preserva versões anteriores do state; o lockfile S3 impede operações Terraform concorrentes.

## Configuração GitHub Actions

Use os ARNs produzidos no output somente em workflows deste repositório. A trust policy valida `aud = sts.amazonaws.com` e os subjects exatos:

- plan: `repo:hgribeiro/tc4-mlops:pull_request` ou `repo:hgribeiro/tc4-mlops:ref:refs/heads/main`;
- deploy: `repo:hgribeiro/tc4-mlops:environment:demo`.

Não há wildcard em `sub`, organização, repositório, ref ou ambiente. Proteja o environment GitHub `demo` com revisores obrigatórios **e restrinja as deployment branches a `main`** antes de ligar qualquer workflow ao ARN de deploy. O subject OIDC de um job que usa environment contém o environment, não a ref; a restrição de branch é, portanto, obrigatória na configuração do environment GitHub.

As duas roles são separadas. A role de plan lê o state separado da demo e manipula somente o lockfile dela; o plan usa `-refresh=false`, portanto não recebe acesso a recursos da demo nem pode escrever o state. A role de deploy atualiza somente o state separado e os recursos temporários de nomes concretos. Ambas usam a mesma permissions boundary. Elas deliberadamente **não** recebem `AdministratorAccess`, `iam:*`, `s3:*`, nem permissão para alterar a trust policy, provider OIDC, roles de automação ou proteções do bootstrap.

O workflow [`.github/workflows/demo-quality-and-deploy.yml`](../.github/workflows/demo-quality-and-deploy.yml) executa qualidade, evidência oficial, deck, Docker e Terraform antes do plan. O plan assume somente `tc4-mlops-github-plan`; deploy só pode ser iniciado manualmente (`workflow_dispatch`) da ref `main`, assume somente `tc4-mlops-github-deploy` e declara `environment: demo`. O environment `demo` está configurado com aprovação manual do mantenedor `hgribeiro` e política de branch personalizada somente para `main`. Como este repositório tem apenas esse mantenedor configurado, a proteção permite autoaprovação (`prevent_self_review=false`); antes de uma demonstração com governança independente, adicione outro revisor e habilite `prevent_self_review`. A trust OIDC do environment não contém a ref, então ambas as proteções são necessárias. Não use `pull_request_target`, secrets de Access Key ou credenciais persistentes.

Quando os recursos temporários tiverem nomes, tags e ARNs definitivos, uma alteração posterior deve ampliar de forma revisada **a policy da role e a permissions boundary**, com testes de invariantes para cada serviço. Não contorne essa etapa anexando uma policy ampla ou removendo a boundary.

## Recuperação e operação segura

- **Lock ativo:** confirme que não há outro Terraform em execução. Só então use o ID mostrado pelo Terraform em `terraform force-unlock LOCK_ID`; nunca apague `.tflock` por suposição.
- **State corrompido ou regressão:** identifique a versão no versionamento S3, baixe-a com `aws s3api get-object --bucket "$bucket" --key bootstrap/terraform.tfstate --version-id VERSION recovered.tfstate --profile "$AWS_PROFILE"`, revise-a localmente e faça backup do state atual. Use `terraform state push recovered.tfstate` apenas após validar lineage/serial e aprovação humana.
- **Falha durante a migração:** mantenha o state local intacto, corrija a causa (permissão, nome ou região) e repita `init -migrate-state`. Não execute um segundo bootstrap apply que possa criar recursos fora do state original.
- **Destroy acidental:** o bucket, provider OIDC, roles e boundary têm `prevent_destroy`; o bucket também tem `force_destroy = false`. Uma remoção persistente exige alteração explícita, revisão humana e confirmação de que nenhuma demo usa o backend.

O bootstrap não guarda secrets em outputs. ARNs e o nome do bucket são identificadores operacionais, não credenciais. Revise regularmente as versões do state, a associação das roles, o Budget e as proteções MFA/SSO com o administrador da conta. O Budget persistente é consultivo e não é um hard stop.

## Demo AWS temporária (#25)

A demo usa o mesmo bucket persistente, porém uma chave de state **separada**:
`demo/terraform.tfstate`. Ela não altera o `prevent_destroy` do bootstrap e não
executa destroy do bootstrap. O script versionado faz o apply em dois estágios:
primeiro ECR, buckets e CloudFront; depois da imagem imutável existir, Lambda e
HTTP API. Ele injeta a URL resultante da API no build do deck, publica-o no
bucket privado, invalida CloudFront e executa os smokes públicos.

```bash
export AWS_PROFILE=coding-agent
# O SHA deve ser o commit que contém a infraestrutura; nunca use latest.
COMMIT_SHA="$(git rev-parse HEAD)" AWS_PROFILE=coding-agent \
  scripts/deploy-demo-aws.sh
```

### Exceção temporária de quota Lambda

Enquanto a conta `969212888717` permanecer com `ConcurrentExecutions = 10` e a
solicitação de aumento estiver pendente, `LOW_QUOTA_MODE=true` é o padrão
configurável tanto do script quanto do workflow. Ele **omite** a concorrência
reservada da função (preserva o hard cap da conta), mas não altera timeout de
Lambda (10 segundos), throttle da API Gateway (5 req/s), burst (10), serviços
ou capacidade. Após a aprovação da quota, informe `LOW_QUOTA_MODE=false` para
restaurar a reserva padrão de 2. A evidência operacional deve registrar a quota
e o modo usados.

O script exige a conta `969212888717`, usa `us-east-1` por padrão (configure
`AWS_REGION` para mudar), cria `backend.hcl` ignorado temporário e usa somente
a cadeia de credenciais do perfil. Ao final ele **mantém** a demo para os itens
seguintes, com `ExpiresAt` quatro horas após o deploy (ou `EXPIRES_AT` explícito
para uma execução de evidência). Isso é uma tag e um failsafe operacional; não
é destruição automática, Budget Alert nem o workflow de encerramento previsto
para a issue #27.

A role OIDC de deploy continua com os mesmos subjects exatos. Sua policy e
permissions boundary agora enumeram a chave `demo/terraform.tfstate` e os
nomes concretos `tc4-mlops-demo-969212888717-*`, sem `AdministratorAccess` ou
`iam:*`. O workflow de deploy é o da issue #26; o teardown usa a mesma role
protegida pelo environment `demo` e a mesma concorrência de ciclo de vida.

## Encerramento e custo da demo (#27)

O bootstrap também cria o AWS Budget mensal de USD 30 da demo, com alertas de
custo realizado em 80% e 100%. O alerta não interrompe gastos automaticamente:
créditos promocionais, Free Tier, impostos e a própria medição de Billing podem
variar. O endereço operacional é mantido uma única vez na variável Terraform,
e não deve ser reproduzido em logs ou artifacts. O procedimento, exportação
minimizada com hashes, retenção de artifact e failsafe agendado estão em
[Encerramento seguro da demo AWS](aws-demo-teardown.md).
