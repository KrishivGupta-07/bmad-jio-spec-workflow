import enum
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class ArtifactKind(str, enum.Enum):
    prd = "prd"
    fsd = "fsd"
    architecture = "architecture"
    test_strategy = "test_strategy"
    last_run = "last_run"
    src = "src"
    tests = "tests"


class Artifact(Base):
    __tablename__ = "artifacts"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), nullable=False, index=True)
    instruction_id: Mapped[int | None] = mapped_column(
        ForeignKey("instructions.id"), nullable=True, index=True
    )
    kind: Mapped[ArtifactKind] = mapped_column(Enum(ArtifactKind), nullable=False)
    path: Mapped[str] = mapped_column(String(1024), nullable=False)
    sha256: Mapped[str] = mapped_column(String(64), nullable=False, default="")
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    project: Mapped["Project"] = relationship(back_populates="artifacts")  # noqa: F821
