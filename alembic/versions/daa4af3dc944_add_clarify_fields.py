"""add_clarify_fields

Revision ID: daa4af3dc944
Revises: ce14d0ccf533
Create Date: 2025-01-23 11:24:30.165399

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'daa4af3dc944'
down_revision: Union[str, None] = 'ce14d0ccf533'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('items',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(), nullable=False),
    sa.Column('description', sa.String(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
    sa.Column('due_date', sa.DateTime(), nullable=True),
    sa.Column('status', sa.Enum('CAPTURED', 'CLARIFIED', 'DONE', 'DELEGATED', 'DEFERRED', name='itemstatus'), nullable=True),
    sa.Column('type', sa.Enum('UNDEFINED', 'TRASH', 'REFERENCE', 'SOMEDAY', 'PROJECT', 'NEXT_ACTION', 'WAITING_FOR', 'CALENDAR', name='itemtype'), nullable=True),
    sa.Column('is_done', sa.Boolean(), nullable=True),
    sa.Column('delegated_to', sa.String(), nullable=True),
    sa.Column('project_id', sa.Integer(), nullable=True),
    sa.Column('energy_level', sa.Integer(), nullable=True),
    sa.Column('estimated_time', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['project_id'], ['items.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('items')
    # ### end Alembic commands ###
