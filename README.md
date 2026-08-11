# Ansible Lab — Automação de Infraestrutura Híbrida

Laboratório completo de automação e observabilidade, com Ansible orquestrando ambientes local (VirtualBox) e nuvem (AWS EC2), CI/CD via GitHub Actions e stack de observabilidade Prometheus + Grafana + Loki + Alertmanager.

## Stack e ferramentas

- **Automação:** Ansible (roles modulares, orquestração via `site.yml`)
- **Containers:** Docker
- **Observabilidade:**
  - Métricas — Prometheus + node_exporter
  - Logs — Loki + Promtail
  - Visualização — Grafana
  - Alertas — Alertmanager (com regras de alerta)
- **Nuvem:** AWS (EC2, VPC, IAM, Security Groups)
- **CI/CD:** GitHub Actions (validação automática a cada push)
- **Versionamento:** Git + GitHub

## Como executar

Aplicar toda a stack:
```bash
ansible-playbook site.yml
```

Aplicar só num grupo específico:
```bash
ansible-playbook site.yml --limit nodes    # só ambiente local
ansible-playbook site.yml --limit aws      # só AWS
```

Testar conectividade:
```bash
ansible all -m ping
```

## Serviços e portas

| Serviço | Porta | Função |
|---|---|---|
| Nginx | 8080 | Web server (teste inicial) |
| Prometheus | 9091 | Coleta de métricas |
| node_exporter | 9100 | Exportador de métricas do sistema |
| Grafana | 3000 | Dashboards e visualização |
| Loki | 3100 | Armazenamento de logs |
| Alertmanager | 9093 | Roteamento de alertas |

## Boas práticas aplicadas

- **Roles reutilizáveis** com variáveis em `defaults/` (dados separados da lógica)
- **Idempotência** garantida em todos os playbooks
- **SSH por chave** (sem senha) para automação
- **Security Group restrito** por IP na EC2
- **CI validando cada push** (sintaxe + ansible-lint)
- **Segredos protegidos** via `.gitignore` (chaves nunca versionadas)

## Sobre

Projeto desenvolvido como transição de carreira: 15+ anos em infraestrutura enterprise (Dell EMC, Linux, VMware) para DevOps. Foco em automação, observabilidade e infraestrutura como código.

