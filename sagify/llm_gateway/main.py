import uvicorn
from fastapi import FastAPI
import sys

import sagify.llm_gateway
from sagify.llm_gateway.api.v1.exceptions import InternalServerError, internal_server_error_handler
from sagify.llm_gateway.api.v1.routes import api_router


app = FastAPI(
    title="Sagify LLM Gateway",
    description="Gateway for Open Source LLM providers",
    version=sagify.llm_gateway.__version__
    )
app.include_router(api_router)
app.add_exception_handler(InternalServerError, internal_server_error_handler)


def start_server(port):
    uvicorn.run("sagify.llm_gateway.main:app", port=port, host="0.0.0.0")


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
    start_server(port)


if __name__ == "__main__":
    start_server()
