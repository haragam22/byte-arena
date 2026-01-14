from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime
from app.models.match import Match

async def get_active_match(db: AsyncSession, user_id: int):
    return await db.scalar(
        select(Match)
        .where(
            ((Match.player1_id == user_id) | (Match.player2_id == user_id)) &
            (Match.status == "active")
        )
        .order_by(Match.start_time.desc())
    )


async def finish_match(
    db: AsyncSession,
    match: Match,
    winner_id: int,
):
    match.winner_id = winner_id
    match.status = "finished"
    match.end_time = datetime.utcnow()

    await db.commit()
    await db.refresh(match)
    return match
