from sqlalchemy import Float, Integer, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from app.db.base import Base

class ContestParticipant(Base):
    __tablename__ = "contest_participant"   
    participant_id: Mapped[int] = mapped_column(primary_key=True)
    contest_id: Mapped[int] = mapped_column(ForeignKey("contest.contest_id"))
    user_id: Mapped[int] = mapped_column(ForeignKey("user.user_id"))

    join_time: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    current_round: Mapped[int] = mapped_column(Integer)
    eliminated: Mapped[bool] = mapped_column(Boolean, default=False)
    
    score: Mapped[float] = mapped_column(Float, default=0.0) 
    last_submission_time: Mapped[datetime] = mapped_column(nullable=True)