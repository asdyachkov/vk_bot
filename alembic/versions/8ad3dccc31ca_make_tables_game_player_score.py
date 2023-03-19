"""Make tables game, player, score

Revision ID: 8ad3dccc31ca
Revises: 
Create Date: 2023-03-19 16:54:17.042786

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8ad3dccc31ca'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('games',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('chat_id', sa.Integer(), nullable=False),
    sa.PrimaryKeyConstraint('id')
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
    sa.Column('score', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['game_id'], ['games.id'], ),
    sa.ForeignKeyConstraint(['score'], ['scores.points'], ),
    sa.PrimaryKeyConstraint('vk_id')
    )
    op.drop_table('answers')
    op.drop_table('questions')
    op.drop_table('themes')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('themes',
    sa.Column('id', sa.INTEGER(), server_default=sa.text("nextval('themes_id_seq'::regclass)"), autoincrement=True, nullable=False),
    sa.Column('title', sa.TEXT(), autoincrement=False, nullable=False),
    sa.PrimaryKeyConstraint('id', name='themes_pkey'),
    sa.UniqueConstraint('title', name='themes_title_key'),
    postgresql_ignore_search_path=False
    )
    op.create_table('questions',
    sa.Column('id', sa.INTEGER(), server_default=sa.text("nextval('questions_id_seq'::regclass)"), autoincrement=True, nullable=False),
    sa.Column('title', sa.TEXT(), autoincrement=False, nullable=False),
    sa.Column('theme_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['theme_id'], ['themes.id'], name='questions_theme_id_fkey', ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id', name='questions_pkey'),
    sa.UniqueConstraint('title', name='questions_title_key'),
    postgresql_ignore_search_path=False
    )
    op.create_table('answers',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('question_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('title', sa.TEXT(), autoincrement=False, nullable=False),
    sa.Column('is_correct', sa.BOOLEAN(), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['question_id'], ['questions.id'], name='answers_question_id_fkey', ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id', name='answers_pkey')
    )
    op.drop_table('players')
    op.drop_table('scores')
    op.drop_table('games')
    # ### end Alembic commands ###
