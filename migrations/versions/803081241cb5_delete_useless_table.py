"""delete useless table

Revision ID: 803081241cb5
Revises: 4c8bd87a5c6a
Create Date: 2024-02-15 04:05:14.582159

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '803081241cb5'
down_revision = '4c8bd87a5c6a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('user_session')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user_session',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('user_id', sa.INTEGER(), nullable=False),
    sa.Column('favorites_count', sa.INTEGER(), nullable=True),
    sa.Column('last_accessed', sa.DATETIME(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###
