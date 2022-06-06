"""empty message

Revision ID: ae9fc57070ae
Revises: 160772f75a45
Create Date: 2022-06-07 03:22:00.919887

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ae9fc57070ae'
down_revision = '160772f75a45'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('requested_events', sa.Column('Status', sa.Integer(), nullable=False))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('requested_events', 'Status')
    # ### end Alembic commands ###
