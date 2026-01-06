from sqlalchemy import String, Integer, DateTime, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from app.db.base import Base

class User(Base):
    __tablename__ = "user"

    user_id: Mapped[int] = mapped_column(primary_key=True)

    username: Mapped[str] = mapped_column(String, unique=True, index=True)
    email: Mapped[str | None] = mapped_column(String, unique=True, index=True)


    password_hash: Mapped[str | None] = mapped_column(String)  
    google_id: Mapped[str | None] = mapped_column(
        String, unique=True, index=True
    )

    cf_handle: Mapped[str | None] = mapped_column(
        String, unique=True, index=True
    )
    cf_rating: Mapped[int | None] = mapped_column(Integer)

    platform_rating: Mapped[int] = mapped_column(Integer, default=1200)
    profile_completed: Mapped[bool] = mapped_column(Boolean, default=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )
