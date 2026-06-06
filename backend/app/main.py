from fastapi import FastAPI

app = FastAPI(
    title="TeamParacetamol API",
    version="0.1.0",
)


@app.get("/")
async def root():
    return {
        "message": "Hello from FastAPI!"
    }
