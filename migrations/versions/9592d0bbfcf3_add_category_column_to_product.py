"""Add category column to product

Revision ID: 9592d0bbfcf3
Revises: 72e47b187bec
Create Date: 2024-02-14 04:35:51.690498

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9592d0bbfcf3'
down_revision = '72e47b187bec'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('product', schema=None) as batch_op:
        batch_op.add_column(sa.Column('category', sa.String(length=100), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('product', schema=None) as batch_op:
        batch_op.drop_column('category')

    # ### end Alembic commands ###
