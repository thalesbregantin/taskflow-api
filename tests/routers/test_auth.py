

# ---------------------------------------------------------------------------
# POST /auth/register
# ---------------------------------------------------------------------------

async def test_register_retorna_201_com_dados_do_usuario(client):
    # Given um email e senha válidos
    # When POST /auth/register
    response = await client.post(
        "/auth/register",
        json={"email": "joao@teste.com", "password": "senha123"},
    )
    # Then retorna 201 com os dados do usuário (sem senha)
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "joao@teste.com"
    assert data["is_active"] is True
    assert "id" in data
    assert "created_at" in data
    assert "password" not in data
    assert "hashed_password" not in data


async def test_register_rejeita_email_duplicado(client):
    # Given um usuário já cadastrado
    await client.post(
        "/auth/register",
        json={"email": "duplicado@teste.com", "password": "senha123"},
    )
    # When tenta registrar com o mesmo email
    response = await client.post(
        "/auth/register",
        json={"email": "duplicado@teste.com", "password": "outrasenha"},
    )
    # Then retorna 400
    assert response.status_code == 400
    assert "Email já cadastrado" in response.json()["detail"]


async def test_register_rejeita_email_invalido(client):
    # Given um email malformado
    # When POST /auth/register
    response = await client.post(
        "/auth/register",
        json={"email": "nao-e-um-email", "password": "senha123"},
    )
    # Then retorna 422 (validação do Pydantic)
    assert response.status_code == 422


# ---------------------------------------------------------------------------
# POST /auth/login
# ---------------------------------------------------------------------------

async def test_login_retorna_token_jwt(client):
    # Given um usuário cadastrado
    await client.post(
        "/auth/register",
        json={"email": "maria@teste.com", "password": "senha123"},
    )
    # When POST /auth/login com credenciais corretas
    response = await client.post(
        "/auth/login",
        data={"username": "maria@teste.com", "password": "senha123"},
    )
    # Then retorna 200 com o token JWT
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


async def test_login_rejeita_senha_errada(client):
    # Given um usuário cadastrado
    await client.post(
        "/auth/register",
        json={"email": "carlos@teste.com", "password": "senha123"},
    )
    # When POST /auth/login com senha incorreta
    response = await client.post(
        "/auth/login",
        data={"username": "carlos@teste.com", "password": "senhaerrada"},
    )
    # Then retorna 401
    assert response.status_code == 401


async def test_login_rejeita_usuario_inexistente(client):
    # Given um email que não existe
    # When POST /auth/login
    response = await client.post(
        "/auth/login",
        data={"username": "fantasma@teste.com", "password": "senha123"},
    )
    # Then retorna 401
    assert response.status_code == 401


# ---------------------------------------------------------------------------
# GET /users/me
# ---------------------------------------------------------------------------

async def test_me_retorna_perfil_do_usuario_logado(client):
    # Given um usuário logado com token válido
    await client.post(
        "/auth/register",
        json={"email": "ana@teste.com", "password": "senha123"},
    )
    login = await client.post(
        "/auth/login",
        data={"username": "ana@teste.com", "password": "senha123"},
    )
    token = login.json()["access_token"]
    # When GET /users/me com o token no header
    response = await client.get(
        "/users/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    # Then retorna o perfil (sem senha)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "ana@teste.com"
    assert "hashed_password" not in data


async def test_me_rejeita_requisicao_sem_token(client):
    # Given nenhum token no header
    # When GET /users/me
    response = await client.get("/users/me")
    # Then retorna 401
    assert response.status_code == 401


async def test_me_rejeita_token_invalido(client):
    # Given um token inválido
    # When GET /users/me com token falso
    response = await client.get(
        "/users/me",
        headers={"Authorization": "Bearer token.invalido.aqui"},
    )
    # Then retorna 401
    assert response.status_code == 401
