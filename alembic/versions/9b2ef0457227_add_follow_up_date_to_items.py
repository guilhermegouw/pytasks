"""add follow up date to items

Revision ID: 9b2ef0457227
Revises: ffdc600a447b
Create Date: 2025-02-07 08:57:11.344548

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "9b2ef0457227"
down_revision: Union[str, None] = "ffdc600a447b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "items",
        sa.Column("follow_up_date", sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("items", "follow_up_date")
