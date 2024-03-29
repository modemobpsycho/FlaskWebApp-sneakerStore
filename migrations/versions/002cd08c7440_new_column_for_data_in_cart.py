"""new column for data in cart

Revision ID: 002cd08c7440
Revises: b123be94fd47
Create Date: 2024-02-18 21:57:43.664180

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '002cd08c7440'
down_revision = 'b123be94fd47'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('order', schema=None) as batch_op:
        batch_op.add_column(sa.Column('cart_data', sa.JSON(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('order', schema=None) as batch_op:
        batch_op.drop_column('cart_data')

    # ### end Alembic commands ###
