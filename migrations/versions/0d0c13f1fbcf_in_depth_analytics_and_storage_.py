"""in depth analytics and storage structure modifications

Revision ID: 0d0c13f1fbcf
Revises: e5adfdf3635c
Create Date: 2025-04-09 05:23:43.023833

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0d0c13f1fbcf'
down_revision: Union[str, None] = 'e5adfdf3635c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Convert lineitem_discount in line_items to Numeric
    op.alter_column(
        'line_items',
        'lineitem_discount',
        existing_type=sa.VARCHAR(),
        type_=sa.Numeric(precision=12, scale=2),
        postgresql_using="NULLIF(lineitem_discount, '')::numeric(12,2)",
        existing_nullable=True
    )

    # Convert subtotal in orders to Numeric
    op.alter_column(
        'orders',
        'subtotal',
        existing_type=sa.VARCHAR(),
        type_=sa.Numeric(precision=12, scale=2),
        postgresql_using="NULLIF(subtotal, '')::numeric(12,2)",
        existing_nullable=True
    )

    # Convert shipping in orders to Numeric
    op.alter_column(
        'orders',
        'shipping',
        existing_type=sa.VARCHAR(),
        type_=sa.Numeric(precision=12, scale=2),
        postgresql_using="NULLIF(shipping, '')::numeric(12,2)",
        existing_nullable=True
    )

    # Convert taxes in orders to Numeric
    op.alter_column(
        'orders',
        'taxes',
        existing_type=sa.VARCHAR(),
        type_=sa.Numeric(precision=12, scale=2),
        postgresql_using="NULLIF(taxes, '')::numeric(12,2)",
        existing_nullable=True
    )

    # Convert total in orders to Numeric
    op.alter_column(
        'orders',
        'total',
        existing_type=sa.VARCHAR(),
        type_=sa.Numeric(precision=12, scale=2),
        postgresql_using="NULLIF(total, '')::numeric(12,2)",
        existing_nullable=True
    )

    # Convert discount_amount in orders to Numeric
    op.alter_column(
        'orders',
        'discount_amount',
        existing_type=sa.VARCHAR(),
        type_=sa.Numeric(precision=12, scale=2),
        postgresql_using="NULLIF(discount_amount, '')::numeric(12,2)",
        existing_nullable=True
    )

    # Convert refunded_amount in orders to Numeric
    op.alter_column(
        'orders',
        'refunded_amount',
        existing_type=sa.VARCHAR(),
        type_=sa.Numeric(precision=12, scale=2),
        postgresql_using="NULLIF(refunded_amount, '')::numeric(12,2)",
        existing_nullable=True
    )

    # Convert outstanding_balance in orders to Numeric
    op.alter_column(
        'orders',
        'outstanding_balance',
        existing_type=sa.VARCHAR(),
        type_=sa.Numeric(precision=12, scale=2),
        postgresql_using="NULLIF(outstanding_balance, '')::numeric(12,2)",
        existing_nullable=True
    )

    # Convert duties in orders to Numeric
    op.alter_column(
        'orders',
        'duties',
        existing_type=sa.VARCHAR(),
        type_=sa.Numeric(precision=12, scale=2),
        postgresql_using="NULLIF(duties, '')::numeric(12,2)",
        existing_nullable=True
    )

    # Create the new index on orders for user_id + created_at
    op.create_index('idx_orders_user_created', 'orders', ['user_id', 'created_at'], unique=False)


def downgrade() -> None:
    # Drop the index
    op.drop_index('idx_orders_user_created', table_name='orders')

    # Revert duties
    op.alter_column(
        'orders',
        'duties',
        existing_type=sa.Numeric(precision=12, scale=2),
        type_=sa.VARCHAR(),
        existing_nullable=True
    )

    # Revert outstanding_balance
    op.alter_column(
        'orders',
        'outstanding_balance',
        existing_type=sa.Numeric(precision=12, scale=2),
        type_=sa.VARCHAR(),
        existing_nullable=True
    )

    # Revert refunded_amount
    op.alter_column(
        'orders',
        'refunded_amount',
        existing_type=sa.Numeric(precision=12, scale=2),
        type_=sa.VARCHAR(),
        existing_nullable=True
    )

    # Revert discount_amount
    op.alter_column(
        'orders',
        'discount_amount',
        existing_type=sa.Numeric(precision=12, scale=2),
        type_=sa.VARCHAR(),
        existing_nullable=True
    )

    # Revert total
    op.alter_column(
        'orders',
        'total',
        existing_type=sa.Numeric(precision=12, scale=2),
        type_=sa.VARCHAR(),
        existing_nullable=True
    )

    # Revert taxes
    op.alter_column(
        'orders',
        'taxes',
        existing_type=sa.Numeric(precision=12, scale=2),
        type_=sa.VARCHAR(),
        existing_nullable=True
    )

    # Revert shipping
    op.alter_column(
        'orders',
        'shipping',
        existing_type=sa.Numeric(precision=12, scale=2),
        type_=sa.VARCHAR(),
        existing_nullable=True
    )

    # Revert subtotal
    op.alter_column(
        'orders',
        'subtotal',
        existing_type=sa.Numeric(precision=12, scale=2),
        type_=sa.VARCHAR(),
        existing_nullable=True
    )

    # Revert lineitem_discount
    op.alter_column(
        'line_items',
        'lineitem_discount',
        existing_type=sa.Numeric(precision=12, scale=2),
        type_=sa.VARCHAR(),
        existing_nullable=True
    )
