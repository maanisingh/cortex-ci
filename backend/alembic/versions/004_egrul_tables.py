"""Add EGRUL company registry tables

Revision ID: 004_egrul
Revises: 003_russian_compliance
Create Date: 2024-12-29

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '004_egrul'
down_revision: Union[str, None] = '003_russian_compliance'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create egrul_companies table
    op.create_table(
        'egrul_companies',
        sa.Column('inn', sa.String(12), nullable=False),
        sa.Column('ogrn', sa.String(15), nullable=True),
        sa.Column('kpp', sa.String(9), nullable=True),
        sa.Column('okpo', sa.String(14), nullable=True),
        sa.Column('full_name', sa.String(500), nullable=False),
        sa.Column('short_name', sa.String(200), nullable=True),
        sa.Column('legal_form', sa.String(100), nullable=True),
        sa.Column('legal_address', sa.String(500), nullable=True),
        sa.Column('actual_address', sa.String(500), nullable=True),
        sa.Column('region', sa.String(100), nullable=True),
        sa.Column('registration_date', sa.DateTime(), nullable=True),
        sa.Column('registration_authority', sa.String(300), nullable=True),
        sa.Column('director_name', sa.String(200), nullable=True),
        sa.Column('director_position', sa.String(100), nullable=True),
        sa.Column('director_inn', sa.String(12), nullable=True),
        sa.Column('founders', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('okved_main', sa.String(10), nullable=True),
        sa.Column('okved_main_name', sa.String(300), nullable=True),
        sa.Column('okved_additional', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('authorized_capital', sa.Integer(), nullable=True),
        sa.Column('authorized_capital_currency', sa.String(3), server_default='RUB'),
        sa.Column('employee_count', sa.String(50), nullable=True),
        sa.Column('revenue_category', sa.String(50), nullable=True),
        sa.Column('status', sa.String(50), server_default='active'),
        sa.Column('status_detail', sa.Text(), nullable=True),
        sa.Column('phone', sa.String(100), nullable=True),
        sa.Column('email', sa.String(255), nullable=True),
        sa.Column('website', sa.String(255), nullable=True),
        sa.Column('tax_regime', sa.String(50), nullable=True),
        sa.Column('raw_data', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('source', sa.String(50), server_default='rusprofile'),
        sa.Column('source_url', sa.String(500), nullable=True),
        sa.Column('last_fetched', sa.DateTime(), nullable=True),
        sa.Column('last_updated_at_source', sa.DateTime(), nullable=True),
        sa.Column('is_stale', sa.Boolean(), server_default='false'),
        sa.Column('fetch_attempts', sa.Integer(), server_default='0'),
        sa.Column('last_error', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('inn')
    )
    op.create_index('ix_egrul_companies_inn', 'egrul_companies', ['inn'])
    op.create_index('ix_egrul_companies_ogrn', 'egrul_companies', ['ogrn'])

    # Create egrul_fetch_log table
    op.create_table(
        'egrul_fetch_log',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('inn', sa.String(12), nullable=False),
        sa.Column('source', sa.String(50), nullable=False),
        sa.Column('success', sa.Boolean(), nullable=False),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('response_code', sa.Integer(), nullable=True),
        sa.Column('response_time_ms', sa.Integer(), nullable=True),
        sa.Column('company_found', sa.Boolean(), server_default='false'),
        sa.Column('company_name', sa.String(500), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_egrul_fetch_log_inn', 'egrul_fetch_log', ['inn'])


def downgrade() -> None:
    op.drop_index('ix_egrul_fetch_log_inn', table_name='egrul_fetch_log')
    op.drop_table('egrul_fetch_log')
    op.drop_index('ix_egrul_companies_ogrn', table_name='egrul_companies')
    op.drop_index('ix_egrul_companies_inn', table_name='egrul_companies')
    op.drop_table('egrul_companies')
