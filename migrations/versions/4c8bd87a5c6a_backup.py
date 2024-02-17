"""backup

Revision ID: 4c8bd87a5c6a
Revises: 00d9934612a3
Create Date: 2024-02-15 03:53:14.371477

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4c8bd87a5c6a'
down_revision = '00d9934612a3'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_column('favorites_count')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('favorites_count', sa.INTEGER(), server_default=sa.text('0'), nullable=True))

    # ### end Alembic commands ###