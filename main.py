from fastapi import FastAPI
import os

app = FastAPI(title="Encore Agent API")

@app.get("/")
def read_root():
    return {"status": "ok", "message": "Encore Agent API is running."}

# Additional routes for pipeline and agent can be included here
