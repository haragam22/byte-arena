# backend/setup_test_data.py
import os

# --- 1. SET ENV VARS (SQLite Mode) ---
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///./test.db"
os.environ["GOOGLE_CLIENT_ID"] = "dummy"
os.environ["GOOGLE_CLIENT_SECRET"] = "dummy"
os.environ["SESSION_SECRET"] = "dummy"
os.environ["JWT_SECRET_KEY"] = "dummy"
os.environ["BACKEND_BASE_URL"] = "http://localhost:8000"

import asyncio
import random
from datetime import datetime, timedelta

# IMPORT ENGINE & BASE (Required to create tables)
from app.db.session import AsyncSessionLocal, engine
from app.db.base import Base

# IMPORT ALL MODELS (So Base knows what to create)
from app.models.user import User
from app.models.contest import Contest
from app.models.contest_participant import ContestParticipant

async def create_test_scenario():
    print("🔨 Initialization: Creating tables in test.db...")
    
    # --- 2. CREATE TABLES (The Missing Step) ---
    # This instructs the DB to build the schema based on your models
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)   # Reset DB
        await conn.run_sync(Base.metadata.create_all) # Create new tables
    
    print("✅ Tables created successfully.")

    # --- 3. ADD DATA ---
    async with AsyncSessionLocal() as db:
        print("⚙️  Setting up test data...")

        contest_id = 999
        contest = Contest(
            contest_id=contest_id,
            contest_name="Test Battle Royale",
            contest_type="1v1",
            status="active",
            max_players=100,
            start_time=datetime.utcnow(),
            end_time=datetime.utcnow() + timedelta(hours=1)
        )
        db.add(contest)

        print("👤 Creating 35 participants...")
        for i in range(1, 36):
            uid = 10000 + i
            
            # Create User
            user = User(
                user_id=uid,
                username=f"tester_{uid}",
                email=f"tester_{uid}@example.com",
                platform_rating=1200
            )
            db.add(user)

            # Create Participant
            score = random.randint(0, 5) * 100
            t_submission = datetime.utcnow() - timedelta(minutes=random.randint(1, 60))

            part = ContestParticipant(
                contest_id=contest_id,
                user_id=uid,
                score=float(score),
                last_submission_time=t_submission,
                current_round=1,
                eliminated=False
            )
            db.add(part)
        
        await db.commit()
        print("✅ Test Data Ready!")
        print(f"👉 Contest ID: {contest_id}")
        return contest_id

async def test_round_1_finalization(contest_id: int):
    from app.services import scoring, matchmaking
    from app.db.session import AsyncSessionLocal
    
    print(f"\n🚀 Testing Round 1 Finalization for Contest {contest_id}...")
    
    async with AsyncSessionLocal() as db:
        qualified_ids = await scoring.get_qualified_users(db, contest_id=contest_id, limit=32)
        print(f"📊 Found {len(qualified_ids)} qualified users.")
        
        if not qualified_ids:
            print("❌ No qualified users found!")
            return

        success_count = 0
        for user_id in qualified_ids:
            added = await matchmaking.join_queue(user_id)
            if added:
                success_count += 1
        
        print(f"✅ Successfully queued {success_count} users to matchmaking.")
        
        # Verify in Redis (briefly)
        try:
            from app.db.redis import redis_client
            queue_len = await redis_client.llen("matchmaking:queue")
            print(f"🔗 Redis Queue Length: {queue_len}")
        except Exception as e:
            print(f"⚠️ Could not check Redis (is it running?): {e}")

async def main():
    contest_id = await create_test_scenario()
    await test_round_1_finalization(contest_id)

if __name__ == "__main__":
    asyncio.run(create_test_scenario())