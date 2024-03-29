"""Update indexes

Revision ID: 8693eef67ac6
Revises: 7039aecf71a9
Create Date: 2024-02-24 12:15:32.976440

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "8693eef67ac6"
down_revision = "7039aecf71a9"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("files", schema=None) as batch_op:
        batch_op.alter_column("user_id", existing_type=sa.INTEGER(), nullable=False)
        batch_op.drop_constraint("files_slug_key", type_="unique")
        batch_op.create_index(
            batch_op.f("ix_files_file_hash"), ["file_hash"], unique=False
        )
        batch_op.create_index(batch_op.f("ix_files_name"), ["name"], unique=False)
        batch_op.create_index(batch_op.f("ix_files_slug"), ["slug"], unique=True)
        batch_op.create_index(batch_op.f("ix_files_user_id"), ["user_id"], unique=False)

    with op.batch_alter_table("users", schema=None) as batch_op:
        batch_op.alter_column("is_admin", existing_type=sa.BOOLEAN(), nullable=False)
        batch_op.drop_constraint("users_email_key", type_="unique")
        batch_op.create_index(batch_op.f("ix_users_email"), ["email"], unique=True)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("users", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_users_email"))
        batch_op.create_unique_constraint("users_email_key", ["email"])
        batch_op.alter_column("is_admin", existing_type=sa.BOOLEAN(), nullable=True)

    with op.batch_alter_table("files", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_files_user_id"))
        batch_op.drop_index(batch_op.f("ix_files_slug"))
        batch_op.drop_index(batch_op.f("ix_files_name"))
        batch_op.drop_index(batch_op.f("ix_files_file_hash"))
        batch_op.create_unique_constraint("files_slug_key", ["slug"])
        batch_op.alter_column("user_id", existing_type=sa.INTEGER(), nullable=True)

    # ### end Alembic commands ###
