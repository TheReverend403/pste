"""empty message

Revision ID: 7039aecf71a9
Revises: 2a006fa06649
Create Date: 2020-12-02 19:08:15.585230

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = '7039aecf71a9'
down_revision = '2a006fa06649'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('files', 'slug',
               existing_type=sa.VARCHAR(length=32),
               type_=sa.Text(),
               existing_nullable=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('files', 'slug',
               existing_type=sa.Text(),
               type_=sa.VARCHAR(length=32),
               existing_nullable=False)
    # ### end Alembic commands ###