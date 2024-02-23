"""new column for feat with mail

Revision ID: 4bd65d95056d
Revises: d861b07bee68
Create Date: 2024-02-22 02:39:22.201338

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4bd65d95056d'
down_revision = 'd861b07bee68'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('sessions', schema=None) as batch_op:
        batch_op.alter_column('session_id',
               existing_type=sa.TEXT(length=255),
               type_=sa.String(length=255),
               existing_nullable=False)

    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('access', sa.Boolean(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_column('access')

    with op.batch_alter_table('sessions', schema=None) as batch_op:
        batch_op.alter_column('session_id',
               existing_type=sa.String(length=255),
               type_=sa.TEXT(length=255),
               existing_nullable=False)

    # ### end Alembic commands ###