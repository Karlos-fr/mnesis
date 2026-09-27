"""Ajoute les détails du cycle cognitif aux traces persistantes."""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0007_cognitive_trace_details"
down_revision: str | None = "0006_constructions"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    """Ajoute interprétations, règles et construction de sortie aux traces."""
    op.add_column(
        "decision_traces",
        sa.Column("interpretations", sa.JSON(), nullable=False, server_default="[]"),
    )
    op.add_column(
        "decision_traces",
        sa.Column("triggered_rules", sa.JSON(), nullable=False, server_default="[]"),
    )
    op.add_column(
        "decision_traces",
        sa.Column("output_construction_id", sa.String(255), nullable=True),
    )


def downgrade() -> None:
    """Supprime les détails du cycle cognitif."""
    op.drop_column("decision_traces", "output_construction_id")
    op.drop_column("decision_traces", "triggered_rules")
    op.drop_column("decision_traces", "interpretations")
