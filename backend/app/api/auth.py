from fastapi import APIRouter, Request, Depends
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.oauth import oauth
from app.core.security import create_access_token
from app.db.session import AsyncSessionLocal
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["auth"])

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


@router.get("/google/login")
async def google_login(request: Request):
    redirect_uri = request.url_for("google_callback")
    print("REDIRECT URI SENT TO GOOGLE:", redirect_uri)
    return await oauth.google.authorize_redirect(request, redirect_uri)



@router.get("/google/callback", name="google_callback")
async def google_callback(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    token = await oauth.google.authorize_access_token(request)
    user_info = token["userinfo"]

    google_id = user_info["sub"]
    email = user_info.get("email")
    name = user_info.get("name")

    user = await db.scalar(
        select(User).where(User.google_id == google_id)
    )

    if not user:
        user = User(
            google_id=google_id,
            email=email,
            username=name,
            profile_completed=False,
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)

    access_token = create_access_token(
        {"sub": str(user.user_id)}
    )

    return RedirectResponse(
        url=f"http://127.0.0.1:5173/profile/setup?token={access_token}"
    )
