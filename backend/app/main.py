from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware
from app.api import auth, profile


app = FastAPI()

app.add_middleware(
    SessionMiddleware,
    secret_key="meow",
    same_site="lax",         
    https_only=False,         
)

app.include_router(auth.router)
app.include_router(auth.router)
app.include_router(profile.router)
