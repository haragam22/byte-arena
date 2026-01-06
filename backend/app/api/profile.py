from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.deps import get_current_user, get_db
from app.models.user import User
from app.services.codeforces import fetch_cf_user
from app.schemas.profile import ProfileSetupRequest

router = APIRouter(prefix="/profile", tags=["profile"])


@router.post("/setup")
async def setup_profile(
    payload: ProfileSetupRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if user.profile_completed:
        raise HTTPException(
            status_code=400,
            detail="Profile already completed",
        )

    cf_handle = payload.cf_handle

    cf_user = await fetch_cf_user(cf_handle)
    if not cf_user:
        raise HTTPException(
            status_code=400,
            detail="Invalid Codeforces handle",
        )

    existing = await db.scalar(
        select(User).where(User.cf_handle == cf_handle)
    )
    if existing:
        raise HTTPException(
            status_code=409,
            detail="Codeforces handle already in use",
        )

    user.cf_handle = cf_handle
    user.cf_rating = cf_user.get("rating")
    user.profile_completed = True

    await db.commit()

    return {
        "message": "Profile completed",
        "cf_handle": cf_handle,
        "cf_rating": user.cf_rating,
    }
