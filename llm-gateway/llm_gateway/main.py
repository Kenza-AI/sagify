import uvicorn
from fastapi import FastAPI

import llm_gateway
from llm_gateway.api.v1.routes import api_router

app = FastAPI()
app.include_router(api_router)

if __name__ == "__main__":
    uvicorn.run("llm_gateway.main:app", port=8080, host="0.0.0.0")
