"""create  InlineQuery table

Revision ID: 90b87dab9288
Revises: 
Create Date: 2019-01-12 15:13:27.503686

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '90b87dab9288'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'InlineQuery',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('telegram_id', sa.Integer(), nullable=False),
        sa.Column('query', sa.Text),
        sa.Column('created_at', sa.DateTime())
    )


def downgrade():
    op.drop_table('InlineQuery')
