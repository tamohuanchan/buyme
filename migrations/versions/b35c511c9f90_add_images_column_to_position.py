"""Add images column to position

Revision ID: b35c511c9f90
Revises: d37d3d37cbd4
Create Date: 2025-02-25 14:24:23.384589

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b35c511c9f90'
down_revision = 'd37d3d37cbd4'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('position', schema=None) as batch_op:
        batch_op.add_column(sa.Column('images', sa.String(length=500), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('position', schema=None) as batch_op:
        batch_op.drop_column('images')

    # ### end Alembic commands ###
