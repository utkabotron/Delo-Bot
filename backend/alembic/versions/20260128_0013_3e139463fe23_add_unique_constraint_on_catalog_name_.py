"""Add unique constraint on catalog name and type

Revision ID: 3e139463fe23
Revises: 50f3b241f370
Create Date: 2026-01-28 00:13:15.214973

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3e139463fe23'
down_revision = '50f3b241f370'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # SQLite doesn't support ALTER for constraints, use batch mode
    with op.batch_alter_table('product_catalog', schema=None) as batch_op:
        batch_op.create_unique_constraint('uix_name_type', ['name', 'product_type'])


def downgrade() -> None:
    # SQLite batch mode for dropping constraint
    with op.batch_alter_table('product_catalog', schema=None) as batch_op:
        batch_op.drop_constraint('uix_name_type', type_='unique')
