---
status: accepted
---

# AWS como arquitetura executável do MVP

Embora a direção anterior descrevesse Azure como arquitetura-alvo para Lary, o MVP foi desenvolvido localmente com LocalStack e implantado temporariamente na AWS por Terraform. A arquitetura cloud efetivamente executada e validada foi AWS: apresentação HTML estática em S3/CloudFront, API de Demonstração serverless em API Gateway/Lambda por ECR e auditoria minimizada em S3/CloudWatch. Azure permanece apenas como equivalência corporativa conceitual, sem implantação, smoke, validação ou alegação de arquitetura multicloud.

## Consequências

A documentação e a apresentação devem distinguir explicitamente a AWS validada da equivalência Azure não implantada, além da integração LocalStack e da contingência estática. O ambiente AWS `demo` foi criado sob demanda e destruído após o uso; somente o bootstrap de estado, OIDC/roles e Budget permanecem. Aprendizado online e processamento cloud de Delayed Rewards (EventBridge/SQS/worker) continuam fora do MVP executável e são evolução futura não provisionada.
