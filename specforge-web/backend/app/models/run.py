import enum
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class RunStatus(str, enum.Enum):
    pending = "pending"
    running = "running"
    success = "success"
    failure = "failure"
    halted = "halted"


class Run(Base):
    __tablename__ = "runs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), nullable=False, index=True)
    instruction_id: Mapped[int | None] = mapped_column(
        ForeignKey("instructions.id"), nullable=True, index=True
    )
    skill_name: Mapped[str] = mapped_column(String(128), nullable=False)
    trigger_phrase: Mapped[str] = mapped_column(String(512), nullable=False)
    status: Mapped[RunStatus] = mapped_column(
        Enum(RunStatus), default=RunStatus.pending, nullable=False
    )
    started_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    ended_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    iteration: Mapped[int | None] = mapped_column(Integer, nullable=True)
    claude_session_id: Mapped[str | None] = mapped_column(String(64), nullable=True)

    project: Mapped["Project"] = relationship(back_populates="runs")  # noqa: F821
    messages: Mapped[list["Message"]] = relationship(back_populates="run")  # noqa: F821
    llm_calls: Mapped[list["LLMCall"]] = relationship(back_populates="run")  # noqa: F821
