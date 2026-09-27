"""Migration initiale : instances et affirmations isolées."""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0001_initial"
down_revision: str | None = None
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    """Crée les tables minimales de la V1."""
    op.create_table(
        "instances",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("locale", sa.String(32), nullable=False),
        sa.Column("personality", sa.JSON(), nullable=False),
        sa.Column("affect", sa.JSON(), nullable=False),
    )
    op.create_table(
        "claims",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("instance_id", sa.String(36), sa.ForeignKey("instances.id", ondelete="CASCADE"), nullable=False),
        sa.Column("subject_id", sa.String(36), nullable=False),
        sa.Column("predicate", sa.String(255), nullable=False),
        sa.Column("object_id", sa.String(36), nullable=True),
        sa.Column("literal", sa.JSON(), nullable=True),
        sa.Column("confidence", sa.Float(), nullable=False),
        sa.Column("status", sa.String(32), nullable=False),
        sa.Column("origin", sa.String(32), nullable=False),
        sa.Column("evidence", sa.JSON(), nullable=False),
    )
    op.create_index("ix_claims_instance_id", "claims", ["instance_id"])


def downgrade() -> None:
    """Supprime les tables de la migration initiale."""
    op.drop_index("ix_claims_instance_id", table_name="claims")
    op.drop_table("claims")
    op.drop_table("instances")
