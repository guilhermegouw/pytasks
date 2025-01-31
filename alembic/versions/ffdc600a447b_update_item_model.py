"""update_item_model
Revision ID: ffdc600a447b
Revises: daa4af3dc944
Create Date: 2025-01-27 14:23:42.703307
"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

revision: str = "ffdc600a447b"
down_revision: Union[str, None] = "daa4af3dc944"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create new table with desired schema
    op.create_table(
        "items_new",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("title", sa.String, nullable=False),
        sa.Column("description", sa.String, nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column(
            "item_type",
            sa.Enum(
                "NEXT_ACTION",
                "QUICK_TASK",
                "REFERENCE",
                "SOMEDAY",
                "TRASH",
                "UNDEFINED",
                name="itemtype",
            ),
            nullable=False,
            default="undefined",
        ),
        sa.Column("is_done", sa.Boolean, nullable=False, default=False),
        sa.Column("delegated_to", sa.String, nullable=True),
        sa.Column("due_date", sa.DateTime, nullable=True),
        sa.Column(
            "project_id", sa.Integer, sa.ForeignKey("items.id"), nullable=True
        ),
    )

    # Copy data
    op.execute(
        "INSERT INTO items_new (id, title, description, created_at, item_type, is_done, delegated_to, due_date, project_id) "
        'SELECT id, title, description, created_at, "undefined", COALESCE(is_done, false), NULL, due_date, project_id FROM items'
    )

    # Drop old table and rename new
    op.drop_table("items")
    op.rename_table("items_new", "items")


def downgrade() -> None:
    op.create_table(
        "items_old",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("title", sa.String, nullable=False),
        sa.Column("description", sa.String, nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=True),
        sa.Column("type", sa.String(11), nullable=True),
        sa.Column("status", sa.String(9), nullable=True),
        sa.Column("is_done", sa.Boolean, nullable=True),
        sa.Column("due_date", sa.DateTime, nullable=True),
        sa.Column("project_id", sa.Integer, nullable=True),
        sa.Column("energy_level", sa.Integer, nullable=True),
        sa.Column("estimated_time", sa.Integer, nullable=True),
    )

    op.execute(
        "INSERT INTO items_old SELECT id, title, description, created_at, NULL, NULL, is_done, due_date, project_id, NULL, NULL FROM items"
    )
    op.drop_table("items")
    op.rename_table("items_old", "items")
