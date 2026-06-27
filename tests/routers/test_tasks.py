

# ---------------------------------------------------------------------------
# Fixture: usuário autenticado com token
# ---------------------------------------------------------------------------


async def _auth_token(client, email: str = "user@teste.com", password: str = "senha123") -> str:
    await client.post("/auth/register", json={"email": email, "password": password})
    response = await client.post("/auth/login", data={"username": email, "password": password})
    return response.json()["access_token"]


def _h(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


# ---------------------------------------------------------------------------
# POST /tasks
# ---------------------------------------------------------------------------


async def test_criar_task_retorna_201(client):
    # Given usuário autenticado
    token = await _auth_token(client, "criar@teste.com")
    # When POST /tasks com título válido
    response = await client.post(
        "/tasks",
        json={"title": "Estudar FastAPI"},
        headers=_h(token),
    )
    # Then retorna 201 com a task criada
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Estudar FastAPI"
    assert data["completed"] is False
    assert "id" in data


async def test_criar_task_sem_token_retorna_401(client):
    # Given nenhum token
    # When POST /tasks
    response = await client.post("/tasks", json={"title": "Sem auth"})
    # Then retorna 401
    assert response.status_code == 401


async def test_criar_task_com_descricao_opcional(client):
    # Given usuário autenticado
    token = await _auth_token(client, "descricao@teste.com")
    # When POST /tasks com title e description
    response = await client.post(
        "/tasks",
        json={"title": "Com descrição", "description": "Detalhe da tarefa"},
        headers=_h(token),
    )
    # Then description é salva
    assert response.status_code == 201
    assert response.json()["description"] == "Detalhe da tarefa"


# ---------------------------------------------------------------------------
# GET /tasks
# ---------------------------------------------------------------------------


async def test_listar_tasks_retorna_apenas_as_do_usuario(client):
    # Given dois usuários com tasks distintas
    token_a = await _auth_token(client, "listA@teste.com")
    token_b = await _auth_token(client, "listB@teste.com")
    await client.post("/tasks", json={"title": "Task do A"}, headers=_h(token_a))
    await client.post("/tasks", json={"title": "Task do B"}, headers=_h(token_b))
    # When usuário A lista suas tasks
    response = await client.get("/tasks", headers=_h(token_a))
    # Then vê apenas as suas
    assert response.status_code == 200
    titles = [t["title"] for t in response.json()]
    assert "Task do A" in titles
    assert "Task do B" not in titles


# ---------------------------------------------------------------------------
# GET /tasks/{id}
# ---------------------------------------------------------------------------


async def test_obter_task_por_id(client):
    # Given usuário com uma task criada
    token = await _auth_token(client, "getid@teste.com")
    create = await client.post("/tasks", json={"title": "Minha Task"}, headers=_h(token))
    task_id = create.json()["id"]
    # When GET /tasks/{id}
    response = await client.get(f"/tasks/{task_id}", headers=_h(token))
    # Then retorna a task
    assert response.status_code == 200
    assert response.json()["id"] == task_id


async def test_nao_pode_ver_task_de_outro_usuario(client):
    # Given dois usuários com tasks distintas
    token_a = await _auth_token(client, "dono@teste.com")
    token_b = await _auth_token(client, "invasor@teste.com")
    create = await client.post("/tasks", json={"title": "Privada"}, headers=_h(token_a))
    task_id = create.json()["id"]
    # When usuário B tenta acessar a task do A
    response = await client.get(f"/tasks/{task_id}", headers=_h(token_b))
    # Then retorna 404 (não expõe que existe)
    assert response.status_code == 404


# ---------------------------------------------------------------------------
# PATCH /tasks/{id}
# ---------------------------------------------------------------------------


async def test_atualizar_task_marca_como_concluida(client):
    # Given uma task pendente
    token = await _auth_token(client, "patch@teste.com")
    create = await client.post("/tasks", json={"title": "Pendente"}, headers=_h(token))
    task_id = create.json()["id"]
    # When PATCH com completed=true
    response = await client.patch(
        f"/tasks/{task_id}",
        json={"completed": True},
        headers=_h(token),
    )
    # Then task está concluída
    assert response.status_code == 200
    assert response.json()["completed"] is True


async def test_atualizar_task_parcialmente(client):
    # Given uma task com título e sem descrição
    token = await _auth_token(client, "parcial@teste.com")
    create = await client.post("/tasks", json={"title": "Original"}, headers=_h(token))
    task_id = create.json()["id"]
    # When PATCH apenas o título
    response = await client.patch(
        f"/tasks/{task_id}",
        json={"title": "Atualizado"},
        headers=_h(token),
    )
    # Then só o título mudou
    assert response.status_code == 200
    assert response.json()["title"] == "Atualizado"
    assert response.json()["completed"] is False


# ---------------------------------------------------------------------------
# DELETE /tasks/{id}
# ---------------------------------------------------------------------------


async def test_deletar_task_retorna_204(client):
    # Given uma task existente
    token = await _auth_token(client, "delete@teste.com")
    create = await client.post("/tasks", json={"title": "Apagar"}, headers=_h(token))
    task_id = create.json()["id"]
    # When DELETE /tasks/{id}
    response = await client.delete(f"/tasks/{task_id}", headers=_h(token))
    # Then retorna 204
    assert response.status_code == 204


async def test_task_deletada_nao_existe_mais(client):
    # Given uma task deletada
    token = await _auth_token(client, "deletado@teste.com")
    create = await client.post("/tasks", json={"title": "Apagar"}, headers=_h(token))
    task_id = create.json()["id"]
    await client.delete(f"/tasks/{task_id}", headers=_h(token))
    # When tenta buscar a task deletada
    response = await client.get(f"/tasks/{task_id}", headers=_h(token))
    # Then retorna 404
    assert response.status_code == 404
