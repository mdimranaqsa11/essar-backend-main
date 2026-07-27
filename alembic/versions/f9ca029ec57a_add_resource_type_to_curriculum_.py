"""add resource_type to curriculum materials

Revision ID: f9ca029ec57a
Revises: 328998642fd4
Create Date: 2026-07-25 17:16:27.952520

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f9ca029ec57a'
down_revision = '328998642fd4'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        'curriculum_materials',
        sa.Column('resource_type', sa.String(length=20), nullable=True),
    )


def downgrade() -> None:
    op.drop_column('curriculum_materials', 'resource_type')
