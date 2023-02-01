"""empty message

Revision ID: 045421638de0
Revises: f967ebc1788f
Create Date: 2022-12-15 21:18:36.738435

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '045421638de0'
down_revision = 'f967ebc1788f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('Show', schema=None) as batch_op:
        batch_op.add_column(sa.Column('artist_id', sa.Integer(), nullable=False))
        batch_op.add_column(sa.Column('venue_id', sa.Integer(), nullable=False))
        batch_op.create_foreign_key(None, 'Venue', ['venue_id'], ['id'])
        batch_op.create_foreign_key(None, 'Artist', ['artist_id'], ['id'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('Show', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_column('venue_id')
        batch_op.drop_column('artist_id')

    # ### end Alembic commands ###
