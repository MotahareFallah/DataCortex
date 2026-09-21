from fastapi import FastAPI

from app.api.routes.query import router as query_router

app = FastAPI(
    title="DataCortex",
    description="AI-Powered Data Intelligence Platform",
    version="0.1.0",
)


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "DataCortex",
    }


app.include_router(query_router)
