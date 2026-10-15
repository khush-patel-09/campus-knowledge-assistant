from fastapi import FastAPI

from backend.app.api.routes.qa import router as qa_router

app = FastAPI(
    title="Campus Knowledge Assistant",
    version="0.1.0",
)

app.include_router(qa_router)


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}