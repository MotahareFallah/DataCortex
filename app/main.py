from fastapi import FastAPI

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
