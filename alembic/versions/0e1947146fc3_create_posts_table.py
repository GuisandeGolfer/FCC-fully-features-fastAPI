"""create posts table

Revision ID: 0e1947146fc3
Revises: 
Create Date: 2023-05-10 10:28:45.366931

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0e1947146fc3'
down_revision = None
branch_labels = None
depends_on = None

# The upgrade command is meant to be run whenever we make a change to our databases.
# so we have to put the logic for creating the posts table inside.
def upgrade() -> None:
    op.create_table('posts', sa.Column('id', sa.Integer(), nullable=False, primary_key=True), 
        sa.Column('title', sa.String(), nullable=False))
    pass

# put all the logic for deleting the posts table inside 'downgrade'
def downgrade() -> None:
    op.drop_table('posts')
    pass
