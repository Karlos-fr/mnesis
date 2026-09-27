"""Ajoute la persistance des constructions linguistiques déclaratives."""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0006_constructions"
down_revision: str | None = "0005_trace_confidence"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    """Crée la table des constructions déclaratives et ses index."""
    op.create_table(
        "constructions",
        sa.Column("id", sa.String(255), primary_key=True),
        sa.Column("instance_id", sa.String(36), sa.ForeignKey("instances.id", ondelete="CASCADE"), nullable=True),
        sa.Column("language", sa.String(16), nullable=False),
        sa.Column("pattern", sa.JSON(), nullable=False),
        sa.Column("semantics", sa.JSON(), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=False),
        sa.Column("origin", sa.String(32), nullable=False),
        sa.Column("usage_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("reinforced_at", sa.String(64), nullable=True),
    )
    op.create_index("ix_constructions_instance_id", "constructions", ["instance_id"])
    op.create_index("ix_constructions_language", "constructions", ["language"])


def downgrade() -> None:
    """Supprime la table des constructions déclaratives."""
    op.drop_index("ix_constructions_language", table_name="constructions")
    op.drop_index("ix_constructions_instance_id", table_name="constructions")
    op.drop_table("constructions")
