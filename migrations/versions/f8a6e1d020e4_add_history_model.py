"""Add history model

Revision ID: f8a6e1d020e4
Revises: 2beb40555565
Create Date: 2021-03-15 14:27:51.960821

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f8a6e1d020e4'
down_revision = '2beb40555565'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('product_history',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('products_id', sa.Integer(), nullable=True),
    sa.Column('datetime', sa.DateTime(), nullable=True),
    sa.Column('purshase_price', sa.Float(), nullable=True),
    sa.Column('sell_price', sa.Float(), nullable=True),
    sa.Column('stock_change', sa.Float(), nullable=True),
    sa.Column('promotion_percent', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['products_id'], ['product.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('product_history')
    # ### end Alembic commands ###
