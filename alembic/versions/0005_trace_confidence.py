"""Ajoute le niveau de confiance explicite aux traces cognitives."""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0005_trace_confidence"
down_revision: str | None = "0004_traces"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    """Ajoute la colonne de confiance à la table des traces."""
    op.add_column(
        "decision_traces",
        sa.Column("confidence", sa.Float(), nullable=False, server_default="0.5"),
    )


def downgrade() -> None:
    """Supprime la colonne de confiance des traces."""
    op.drop_column("decision_traces", "confidence")
