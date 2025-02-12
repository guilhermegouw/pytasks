"""create projects table

Revision ID: 1ac2532936d0
Revises: 9b2ef0457227
Create Date: 2025-02-07 09:17:53.322525

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "1ac2532936d0"
down_revision: Union[str, None] = "9b2ef0457227"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "projects",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("description", sa.String(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column("is_active", sa.Boolean(), default=True, nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    with op.batch_alter_table("items") as batch_op:
        batch_op.create_foreign_key(
            "fk_item_project",
            "projects",
            ["project_id"],
            ["id"],
        )


def downgrade() -> None:
    with op.batch_alter_table("items") as batch_op:
        batch_op.drop_constraint("fk_item_project", type_="foreignkey")

    op.drop_table("projects")
