"""Add product_description to projects

Revision ID: 002_project_product_description
Revises: 001_initial
Create Date: 2026-05-28
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "002_project_product_description"
down_revision: Union[str, None] = "001_initial"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "projects",
        sa.Column("product_description", sa.Text(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("projects", "product_description")
