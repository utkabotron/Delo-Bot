"""Add cost breakdown columns to catalog

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2026-01-28 02:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b2c3d4e5f6a7'
down_revision = 'a1b2c3d4e5f6'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # SQLite batch mode for adding columns
    with op.batch_alter_table('product_catalog', schema=None) as batch_op:
        batch_op.add_column(sa.Column('cost_materials', sa.Numeric(10, 2), nullable=True, server_default='0'))
        batch_op.add_column(sa.Column('cost_metal', sa.Numeric(10, 2), nullable=True, server_default='0'))
        batch_op.add_column(sa.Column('cost_powder', sa.Numeric(10, 2), nullable=True, server_default='0'))
        batch_op.add_column(sa.Column('cost_cnc', sa.Numeric(10, 2), nullable=True, server_default='0'))
        batch_op.add_column(sa.Column('cost_carpentry', sa.Numeric(10, 2), nullable=True, server_default='0'))
        batch_op.add_column(sa.Column('cost_painting', sa.Numeric(10, 2), nullable=True, server_default='0'))
        batch_op.add_column(sa.Column('cost_upholstery', sa.Numeric(10, 2), nullable=True, server_default='0'))
        batch_op.add_column(sa.Column('cost_components', sa.Numeric(10, 2), nullable=True, server_default='0'))
        batch_op.add_column(sa.Column('cost_box', sa.Numeric(10, 2), nullable=True, server_default='0'))
        batch_op.add_column(sa.Column('cost_logistics', sa.Numeric(10, 2), nullable=True, server_default='0'))
        batch_op.add_column(sa.Column('cost_assembly', sa.Numeric(10, 2), nullable=True, server_default='0'))
        batch_op.add_column(sa.Column('cost_other', sa.Numeric(10, 2), nullable=True, server_default='0'))


def downgrade() -> None:
    with op.batch_alter_table('product_catalog', schema=None) as batch_op:
        batch_op.drop_column('cost_other')
        batch_op.drop_column('cost_assembly')
        batch_op.drop_column('cost_logistics')
        batch_op.drop_column('cost_box')
        batch_op.drop_column('cost_components')
        batch_op.drop_column('cost_upholstery')
        batch_op.drop_column('cost_painting')
        batch_op.drop_column('cost_carpentry')
        batch_op.drop_column('cost_cnc')
        batch_op.drop_column('cost_powder')
        batch_op.drop_column('cost_metal')
        batch_op.drop_column('cost_materials')
