from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import AsyncSessionLocal # Use the session factory we fixed earlier
from app.services import scoring, matchmaking 





router = APIRouter()

# Dependency to get DB session
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

@router.post("/contest/{contest_id}/finalize-round-1")
async def finalize_round_1(
    contest_id: int, 
    db: AsyncSession = Depends(get_db)
):
    
    
    qualified_ids = await scoring.get_qualified_users(db, contest_id=contest_id, limit=32)
    
    if not qualified_ids:
        raise HTTPException(status_code=400, detail="No qualified participants found.")

    
    success_count = 0
    for user_id in qualified_ids:
        
        added = await matchmaking.join_queue(user_id) 
        if added:
            success_count += 1

    return {
        "status": "Round 1 Finalized",
        "qualified_count": len(qualified_ids),
        "queued_count": success_count,
        "participants": qualified_ids
    }