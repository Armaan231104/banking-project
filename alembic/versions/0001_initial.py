"""initial

Revision ID: 0001_initial
Revises:
Create Date: 2026-04-26
"""

from alembic import op
import sqlalchemy as sa

revision = '0001_initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table('users',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('email', sa.String(255), nullable=False, unique=True),
        sa.Column('full_name', sa.String(255), nullable=False),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('role', sa.Enum('admin', 'user', name='userrole'), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False)
    )
    op.create_index('ix_users_email', 'users', ['email'])
    op.create_table('accounts',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('owner_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('account_id', sa.String(50), nullable=False, unique=True),
        sa.Column('balance', sa.Numeric(14,2), nullable=False),
        sa.Column('currency', sa.String(3), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.CheckConstraint('balance >= 0', name='ck_accounts_balance_non_negative')
    )
    op.create_index('ix_accounts_owner_id', 'accounts', ['owner_id'])
    op.create_index('ix_accounts_account_id', 'accounts', ['account_id'])
    op.create_table('transactions',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('type', sa.Enum('deposit', 'withdrawal', 'transfer', name='transactiontype'), nullable=False),
        sa.Column('source_account_id', sa.Integer(), sa.ForeignKey('accounts.id'), nullable=True),
        sa.Column('destination_account_id', sa.Integer(), sa.ForeignKey('accounts.id'), nullable=True),
        sa.Column('amount', sa.Numeric(14,2), nullable=False),
        sa.Column('currency', sa.String(3), nullable=False),
        sa.Column('idempotency_key', sa.String(64), unique=True, nullable=True),
        sa.Column('flagged_fraud', sa.Boolean(), nullable=False),
        sa.Column('description', sa.String(255), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.CheckConstraint('amount > 0', name='ck_transactions_amount_positive')
    )
    op.create_index('ix_transactions_created_at', 'transactions', ['created_at'])
    op.create_table('ledger_entries',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('transaction_id', sa.Integer(), sa.ForeignKey('transactions.id'), nullable=False),
        sa.Column('account_id', sa.Integer(), sa.ForeignKey('accounts.id'), nullable=False),
        sa.Column('entry_type', sa.Enum('debit', 'credit', name='ledgerentrytype'), nullable=False),
        sa.Column('amount', sa.Numeric(14,2), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False)
    )
    op.create_index('ix_ledger_entries_transaction_id', 'ledger_entries', ['transaction_id'])
    op.create_index('ix_ledger_entries_account_id', 'ledger_entries', ['account_id'])
    op.create_table('refresh_tokens',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('token_jti', sa.String(64), nullable=False, unique=True),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.Column('revoked', sa.Boolean(), nullable=False),
        sa.Column('replaced_by_jti', sa.String(64), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False)
    )
    op.create_index('ix_refresh_tokens_user_id', 'refresh_tokens', ['user_id'])
    op.create_index('ix_refresh_tokens_token_jti', 'refresh_tokens', ['token_jti'])
    op.create_table('audit_logs',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=True),
        sa.Column('action', sa.String(120), nullable=False),
        sa.Column('entity_type', sa.String(120), nullable=False),
        sa.Column('entity_id', sa.String(120), nullable=True),
        sa.Column('ip_address', sa.String(64), nullable=True),
        sa.Column('user_agent', sa.String(255), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False)
    )
    op.create_index('ix_audit_logs_action', 'audit_logs', ['action'])


def downgrade() -> None:
    op.drop_table('audit_logs')
    op.drop_table('refresh_tokens')
    op.drop_table('ledger_entries')
    op.drop_table('transactions')
    op.drop_table('accounts')
    op.drop_table('users')
