# Cloud shape local: Terraform + LocalStack Community

Este fluxo implementa a integração local da **API de Demonstração**, não uma implantação bancária, AWS real ou uma alegação de paridade. Ele preserva a aplicação FastAPI/Mangum usada pela Lambda: a API aceita apenas cenários oficiais, aplica Guardrails antes da política e só retorna sucesso depois de persistir uma auditoria minimizada.

## Pré-requisitos

- Docker com Docker Compose e acesso a `/var/run/docker.sock`;
- Terraform >= 1.9;
- Python com as dependências do repositório (`python -m pip install -e '.[test]'`).

Não configure perfil, credencial, backend ou endpoint AWS global para este fluxo. O provider do ambiente local recebe credenciais `test`, state no disco e overrides explícitos para `http://localhost:4566`; o runtime Lambda aponta S3 somente para `http://localstack:4566` dentro da rede Docker.

### Compatibilidade LocalStack Community/provider

O ambiente local fixa o AWS provider em `~> 5.0` (lock atual `5.100.0`) **somente neste ambiente Terraform**. O LocalStack Community `4.13.1` responde ao `GetRestApi` sem o campo `status`; a espera introduzida pelo provider AWS `6.58.0` falha apesar de S3, IAM e Lambda funcionarem. A pinagem local evita esse waiter incompatível. Ela não altera nem define a versão de futuros módulos ou implantações AWS reais: o módulo compartilhável mantém seus contratos de S3/IAM/Lambda/API, e a compatibilidade AWS real ainda exige validação separada.

## Um comando de início e smoke

Na raiz do repositório:

```bash
python -m pip install -e '.[test]'
./scripts/local-demo.sh start
```

O comando sobe `localstack/localstack:4.13.1`, usa `python:3.12-slim` apenas para montar `.build/localstack-lambda.zip` com a aplicação, FastAPI, Mangum e as demais dependências Python 3.12, e aplica o módulo Terraform. O ambiente local fixa o provider AWS 5.x porque o provider 6.x aguarda um campo `status` que o `GetRestApi` do LocalStack Community 4.13.1 não devolve; isso é uma adaptação de compatibilidade local, não uma mudança do módulo para AWS real. O output `api_endpoint` usa a rota HTTP local do REST API (`/restapis/.../local/_user_request_`), em vez do hostname AWS sintético. Por fim, `scripts/smoke_localstack.py` chama `POST /v1/decisions` pelo API Gateway REST emulado e obtém o objeto S3 indicado por `audit_log_ref`. O smoke falha se o contrato HTTP, a limitação de não aprovação, a correspondência do `decision_id` ou a minimização do objeto não forem preservados.

Para ver os outputs sem chamar novamente a API:

```bash
terraform -chdir=infrastructure/environments/localstack output
```

Limpe sempre após a demonstração:

```bash
./scripts/local-demo.sh cleanup
```

O cleanup executa `terraform destroy` contra o state local, remove o volume LocalStack e remove `.build/`. Ele não toca em recursos AWS reais.

## Estrutura Terraform

`infrastructure/modules/demo-api` é o módulo compartilhável: bucket S3 privado com Block Public Access e SSE-S3, role Lambda limitada a `s3:PutObject` no prefixo de auditoria, Lambda ZIP e API Gateway REST. O ambiente `infrastructure/environments/localstack` só fornece backend local, credenciais descartáveis e endpoint overrides. O ZIP é um transporte local para a Lambda suportado pela edição Community, não uma segunda aplicação: contém o mesmo código FastAPI/Mangum e usa o mesmo handler `responsible_next_step.api.handler`.

Validação estática e de contrato:

```bash
terraform fmt -check -recursive
terraform -chdir=infrastructure/environments/localstack init -reconfigure
terraform -chdir=infrastructure/environments/localstack validate
terraform -chdir=infrastructure/modules/demo-api init -backend=false
terraform -chdir=infrastructure/modules/demo-api test
```

## Limites explícitos do LocalStack Community

LocalStack Community retornou `501`/licença requerida para o transporte ECR da tentativa anterior. Por isso este fluxo **não cria ECR, não publica imagem e não afirma paridade de container**. O ZIP local não é evidência de que Lambda por imagem/ECR da AWS funciona; o smoke AWS real histórico do #25 cobriu esse transporte, mas seus recursos foram destruídos no #27.

O smoke local é evidência somente para a integração efetivamente exercitada: API Gateway REST → Lambda ZIP → FastAPI/Mangum → S3. Ele não é prova de comportamento AWS.

A URL REST do LocalStack é construída pelo provider 5.x após a criação do API Gateway; a integração usa o URI Lambda no formato AWS (`arn:aws:apigateway:...:lambda:path/2015-03-31/functions/.../invocations`). O smoke exercita o mesmo contrato, mas não substitui a validação AWS da arquitetura por imagem/ECR.

As superfícies abaixo **não são emuladas como evidência neste fluxo**: CloudFront, OIDC/IAM Identity Center, IAM de conta real, ECR e Lambda por imagem, CloudWatch Logs/métricas/alarmes, throttling/concurrency da Lambda, políticas IAM efetivamente avaliadas, DNS/TLS/API Gateway e comportamento operacional/ciclo de vida. O #25 validou essas superfícies na AWS real de forma histórica; hoje seus recursos estão destruídos. Não há LocalStack pago, CloudFront, GitHub Actions ou bootstrap persistente de AWS neste escopo local.

Se Docker, LocalStack ou o runtime Lambda não estiverem disponíveis, não interprete `terraform validate` ou testes mockados como smoke. Registre o bloqueio e execute o smoke somente quando a dependência estiver funcional.
