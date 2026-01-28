"""Add notes and is_archived to projects

Revision ID: a1b2c3d4e5f6
Revises: 3e139463fe23
Create Date: 2026-01-28 01:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a1b2c3d4e5f6'
down_revision = '3e139463fe23'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # SQLite batch mode for adding columns
    with op.batch_alter_table('projects', schema=None) as batch_op:
        batch_op.add_column(sa.Column('notes', sa.String(), nullable=True, server_default=''))
        batch_op.add_column(sa.Column('is_archived', sa.Boolean(), nullable=True, server_default='0'))
        batch_op.create_index('ix_projects_is_archived', ['is_archived'])


def downgrade() -> None:
    with op.batch_alter_table('projects', schema=None) as batch_op:
        batch_op.drop_index('ix_projects_is_archived')
        batch_op.drop_column('is_archived')
        batch_op.drop_column('notes')
