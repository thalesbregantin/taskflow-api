# Taskflow API

![CI](https://github.com/thalesbregantin/taskflow-api/actions/workflows/ci.yml/badge.svg)

API REST para gerenciamento de tarefas pessoais com autenticação JWT. Projeto construído para demonstrar boas práticas de desenvolvimento backend com Python moderno.

## Stack

- **Python 3.12** + **FastAPI** — framework async de alta performance
- **SQLAlchemy 2 (async)** — ORM com suporte nativo a async/await
- **PostgreSQL** — banco de dados relacional
- **Alembic** — migrations versionadas
- **JWT (python-jose)** — autenticação stateless
- **pytest + httpx** — testes de integração com banco real
- **ruff + mypy** — linting e tipagem estática
- **Docker** — ambiente reproduzível
- **uv** — gerenciador de dependências ultrarrápido

## Funcionalidades

- Registro e login de usuários com hash bcrypt
- Geração e validação de tokens JWT
- CRUD completo de tarefas (criar, listar, buscar, atualizar, deletar)
- Isolamento por usuário — cada um vê e gerencia apenas suas próprias tarefas

## Como rodar localmente

**Pré-requisitos:** Docker Desktop instalado

```bash
# 1. Clone o repositório
git clone https://github.com/thalesbregantin/taskflow-api.git
cd taskflow-api

# 2. Instale o uv (gerenciador de dependências)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 3. Instale as dependências
uv sync --all-groups

# 4. Configure as variáveis de ambiente
cp .env.example .env

# 5. Suba o banco de dados
docker compose up -d db

# 6. Execute as migrations
uv run alembic upgrade head

# 7. Inicie a API
uv run uvicorn app.main:app --reload
```

Acesse a documentação interativa em: **http://localhost:8000/docs**

## Rodando os testes

Os testes de integração rodam contra um banco PostgreSQL real (sem mocks).

```bash
# Suba o banco de teste
docker compose up -d db

# Crie o banco de teste
docker exec -it <container_id> psql -U user -c "CREATE DATABASE taskflow_test;"

# Execute os testes
uv run pytest -v
```

## Endpoints

| Método | Endpoint | Descrição | Auth |
|--------|----------|-----------|------|
| `POST` | `/auth/register` | Cria uma nova conta | — |
| `POST` | `/auth/login` | Autentica e retorna JWT | — |
| `GET` | `/users/me` | Perfil do usuário logado | ✓ |
| `POST` | `/tasks` | Cria uma nova tarefa | ✓ |
| `GET` | `/tasks` | Lista tarefas do usuário | ✓ |
| `GET` | `/tasks/{id}` | Busca tarefa por ID | ✓ |
| `PATCH` | `/tasks/{id}` | Atualiza tarefa (parcial) | ✓ |
| `DELETE` | `/tasks/{id}` | Remove uma tarefa | ✓ |

## Decisões de arquitetura

**Por que SQLAlchemy async?**
O FastAPI é construído sobre ASGI e suporta concorrência real com async/await. Usar o driver síncrono bloquearia o event loop durante queries — o driver async mantém a performance sob carga.

**Por que banco real nos testes?**
Mocks do ORM mascaram bugs de migração e comportamentos específicos do PostgreSQL (constraints, tipos, índices). Testes de integração com banco real têm maior fidelidade ao ambiente de produção.

**Por que ruff + mypy?**
Ruff é um linter/formatter extremamente rápido (substitui flake8, isort, e outros). Mypy com `strict=true` garante que o código é completamente tipado — erros de tipo são capturados antes de chegar ao runtime.

**Estrutura de pastas**

```
app/
  core/            # Infraestrutura: config, banco, segurança
  models/          # ORM: definição das tabelas
  schemas/         # Pydantic: validação de entrada/saída
  routers/         # HTTP: endpoints da API
  dependencies.py  # Injeção de dependências compartilhadas
```

A lógica de negócio é mantida separada da camada de transporte HTTP — os routers delegam, não implementam.
