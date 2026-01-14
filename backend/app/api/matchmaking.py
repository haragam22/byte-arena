from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.deps import get_current_user
from app.db.session import AsyncSessionLocal
from app.db.redis import redis_client
from app.services.matchmaking import join_queue, leave_queue, try_match
from app.models.match import Match
from app.services.matchmaking import QUEUE_KEY
from sqlalchemy import select

router = APIRouter(prefix="/matchmaking", tags=["matchmaking"])


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


@router.get("/status")
async def matchmaking_status(
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Check queue
    in_queue = await redis_client.lpos(QUEUE_KEY, user.user_id)

    if in_queue is not None:
        return {"queued": True, "match_id": None}

    # Check active match
    match = await db.scalar(
        select(Match)
        .where(
            (Match.player1_id == user.user_id) |
            (Match.player2_id == user.user_id)
        )
        .where(Match.status == "active")
        .order_by(Match.start_time.desc())
    )

    if match:
        return {"queued": False, "match_id": match.match_id}

    return {"queued": False, "match_id": None}


@router.post("/join")
async def join(
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    queued = await join_queue(user.user_id)

    if not queued:
        return {"status": "already_queued"}

    match = await try_match(db)

    if match:
        return {"status": "matched", "match_id": match.match_id}

    return {"status": "queued"}



@router.post("/leave")
async def leave(user=Depends(get_current_user)):
    await leave_queue(user.user_id)
    return {"status": "left queue"}

