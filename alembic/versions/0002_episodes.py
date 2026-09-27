"""Ajoute la mémoire épisodique persistante."""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0002_episodes"
down_revision: str | None = "0001_initial"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    """Crée la table des épisodes et son index d'isolation par instance."""
    op.create_table(
        "episodes",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("instance_id", sa.String(36), sa.ForeignKey("instances.id", ondelete="CASCADE"), nullable=False),
        sa.Column("occurred_at", sa.String(64), nullable=False),
        sa.Column("summary", sa.String(1000), nullable=False),
        sa.Column("importance", sa.Float(), nullable=False),
        sa.Column("affect", sa.JSON(), nullable=False),
        sa.Column("recall_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("accessibility", sa.Float(), nullable=False),
    )
    op.create_index("ix_episodes_instance_id", "episodes", ["instance_id"])


def downgrade() -> None:
    """Supprime la table des épisodes."""
    op.drop_index("ix_episodes_instance_id", table_name="episodes")
    op.drop_table("episodes")
