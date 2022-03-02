# Run dependency injections
import os
from injectable import load_injection_container
load_injection_container()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from resources.resource_ping import router_ping
from resources.resource_target import router_target

app = FastAPI()

# Setup CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(router_ping)
app.include_router(router_target)
