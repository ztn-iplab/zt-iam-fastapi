import os

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from starlette.responses import JSONResponse
from starlette.types import ASGIApp, Receive, Scope, Send

from app.routers.admin import router as admin_router
from app.routers.aig import router as aig_router
from app.routers.agent import router as agent_router
from app.routers.auth import router as auth_router
from app.routers.home import router as home_router
from app.routers.iam import router as iam_router
from app.routers.roles import router as roles_router
from app.routers.settings import router as settings_router
from app.routers.transactions import router as transactions_router
from app.routers.users import router as users_router
from app.routers.wallets import router as wallets_router
from app.routers.webauthn import router as webauthn_router

class ForwardedProtoMiddleware:
    def __init__(self, app: ASGIApp):
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] in {"http", "websocket"}:
            headers = {k.decode().lower(): v.decode() for k, v in scope.get("headers", [])}
            forwarded_proto = headers.get("x-forwarded-proto")
            forwarded_host = headers.get("x-forwarded-host")

            if forwarded_proto:
                scope["scheme"] = forwarded_proto.split(",")[0].strip()

            if forwarded_host:
                host = forwarded_host.split(",")[0].strip()
                if ":" in host:
                    hostname, port_str = host.split(":", 1)
                    try:
                        port = int(port_str)
                    except ValueError:
                        port = 443 if scope.get("scheme") == "https" else 80
                else:
                    hostname = host
                    port = 443 if scope.get("scheme") == "https" else 80
                scope["server"] = (hostname, port)

        await self.app(scope, receive, send)


app = FastAPI(
    title="ZT-IAM",
    description="FastAPI entrypoint for the IAMaaS service.",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

app.add_middleware(ForwardedProtoMiddleware)
session_secret = os.getenv("FLASK_SECRET_KEY")
if not session_secret:
    raise RuntimeError("FLASK_SECRET_KEY is required")
app.add_middleware(SessionMiddleware, secret_key=session_secret)
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/health")
def health_check():
    return JSONResponse({"status": "ok"})


app.include_router(wallets_router)
app.include_router(aig_router)
app.include_router(roles_router)
app.include_router(settings_router)
app.include_router(users_router)
app.include_router(transactions_router)
app.include_router(auth_router)
app.include_router(iam_router)
app.include_router(webauthn_router)
app.include_router(admin_router)
app.include_router(agent_router)
app.include_router(home_router)
