from fastapi import FastAPI

from app.routers import auth, tasks, users

app = FastAPI(
    title="Taskflow API",
    description="Backend SaaS com autenticação JWT e gerenciamento de tarefas",
    version="0.1.0",
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(tasks.router)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
