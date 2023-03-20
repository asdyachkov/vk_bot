"""Edit game model

Revision ID: 3d5b9c4356fe
Revises: 
Create Date: 2023-03-20 04:36:16.431509

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3d5b9c4356fe'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('games',
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('chat_id', sa.Integer(), nullable=False),
    sa.PrimaryKeyConstraint('chat_id')
    )
    op.create_table('scores',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('points', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('points')
    )
    op.create_table('players',
    sa.Column('vk_id', sa.Integer(), nullable=False),
    sa.Column('name', sa.Text(), nullable=False),
    sa.Column('last_name', sa.Text(), nullable=False),
    sa.Column('game_id', sa.Integer(), nullable=True),
    sa.Column('score_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['game_id'], ['games.chat_id'], ),
    sa.ForeignKeyConstraint(['score_id'], ['scores.id'], ),
    sa.PrimaryKeyConstraint('vk_id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('players')
    op.drop_table('scores')
    op.drop_table('games')
    # ### end Alembic commands ###
