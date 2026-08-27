# Ansible Infra Observability — Automação de Infraestrutura Híbrida

Laboratório completo de automação e observabilidade, com Ansible orquestrando ambientes local (VirtualBox) e nuvem (AWS EC2), CI/CD via GitHub Actions e stack de observabilidade Prometheus + Grafana + Loki + Alertmanager — incluindo alertas de infraestrutura e de aplicação.

## Arquitetura

```
LOCAL (VirtualBox)                    NUVEM (AWS EC2)
├── control                  ──SSH──> ├── node-aws
│   Ansible roda daqui                │   Amazon Linux 2023, t3.micro
└── node1                             │   Mesma stack replicada via Ansible
    AlmaLinux 9                       │   (com host.docker.internal para
                                       │    comunicação entre containers)
```

Mesma base de código (`site.yml` + roles) aplicada nos dois ambientes, com portabilidade garantida via `host.docker.internal` em vez de IPs fixos — a mesma config funciona local e na nuvem sem edição manual.

## Stack e ferramentas

- **Automação:** Ansible (roles modulares, orquestração via `site.yml`)
- **Containers:** Docker
- **Observabilidade:**
  - Métricas — Prometheus + node_exporter
  - Logs — Loki + Promtail (**com suporte a leitura do systemd journal**, via build customizado — ver seção abaixo)
  - Visualização — Grafana
  - Alertas — Alertmanager, com regras de **infraestrutura** (`NodeExporterDown`, `MemoriaAlta`) e de **aplicação** (`TaxaErroAlta`, baseada em métrica customizada da API)
- **Aplicação de exemplo:** API Flask (`app-pedidos`) instrumentada com métricas Prometheus customizadas (Counter, Histogram)
- **Nuvem:** AWS (EC2, VPC, IAM, Security Groups)
- **CI/CD:** GitHub Actions (validação automática a cada push)
- **Versionamento:** Git + GitHub

## Destaque técnico: suporte a systemd journal no Promtail

A imagem oficial `grafana/promtail` é compilada **sem** suporte a leitura do systemd journal (limitação conhecida do projeto — depende de CGO + libsystemd, removidos da imagem padrão por portabilidade). Isso é um problema real em distros modernas como o **Amazon Linux 2023**, que não gera mais os arquivos de log tradicionais (`/var/log/messages`, `secure`, etc.) por padrão.

Solução implementada: build customizado do Promtail a partir do código-fonte oficial, com `CGO_ENABLED=1` e `libsystemd-dev`, compilado **no control node** (não na instância de destino, para não sobrecarregar hosts pequenos como t3.micro) e distribuído como imagem pré-buildada via Ansible.

## Executando com tags

Todas as roles têm tags para permitir execução isolada, sem reprocessar a stack inteira:

| Tag | Cobre |
|---|---|
| `infra` | docker, firewall, swap |
| `observability` | node_exporter, prometheus, loki, promtail, grafana, alertmanager |
| `app` | app-pedidos |
| *(nome da role)* | Cada role também tem sua própria tag individual (ex: `promtail`, `prometheus`) |

```bash
# Rodar uma role isolada
ansible-playbook site.yml --limit aws --tags promtail

# Rodar um grupo inteiro
ansible-playbook site.yml --limit aws --tags observability

# Pular uma tag (ex: evitar rebuild pesado do Promtail)
ansible-playbook site.yml --limit aws --skip-tags promtail

# Listar todas as tags disponíveis
ansible-playbook site.yml --list-tags
```

## Como executar

### Pré-requisito único: buildar a imagem customizada do Promtail

O `.tar` da imagem não é versionado no Git (arquivo binário, ~90MB). Antes do primeiro deploy, gere localmente:

```bash
cd roles/promtail/files
docker build -t promtail-journal:local -f Dockerfile.promtail-journal .
docker save promtail-journal:local -o promtail-journal.tar
cd ../../..
```

### Aplicar a stack

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
| app-pedidos | 5000 | API de exemplo com métricas customizadas |

## Alertas configurados

| Alerta | Condição | Camada |
|---|---|---|
| `NodeExporterDown` | Target fora do ar por > 1min | Infraestrutura |
| `MemoriaAlta` | Uso de memória > 80% por > 2min | Infraestrutura |
| `TaxaErroAlta` | Taxa de erro da API > 10% por > 2min | Aplicação |

Ciclo completo (`Inactive → Pending → Firing → Resolved`) testado e validado em ambos os ambientes, incluindo geração de tráfego real de erro na API para disparo do alerta de aplicação.

## Boas práticas aplicadas

- **Roles reutilizáveis** com variáveis em `defaults/` (dados separados da lógica)
- **Idempotência** garantida em todos os playbooks
- **Portabilidade entre ambientes** via `host.docker.internal` (sem IPs fixos hardcoded)
- **SSH por chave** (sem senha) para automação
- **Security Group restrito** por IP na EC2
- **Swap persistente** configurado como rede de segurança em instâncias com RAM limitada
- **CI validando cada push** (sintaxe + ansible-lint)
- **Segredos protegidos** via `.gitignore` (chaves, `.tar` de imagens e notas pessoais nunca versionados)

## Sobre

Projeto desenvolvido como transição de carreira: 15+ anos em infraestrutura enterprise (Dell EMC, Linux, VMware) para DevOps. Foco em automação, observabilidade e infraestrutura como código.
