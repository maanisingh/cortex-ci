"""Initial CORTEX-CI schema

Revision ID: 001_initial
Revises:
Create Date: 2024-01-15

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001_initial'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create enum types
    op.execute("CREATE TYPE userrole AS ENUM ('admin', 'analyst', 'approver', 'viewer')")
    op.execute("CREATE TYPE entitytype AS ENUM ('organization', 'individual', 'location', 'asset', 'system')")
    op.execute("CREATE TYPE constrainttype AS ENUM ('policy', 'regulation', 'compliance', 'contractual', 'operational', 'financial', 'security', 'custom')")
    op.execute("CREATE TYPE constraintseverity AS ENUM ('low', 'medium', 'high', 'critical')")
    op.execute("CREATE TYPE dependencylayer AS ENUM ('legal', 'financial', 'operational', 'academic', 'human', 'technical')")
    op.execute("CREATE TYPE risklevel AS ENUM ('low', 'medium', 'high', 'critical')")
    op.execute("CREATE TYPE scenariostatus AS ENUM ('draft', 'running', 'completed', 'archived')")
    op.execute("CREATE TYPE scenariotype AS ENUM ('entity_restriction', 'country_embargo', 'supplier_loss', 'dependency_failure', 'custom')")
    op.execute("CREATE TYPE auditaction AS ENUM ('create', 'read', 'update', 'delete', 'login', 'logout', 'export', 'calculate')")

    # Tenants table
    op.create_table(
        'tenants',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('slug', sa.String(100), unique=True, nullable=False),
        sa.Column('settings', postgresql.JSONB, server_default='{}'),
        sa.Column('is_active', sa.Boolean, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
    )
    op.create_index('ix_tenants_slug', 'tenants', ['slug'])

    # Users table
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('hashed_password', sa.String(255), nullable=False),
        sa.Column('full_name', sa.String(255)),
        sa.Column('role', postgresql.ENUM('admin', 'analyst', 'approver', 'viewer', name='userrole', create_type=False), nullable=False),
        sa.Column('is_active', sa.Boolean, server_default='true'),
        sa.Column('last_login', sa.DateTime(timezone=True)),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
    )
    op.create_index('ix_users_email_tenant', 'users', ['email', 'tenant_id'], unique=True)
    op.create_index('ix_users_tenant_id', 'users', ['tenant_id'])

    # Entities table
    op.create_table(
        'entities',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False),
        sa.Column('type', postgresql.ENUM('organization', 'individual', 'location', 'asset', 'system', name='entitytype', create_type=False), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('aliases', postgresql.ARRAY(sa.Text)),
        sa.Column('description', sa.Text),
        sa.Column('country', sa.String(3)),
        sa.Column('criticality', sa.Integer, server_default='3'),
        sa.Column('custom_data', postgresql.JSONB, server_default='{}'),
        sa.Column('tags', postgresql.ARRAY(sa.String(100))),
        sa.Column('is_active', sa.Boolean, server_default='true'),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id')),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
    )
    op.create_index('ix_entities_tenant_id', 'entities', ['tenant_id'])
    op.create_index('ix_entities_type', 'entities', ['type'])
    op.create_index('ix_entities_name', 'entities', ['name'])
    op.create_index('ix_entities_country', 'entities', ['country'])

    # Constraints table
    op.create_table(
        'constraints',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text),
        sa.Column('type', postgresql.ENUM('policy', 'regulation', 'compliance', 'contractual', 'operational', 'financial', 'security', 'custom', name='constrainttype', create_type=False), nullable=False),
        sa.Column('severity', postgresql.ENUM('low', 'medium', 'high', 'critical', name='constraintseverity', create_type=False), nullable=False),
        sa.Column('reference_code', sa.String(100)),
        sa.Column('source_document', sa.Text),
        sa.Column('applies_to_entity_types', postgresql.ARRAY(sa.String(50))),
        sa.Column('applies_to_countries', postgresql.ARRAY(sa.String(3))),
        sa.Column('effective_date', sa.Date),
        sa.Column('expiry_date', sa.Date),
        sa.Column('risk_weight', sa.Numeric(3, 2), server_default='1.0'),
        sa.Column('requirements', postgresql.JSONB, server_default='{}'),
        sa.Column('is_mandatory', sa.Boolean, server_default='false'),
        sa.Column('tags', postgresql.ARRAY(sa.String(100))),
        sa.Column('custom_data', postgresql.JSONB, server_default='{}'),
        sa.Column('is_active', sa.Boolean, server_default='true'),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id')),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
    )
    op.create_index('ix_constraints_tenant_id', 'constraints', ['tenant_id'])
    op.create_index('ix_constraints_type', 'constraints', ['type'])
    op.create_index('ix_constraints_severity', 'constraints', ['severity'])

    # Entity-Constraint mappings
    op.create_table(
        'entity_constraints',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False),
        sa.Column('entity_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('entities.id', ondelete='CASCADE'), nullable=False),
        sa.Column('constraint_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('constraints.id', ondelete='CASCADE'), nullable=False),
        sa.Column('compliance_status', sa.String(50), server_default="'pending'"),
        sa.Column('notes', sa.Text),
        sa.Column('reviewed_by', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id')),
        sa.Column('reviewed_at', sa.DateTime(timezone=True)),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
    )
    op.create_index('ix_entity_constraints_entity', 'entity_constraints', ['entity_id'])
    op.create_index('ix_entity_constraints_constraint', 'entity_constraints', ['constraint_id'])

    # Dependencies table
    op.create_table(
        'dependencies',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False),
        sa.Column('source_entity_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('entities.id', ondelete='CASCADE'), nullable=False),
        sa.Column('target_entity_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('entities.id', ondelete='CASCADE'), nullable=False),
        sa.Column('layer', postgresql.ENUM('legal', 'financial', 'operational', 'academic', 'human', 'technical', name='dependencylayer', create_type=False), nullable=False),
        sa.Column('relationship_type', sa.String(100), nullable=False),
        sa.Column('criticality', sa.Integer, server_default='3'),
        sa.Column('description', sa.Text),
        sa.Column('custom_data', postgresql.JSONB, server_default='{}'),
        sa.Column('is_active', sa.Boolean, server_default='true'),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id')),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
    )
    op.create_index('ix_dependencies_tenant_id', 'dependencies', ['tenant_id'])
    op.create_index('ix_dependencies_source', 'dependencies', ['source_entity_id'])
    op.create_index('ix_dependencies_target', 'dependencies', ['target_entity_id'])
    op.create_index('ix_dependencies_layer', 'dependencies', ['layer'])

    # Risk scores table
    op.create_table(
        'risk_scores',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False),
        sa.Column('entity_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('entities.id', ondelete='CASCADE'), nullable=False),
        sa.Column('score', sa.Numeric(5, 2), nullable=False),
        sa.Column('level', postgresql.ENUM('low', 'medium', 'high', 'critical', name='risklevel', create_type=False), nullable=False),
        sa.Column('constraint_score', sa.Numeric(5, 2)),
        sa.Column('dependency_score', sa.Numeric(5, 2)),
        sa.Column('country_score', sa.Numeric(5, 2)),
        sa.Column('factors', postgresql.JSONB, server_default='{}'),
        sa.Column('justification', sa.Text),
        sa.Column('calculated_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
    )
    op.create_index('ix_risk_scores_tenant_id', 'risk_scores', ['tenant_id'])
    op.create_index('ix_risk_scores_entity', 'risk_scores', ['entity_id'])
    op.create_index('ix_risk_scores_level', 'risk_scores', ['level'])

    # Risk history table
    op.create_table(
        'risk_history',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False),
        sa.Column('entity_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('entities.id', ondelete='CASCADE'), nullable=False),
        sa.Column('score', sa.Numeric(5, 2), nullable=False),
        sa.Column('level', postgresql.ENUM('low', 'medium', 'high', 'critical', name='risklevel', create_type=False), nullable=False),
        sa.Column('factors', postgresql.JSONB, server_default='{}'),
        sa.Column('recorded_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
    )
    op.create_index('ix_risk_history_entity_date', 'risk_history', ['entity_id', 'recorded_at'])

    # Scenarios table
    op.create_table(
        'scenarios',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text),
        sa.Column('type', postgresql.ENUM('entity_restriction', 'country_embargo', 'supplier_loss', 'dependency_failure', 'custom', name='scenariotype', create_type=False), nullable=False),
        sa.Column('status', postgresql.ENUM('draft', 'running', 'completed', 'archived', name='scenariostatus', create_type=False), server_default="'draft'"),
        sa.Column('parameters', postgresql.JSONB, server_default='{}'),
        sa.Column('baseline_snapshot', postgresql.JSONB),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id')),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('executed_at', sa.DateTime(timezone=True)),
    )
    op.create_index('ix_scenarios_tenant_id', 'scenarios', ['tenant_id'])
    op.create_index('ix_scenarios_status', 'scenarios', ['status'])

    # Scenario results table
    op.create_table(
        'scenario_results',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('scenario_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('scenarios.id', ondelete='CASCADE'), nullable=False),
        sa.Column('entity_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('entities.id', ondelete='CASCADE'), nullable=False),
        sa.Column('impact_type', sa.String(50), nullable=False),
        sa.Column('baseline_score', sa.Numeric(5, 2)),
        sa.Column('projected_score', sa.Numeric(5, 2)),
        sa.Column('score_delta', sa.Numeric(5, 2)),
        sa.Column('cascade_depth', sa.Integer, server_default='0'),
        sa.Column('impact_path', postgresql.JSONB),
        sa.Column('details', postgresql.JSONB, server_default='{}'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
    )
    op.create_index('ix_scenario_results_scenario', 'scenario_results', ['scenario_id'])

    # Audit log table
    op.create_table(
        'audit_log',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='SET NULL')),
        sa.Column('user_email', sa.String(255)),
        sa.Column('user_role', sa.String(50)),
        sa.Column('action', postgresql.ENUM('create', 'read', 'update', 'delete', 'login', 'logout', 'export', 'calculate', name='auditaction', create_type=False), nullable=False),
        sa.Column('resource_type', sa.String(100)),
        sa.Column('resource_id', postgresql.UUID(as_uuid=True)),
        sa.Column('resource_name', sa.String(255)),
        sa.Column('before_state', postgresql.JSONB),
        sa.Column('after_state', postgresql.JSONB),
        sa.Column('ip_address', postgresql.INET),
        sa.Column('user_agent', sa.Text),
        sa.Column('success', sa.Boolean, server_default='true'),
        sa.Column('error_message', sa.Text),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
    )
    op.create_index('ix_audit_log_tenant_id', 'audit_log', ['tenant_id'])
    op.create_index('ix_audit_log_user_id', 'audit_log', ['user_id'])
    op.create_index('ix_audit_log_action', 'audit_log', ['action'])
    op.create_index('ix_audit_log_created_at', 'audit_log', ['created_at'])
    op.create_index('ix_audit_log_resource', 'audit_log', ['resource_type', 'resource_id'])

    # Insert default tenant
    op.execute("""
        INSERT INTO tenants (id, name, slug, settings)
        VALUES (
            'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11',
            'Default Organization',
            'default',
            '{"risk_thresholds": {"low": 40, "medium": 60, "high": 80}}'
        )
    """)


def downgrade() -> None:
    op.drop_table('audit_log')
    op.drop_table('scenario_results')
    op.drop_table('scenarios')
    op.drop_table('risk_history')
    op.drop_table('risk_scores')
    op.drop_table('dependencies')
    op.drop_table('entity_constraints')
    op.drop_table('constraints')
    op.drop_table('entities')
    op.drop_table('users')
    op.drop_table('tenants')

    op.execute("DROP TYPE auditaction")
    op.execute("DROP TYPE scenariotype")
    op.execute("DROP TYPE scenariostatus")
    op.execute("DROP TYPE risklevel")
    op.execute("DROP TYPE dependencylayer")
    op.execute("DROP TYPE constraintseverity")
    op.execute("DROP TYPE constrainttype")
    op.execute("DROP TYPE entitytype")
    op.execute("DROP TYPE userrole")
