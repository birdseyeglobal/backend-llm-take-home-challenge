"""add_voice_profile_table


Revision ID: a1b2c3d4e5f6
Revises: 8d2126d21d1f
Create Date: 2026-04-04 00:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
import sqlmodel
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "a1b2c3d4e5f6"
down_revision: str | None = "8d2126d21d1f"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "voice_profile",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("brand_id", sa.Uuid(), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("warmth", sa.Float(), nullable=False),
        sa.Column("seriousness", sa.Float(), nullable=False),
        sa.Column("technicality", sa.Float(), nullable=False),
        sa.Column("formality", sa.Float(), nullable=False),
        sa.Column("playfulness", sa.Float(), nullable=False),
        sa.Column(
            "target_demographic", sqlmodel.sql.sqltypes.AutoString(), nullable=False
        ),
        sa.Column(
            "style_guide", postgresql.JSONB(astext_type=sa.Text()), nullable=False
        ),
        sa.Column(
            "writing_example", sqlmodel.sql.sqltypes.AutoString(), nullable=False
        ),
        sa.Column("llm_model", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["brand_id"], ["brand.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("brand_id", "version"),
    )


def downgrade() -> None:
    op.drop_table("voice_profile")
