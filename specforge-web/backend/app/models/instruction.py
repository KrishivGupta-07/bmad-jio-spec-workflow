import enum
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class InstructionStatus(str, enum.Enum):
    pending = "pending"
    running = "running"
    success = "success"
    failure = "failure"
    halted = "halted"


class Instruction(Base):
    """A single instruction/prompt within a project group.

    Each instruction owns its own working directory (``path``) seeded with the
    BMAD scaffolding, so its artifacts (``_bmad-output``), ``src/`` and ``tests/``
    are fully isolated from sibling instructions in the same project.
    """

    __tablename__ = "instructions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), nullable=False, index=True)
    slug: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    instruction_text: Mapped[str] = mapped_column(Text, nullable=False, default="")
    path: Mapped[str] = mapped_column(String(1024), nullable=False)
    is_default: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    status: Mapped[InstructionStatus] = mapped_column(
        Enum(InstructionStatus), default=InstructionStatus.pending, nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    project: Mapped["Project"] = relationship(back_populates="instructions")  # noqa: F821
