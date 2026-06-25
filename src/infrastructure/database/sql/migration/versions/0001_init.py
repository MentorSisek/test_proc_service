"""init payments and outbox

Revision ID: 0001
Revises:
Create Date: 2026-06-24

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = '0001'
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
	op.create_table(
		'payments',
		sa.Column('id', postgresql.UUID(as_uuid=False), nullable=False),
		sa.Column('amount', sa.Numeric(precision=18, scale=2), nullable=False),
		sa.Column(
			'currency',
			sa.Enum('RUB', 'USD', 'EUR', name='currency_enum'),
			nullable=False,
		),
		sa.Column('description', sa.String(), nullable=True),
		sa.Column('metadata', postgresql.JSONB(), nullable=False),
		sa.Column(
			'status',
			sa.Enum('pending', 'succeeded', 'failed', name='payment_status_enum'),
			nullable=False,
		),
		sa.Column('idempotency_key', sa.String(), nullable=False),
		sa.Column('webhook_url', sa.String(), nullable=True),
		sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
		sa.Column('processed_at', sa.DateTime(timezone=True), nullable=True),
		sa.PrimaryKeyConstraint('id'),
		sa.UniqueConstraint('idempotency_key'),
	)
	op.create_index('ix_payments_status', 'payments', ['status'])
	op.create_index('ix_payments_idempotency_key', 'payments', ['idempotency_key'])

	op.create_table(
		'outbox',
		sa.Column('id', postgresql.UUID(as_uuid=False), nullable=False),
		sa.Column('routing_key', sa.String(), nullable=False),
		sa.Column('payload', postgresql.JSONB(), nullable=False),
		sa.Column(
			'status',
			sa.Enum('pending', 'published', name='outbox_status_enum'),
			nullable=False,
		),
		sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
		sa.Column('published_at', sa.DateTime(timezone=True), nullable=True),
		sa.PrimaryKeyConstraint('id'),
	)
	op.create_index('ix_outbox_status', 'outbox', ['status'])


def downgrade() -> None:
	op.drop_index('ix_outbox_status', table_name='outbox')
	op.drop_table('outbox')
	op.drop_index('ix_payments_idempotency_key', table_name='payments')
	op.drop_index('ix_payments_status', table_name='payments')
	op.drop_table('payments')
	sa.Enum(name='outbox_status_enum').drop(op.get_bind())
	sa.Enum(name='payment_status_enum').drop(op.get_bind())
	sa.Enum(name='currency_enum').drop(op.get_bind())
