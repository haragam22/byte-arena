from sqlalchemy import select, desc, asc, and_
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.contest_participant import ContestParticipant

async def get_qualified_users(
    db: AsyncSession, 
    contest_id: int, 
    limit: int = 32
) -> list[int]:
    """
    Returns the top 32 user_ids based on Score (Desc) and Time (Asc).
    """
    stmt = (
        select(ContestParticipant.user_id)
        .where(
            and_(
                ContestParticipant.contest_id == contest_id,
                ContestParticipant.eliminated == False
            )
        )
        .order_by(
            desc(ContestParticipant.score),            # Priority 1: High Score
            asc(ContestParticipant.last_submission_time) # Priority 2: Fast Time
        )
        .limit(limit)
    )

    result = await db.execute(stmt)
    return result.scalars().all()