from app.db.redis import redis_client
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.match import Match
from datetime import datetime
from app.models import Round
from sqlalchemy import select
from app.models.problem import Problem

QUEUE_KEY = "matchmaking:queue"

async def pick_problem(db: AsyncSession) -> int:
    problem = await db.scalar(
        select(Problem).order_by(Problem.problem_id.asc())
    )

    if not problem:
        raise RuntimeError("No problems available")

    return problem.problem_id

async def join_queue(user_id: int):
    exists = await redis_client.lpos(QUEUE_KEY, user_id)

    if exists is not None:
        return False

    await redis_client.rpush(QUEUE_KEY, user_id)
    return True


async def leave_queue(user_id: int):
    await redis_client.lrem(QUEUE_KEY, 0, user_id)

async def get_active_matchmaking_round(db: AsyncSession) -> Round:
    round_ = await db.scalar(
        select(Round)
        .where(Round.round_type == "matchmaking")
        .order_by(Round.start_time.desc())
    )

    if not round_:
        raise RuntimeError("No active matchmaking round found")

    return round_

async def try_match(db: AsyncSession):
    users = await redis_client.lrange(QUEUE_KEY, 0, 1)

    if len(users) < 2:
        return None

    user1, user2 = map(int, users)

    await redis_client.lpop(QUEUE_KEY)
    await redis_client.lpop(QUEUE_KEY)

    round = await db.scalar(
        select(Round)
        .where(Round.round_type == "matchmaking")
        .order_by(Round.start_time.desc())
    )

    if not round:
        raise RuntimeError("No active matchmaking round")

    problem_id = await pick_problem(db)  # now guaranteed to exist

    match = Match(
        round_id=round.round_id,
        player1_id=user1,
        player2_id=user2,
        problem_id=problem_id,
        status="active",
        start_time=datetime.utcnow(),
    )

    db.add(match)
    await db.commit()  

    return match
