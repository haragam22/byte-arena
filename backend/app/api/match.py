from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import AsyncSessionLocal
from app.core.security import get_current_user
from app.models.match import Match
from app.services.match import get_active_match, finish_match

router = APIRouter(prefix="/match", tags=["match"])


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


@router.get("/current")
async def current_match(
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    match = await get_active_match(db, user.user_id)

    if not match:
        return {"active": False}

    return {
        "active": True,
        "match_id": match.match_id,
        "player1_id": match.player1_id,
        "player2_id": match.player2_id,
        "problem_id": match.problem_id,
        "status": match.status,
    }


@router.post("/{match_id}/finish")
async def end_match(
    match_id: int,
    winner_id: int,
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    match = await db.get(Match, match_id)

    if not match:
        raise HTTPException(status_code=404, detail="Match not found")

    if match.status != "active":
        raise HTTPException(status_code=400, detail="Match already finished")

    if user.user_id not in (match.player1_id, match.player2_id):
        raise HTTPException(status_code=403, detail="Not your match")

    await finish_match(db, match, winner_id)
    return {"status": "finished", "match_id": match_id}
