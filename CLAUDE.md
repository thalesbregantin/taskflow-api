# Taskflow API — Guia do Agente

## Contexto do Desenvolvedor

Leia sempre o vault Obsidian antes de começar qualquer sessão:
- **Vault:** `~/Documents/AgentVault/`
- **Memória do agente:** `~/Documents/AgentVault/Agent/Memory.md`
- **Tasks ativas:** `~/Documents/AgentVault/Agent/Tasks.md`
- **Stack e padrões:** `~/Documents/AgentVault/Knowledge/fastapi-stack.md`
- **Qualidade:** `~/Documents/AgentVault/Knowledge/qualidade-de-software.md`

Este projeto é portfólio para vaga de dev Python — qualidade e apresentação importam tanto quanto funcionalidade.

---

## O que é este projeto

Backend SaaS em FastAPI com autenticação JWT. Permite que usuários se registrem, façam login e gerenciem suas tarefas pessoais (modelo `Task` a ser implementado).

**Stack:** Python 3.12 · FastAPI · SQLAlchemy async · PostgreSQL · Alembic · JWT (jose) · Docker · pytest · uv

---

## Como rodar localmente

```bash
# Pré-requisito: Docker Desktop rodando

cd ~/Projects/taskflow-api
export PATH="$HOME/.local/bin:$PATH"

# Subir banco
docker compose up -d db

# Rodar API
uv run uvicorn app.main:app --reload
```

Swagger disponível em: `http://localhost:8000/docs`

### Rodar testes

```bash
uv run pytest -v
```

### Rodar linting

```bash
uv run ruff check .
uv run mypy app/
```

---

## Estrutura do projeto

```
app/
  core/
    config.py       # Variáveis de ambiente via pydantic-settings
    database.py     # Engine async + get_db dependency
    security.py     # Hash de senha (bcrypt) + geração/decodificação de JWT
  models/           # ORM — define tabelas do banco
  schemas/          # Pydantic — valida entrada e saída dos endpoints
  routers/          # Transporte HTTP — chama serviços, devolve resposta
  dependencies.py   # get_current_user — extrai usuário logado do JWT
  main.py           # Ponto de entrada, registra routers
tests/              # Espelha estrutura de app/
```

**Regra de ouro:** lógica de negócio fica nos `models/` ou em `services/` (a criar). Routers apenas recebem, delegam e respondem.

---

## Filosofia de desenvolvimento

### 1. API-First
Antes de implementar qualquer feature nova, defina o contrato:
- Qual o endpoint? (método + path)
- O que entra? (body/params)
- O que sai? (response model + status codes)
- Quais os erros possíveis?

Só então escreva o teste, só então implemente.

### 2. TDD
Fluxo obrigatório para toda feature nova:

```
Red   → escreve o teste (falha porque não existe)
Green → implementa o mínimo para passar
Refactor → limpa sem quebrar
```

### 3. BDD nos critérios de aceite
Antes de codar, descreva o comportamento esperado em linguagem natural:

```
Given usuário autenticado com token válido
When POST /tasks com {"title": "Estudar TDD"}
Then retorna 201 com a task criada e user_id correto
```

Esse "given/when/then" vira o nome e a estrutura do teste.

---

## Regras de teste

- **Sempre use banco real** — nunca mocke o SQLAlchemy ou o banco. Temos pytest-asyncio e httpx para isso.
- **Banco de teste separado** — use `DATABASE_URL` apontando para `taskflow_test` nos testes.
- **Cada teste é independente** — setup e teardown por teste, nunca compartilhe estado.
- **Pirâmide:** prefira testes de integração (endpoint + banco) sobre unitários puros. E2E apenas para fluxos críticos.

### Estrutura de um teste de integração

```python
# tests/routers/test_auth.py
async def test_register_cria_usuario(client, db):
    # Given
    payload = {"email": "joao@teste.com", "password": "senha123"}

    # When
    response = await client.post("/auth/register", json=payload)

    # Then
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "joao@teste.com"
    assert "password" not in data
```

---

## Convenções de código

- **Async em tudo** — todos os endpoints e queries usam `async/await`
- **Type hints obrigatórios** — funções sempre tipadas, mypy não deve reclamar
- **Pydantic para I/O** — nunca retorne um model ORM direto, sempre passe por um schema
- **HTTP correto** — `201` para criação, `204` para delete sem body, `422` para validação, `401` para auth, `403` para permissão
- **Sem senha no response** — jamais inclua `hashed_password` em nenhum schema de saída
- **Sem lógica nos routers** — router chama função/serviço, não implementa regra de negócio

---

## O que ainda precisa ser feito (por ordem)

1. **Configurar Alembic** — `alembic init alembic` e criar migration da tabela `users`
2. **Criar `.env`** — copiar `.env.example` e preencher valores locais
3. **Configurar pytest** — `conftest.py` com fixtures de client e banco de teste
4. **Testes de auth** — cobrir register, login, `/users/me` e casos de erro
5. **Modelo Task** — seguir API-First → TDD → implementar
6. **Linting** — adicionar `ruff` e `mypy` ao pyproject.toml
7. **GitHub Actions CI** — rodar pytest + ruff a cada push

---

## O que não fazer

- Não mocke o banco nos testes — já queimamos a mão com isso antes
- Não coloque lógica de negócio dentro de routers
- Não commite `.env` — está no `.gitignore`, mantenha assim
- Não use `SECRET_KEY` padrão em produção — a config já avisa
- Não retorne dados do usuário sem passar pelo schema `UserResponse`
- Não crie abstrações antes de ter 3+ usos concretos (YAGNI)
