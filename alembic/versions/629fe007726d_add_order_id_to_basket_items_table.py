"""Add order_id to basket_items table

Revision ID: 629fe007726d
Revises: b9762a6b930f
Create Date: 2024-11-10 00:36:05.244923

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '629fe007726d'
down_revision: Union[str, None] = 'b9762a6b930f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # `order_id` sütununu `basket_items` tablosuna ekleyin
    op.add_column('basket_items', sa.Column('order_id', postgresql.UUID(), sa.ForeignKey('orders.id'), nullable=True))


def downgrade() -> None:
    # `order_id` sütununu kaldırın
    op.drop_column('basket_items', 'order_id')
