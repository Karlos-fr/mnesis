"""Ajoute les traces persistantes de décision cognitive."""

from collections.abc import Sequence
import sqlalchemy as sa
from alembic import op

revision: str = "0004_traces"
down_revision: str | None = "0003_lexicon"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    """Crée la table des traces cognitives."""
    op.create_table("decision_traces", sa.Column("id", sa.String(36), primary_key=True), sa.Column("instance_id", sa.String(36), sa.ForeignKey("instances.id", ondelete="CASCADE"), nullable=False), sa.Column("action", sa.String(64), nullable=False), sa.Column("candidate_actions", sa.JSON(), nullable=False), sa.Column("consulted_concepts", sa.JSON(), nullable=False), sa.Column("consulted_claims", sa.JSON(), nullable=False), sa.Column("recalled_memories", sa.JSON(), nullable=False), sa.Column("affect_snapshot", sa.JSON(), nullable=False))
    op.create_index("ix_decision_traces_instance_id", "decision_traces", ["instance_id"])


def downgrade() -> None:
    """Supprime la table des traces cognitives."""
    op.drop_index("ix_decision_traces_instance_id", table_name="decision_traces")
    op.drop_table("decision_traces")
