"""Ajoute les concepts et le lexique persistants par instance."""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0003_lexicon"
down_revision: str | None = "0002_episodes"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    """Crée les tables concepts et lexèmes avec isolation par instance."""
    op.create_table("concepts", sa.Column("id", sa.String(36), primary_key=True), sa.Column("instance_id", sa.String(36), sa.ForeignKey("instances.id", ondelete="CASCADE"), nullable=False), sa.Column("kind", sa.String(64), nullable=False), sa.Column("label", sa.String(255), nullable=False))
    op.create_index("ix_concepts_instance_id", "concepts", ["instance_id"])
    op.create_table("lexemes", sa.Column("id", sa.String(36), primary_key=True), sa.Column("instance_id", sa.String(36), sa.ForeignKey("instances.id", ondelete="CASCADE"), nullable=False), sa.Column("surface", sa.String(255), nullable=False), sa.Column("lemma", sa.String(255), nullable=False), sa.Column("language", sa.String(16), nullable=False), sa.Column("part_of_speech", sa.String(64), nullable=False), sa.Column("senses", sa.JSON(), nullable=False), sa.Column("mastery", sa.String(32), nullable=False))
    op.create_index("ix_lexemes_instance_id", "lexemes", ["instance_id"])
    op.create_index("ix_lexemes_lemma", "lexemes", ["lemma"])


def downgrade() -> None:
    """Supprime les tables lexicales."""
    op.drop_index("ix_lexemes_lemma", table_name="lexemes")
    op.drop_index("ix_lexemes_instance_id", table_name="lexemes")
    op.drop_table("lexemes")
    op.drop_index("ix_concepts_instance_id", table_name="concepts")
    op.drop_table("concepts")
