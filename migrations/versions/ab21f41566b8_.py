"""empty message

Revision ID: ab21f41566b8
Revises: b18428ad50df
Create Date: 2020-10-15 00:28:01.720835

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = 'ab21f41566b8'
down_revision = 'b18428ad50df'
branch_labels = None
depends_on = None


def upgrade():
    value_type = postgresql.ENUM('none', 'title', 'subtitle', name='fieldboardvisibility')
    value_type.create(op.get_bind())

    op.execute("ALTER TYPE fieldtype ADD VALUE 'date'")

    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('field', sa.Column('board_visibility', sa.Enum('none', 'title', 'subtitle', name='fieldboardvisibility'), server_default='none', nullable=False))
    op.drop_column('field', 'as_title')
    op.drop_column('field', 'primary')
    op.drop_column('field', 'max')
    op.drop_column('field', 'min')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('field', sa.Column('min', sa.INTEGER(), autoincrement=False, nullable=True))
    op.add_column('field', sa.Column('max', sa.INTEGER(), autoincrement=False, nullable=True))
    op.add_column('field', sa.Column('primary', sa.BOOLEAN(), autoincrement=False, nullable=False))
    op.add_column('field', sa.Column('as_title', sa.BOOLEAN(), autoincrement=False, nullable=False))
    op.drop_column('field', 'board_visibility')
    # ### end Alembic commands ###
