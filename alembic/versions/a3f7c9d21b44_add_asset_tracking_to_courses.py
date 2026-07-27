"""add thumbnail/brochure public_id and resource_type to courses

Revision ID: a3f7c9d21b44
Revises: f9ca029ec57a
Create Date: 2026-07-25 18:30:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a3f7c9d21b44'
down_revision = 'f9ca029ec57a'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('courses', sa.Column('thumbnail_public_id', sa.String(length=255), nullable=True))
    op.add_column('courses', sa.Column('thumbnail_resource_type', sa.String(length=20), nullable=True))
    op.add_column('courses', sa.Column('brochure_public_id', sa.String(length=255), nullable=True))
    op.add_column('courses', sa.Column('brochure_resource_type', sa.String(length=20), nullable=True))


def downgrade() -> None:
    op.drop_column('courses', 'brochure_resource_type')
    op.drop_column('courses', 'brochure_public_id')
    op.drop_column('courses', 'thumbnail_resource_type')
    op.drop_column('courses', 'thumbnail_public_id')
