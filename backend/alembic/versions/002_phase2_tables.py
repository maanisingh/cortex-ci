"""Phase 2: Advanced features tables

Revision ID: 002_phase2
Revises: 001_initial
Create Date: 2025-12-23

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '002_phase2'
down_revision: Union[str, None] = '001_initial'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create new enum types for Phase 2
    op.execute("CREATE TYPE effectseverity AS ENUM ('negligible', 'minor', 'moderate', 'significant', 'severe', 'catastrophic')")
    op.execute("CREATE TYPE aianalysistype AS ENUM ('anomaly', 'pattern', 'summary', 'scenario', 'clustering')")
    op.execute("CREATE TYPE aianalysisstatus AS ENUM ('pending', 'processing', 'completed', 'failed', 'awaiting_approval', 'approved', 'rejected')")

    # Scenario Chains table (Phase 2.2)
    op.create_table(
        'scenario_chains',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text),
        sa.Column('trigger_event', sa.Text, nullable=False),
        sa.Column('trigger_entity_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('entities.id', ondelete='SET NULL')),
        sa.Column('total_entities_affected', sa.Integer, server_default='0'),
        sa.Column('max_cascade_depth', sa.Integer, server_default='0'),
        sa.Column('estimated_timeline_days', sa.Integer, server_default='0'),
        sa.Column('overall_severity', postgresql.ENUM('negligible', 'minor', 'moderate', 'significant', 'severe', 'catastrophic', name='effectseverity', create_type=False), server_default="'moderate'"),
        sa.Column('total_risk_increase', sa.Numeric(10, 2), server_default='0'),
        sa.Column('is_active', sa.Boolean, server_default='true'),
        sa.Column('last_simulated_at', sa.DateTime(timezone=True)),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
    )
    op.create_index('ix_scenario_chains_tenant_id', 'scenario_chains', ['tenant_id'])

    # Chain Effects table
    op.create_table(
        'chain_effects',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('scenario_chain_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('scenario_chains.id', ondelete='CASCADE'), nullable=False),
        sa.Column('entity_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('entities.id', ondelete='CASCADE'), nullable=False),
        sa.Column('effect_description', sa.Text, nullable=False),
        sa.Column('severity', postgresql.ENUM('negligible', 'minor', 'moderate', 'significant', 'severe', 'catastrophic', name='effectseverity', create_type=False), nullable=False),
        sa.Column('cascade_depth', sa.Integer, server_default='1'),
        sa.Column('time_delay_days', sa.Integer, server_default='0'),
        sa.Column('risk_score_delta', sa.Numeric(10, 2), server_default='0'),
        sa.Column('probability', sa.Numeric(5, 2), server_default='1.00'),
        sa.Column('caused_by_effect_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('chain_effects.id', ondelete='SET NULL')),
        sa.Column('notes', sa.Text),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
    )
    op.create_index('ix_chain_effects_chain', 'chain_effects', ['scenario_chain_id'])

    # Risk Justifications table (Phase 2.3)
    op.create_table(
        'risk_justifications',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False),
        sa.Column('entity_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('entities.id', ondelete='CASCADE'), nullable=False),
        sa.Column('risk_score_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('risk_scores.id', ondelete='SET NULL')),
        sa.Column('risk_score', sa.Numeric(10, 2), nullable=False),
        sa.Column('risk_level', sa.String(50), nullable=False),
        sa.Column('primary_factors', postgresql.JSONB, server_default='[]'),
        sa.Column('assumptions', postgresql.JSONB, server_default='[]'),
        sa.Column('confidence', sa.Numeric(5, 2), server_default='0.85'),
        sa.Column('uncertainty_factors', postgresql.JSONB, server_default='[]'),
        sa.Column('source_citations', postgresql.JSONB, server_default='[]'),
        sa.Column('analyst_can_override', sa.Boolean, server_default='true'),
        sa.Column('overridden_by', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='SET NULL')),
        sa.Column('overridden_at', sa.DateTime(timezone=True)),
        sa.Column('override_reason', sa.Text),
        sa.Column('original_score', sa.Numeric(10, 2)),
        sa.Column('version', sa.Integer, server_default='1'),
        sa.Column('previous_version_id', postgresql.UUID(as_uuid=True)),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
    )
    op.create_index('ix_risk_justifications_entity', 'risk_justifications', ['entity_id'])
    op.create_index('ix_risk_justifications_tenant', 'risk_justifications', ['tenant_id'])

    # Historical Snapshots table (Phase 2.4)
    op.create_table(
        'historical_snapshots',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False),
        sa.Column('entity_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('entities.id', ondelete='CASCADE'), nullable=False),
        sa.Column('snapshot_date', sa.Date, nullable=False),
        sa.Column('risk_score', sa.Numeric(10, 2), nullable=False),
        sa.Column('risk_level', sa.String(50), nullable=False),
        sa.Column('constraints_applied', postgresql.JSONB, server_default='[]'),
        sa.Column('dependency_count', sa.Integer, server_default='0'),
        sa.Column('incoming_dependencies', sa.Integer, server_default='0'),
        sa.Column('outgoing_dependencies', sa.Integer, server_default='0'),
        sa.Column('entity_data', postgresql.JSONB, server_default='{}'),
        sa.Column('notes', sa.Text),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
    )
    op.create_index('ix_historical_snapshots_entity', 'historical_snapshots', ['entity_id'])
    op.create_index('ix_historical_snapshots_date', 'historical_snapshots', ['snapshot_date'])

    # Decision Outcomes table
    op.create_table(
        'decision_outcomes',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False),
        sa.Column('decision_date', sa.Date, nullable=False),
        sa.Column('decision_summary', sa.Text, nullable=False),
        sa.Column('decision_type', sa.String(100), nullable=False),
        sa.Column('decision_maker_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='SET NULL')),
        sa.Column('decision_maker_name', sa.String(255)),
        sa.Column('entities_involved', postgresql.JSONB, server_default='[]'),
        sa.Column('context_snapshot', postgresql.JSONB, server_default='{}'),
        sa.Column('risk_scores_at_decision', postgresql.JSONB, server_default='{}'),
        sa.Column('outcome_date', sa.Date),
        sa.Column('outcome_summary', sa.Text),
        sa.Column('outcome_success', sa.Boolean),
        sa.Column('lessons_learned', sa.Text),
        sa.Column('tags', postgresql.JSONB, server_default='[]'),
        sa.Column('is_resolved', sa.Boolean, server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
    )
    op.create_index('ix_decision_outcomes_tenant', 'decision_outcomes', ['tenant_id'])
    op.create_index('ix_decision_outcomes_date', 'decision_outcomes', ['decision_date'])

    # Constraint Changes table
    op.create_table(
        'constraint_changes',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False),
        sa.Column('constraint_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('constraints.id', ondelete='CASCADE'), nullable=False),
        sa.Column('change_date', sa.Date, nullable=False),
        sa.Column('change_type', sa.String(50), nullable=False),
        sa.Column('change_summary', sa.Text, nullable=False),
        sa.Column('before_state', postgresql.JSONB),
        sa.Column('after_state', postgresql.JSONB, nullable=False),
        sa.Column('changed_by_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='SET NULL')),
        sa.Column('entities_affected', sa.Integer, server_default='0'),
        sa.Column('risk_scores_affected', sa.Integer, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
    )
    op.create_index('ix_constraint_changes_constraint', 'constraint_changes', ['constraint_id'])
    op.create_index('ix_constraint_changes_date', 'constraint_changes', ['change_date'])

    # Transition Reports table
    op.create_table(
        'transition_reports',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('report_date', sa.Date, nullable=False),
        sa.Column('period_start', sa.Date, nullable=False),
        sa.Column('period_end', sa.Date, nullable=False),
        sa.Column('executive_summary', sa.Text, nullable=False),
        sa.Column('key_risks', postgresql.JSONB, server_default='[]'),
        sa.Column('critical_entities', postgresql.JSONB, server_default='[]'),
        sa.Column('pending_decisions', postgresql.JSONB, server_default='[]'),
        sa.Column('lessons_learned', postgresql.JSONB, server_default='[]'),
        sa.Column('recommendations', postgresql.JSONB, server_default='[]'),
        sa.Column('statistics', postgresql.JSONB, server_default='{}'),
        sa.Column('generated_by_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='SET NULL')),
        sa.Column('is_draft', sa.Boolean, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
    )
    op.create_index('ix_transition_reports_tenant', 'transition_reports', ['tenant_id'])

    # AI Analyses table (Phase 2.5)
    op.create_table(
        'ai_analyses',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False),
        sa.Column('analysis_type', postgresql.ENUM('anomaly', 'pattern', 'summary', 'scenario', 'clustering', name='aianalysistype', create_type=False), nullable=False),
        sa.Column('status', postgresql.ENUM('pending', 'processing', 'completed', 'failed', 'awaiting_approval', 'approved', 'rejected', name='aianalysisstatus', create_type=False), server_default="'pending'"),
        sa.Column('request_description', sa.Text, nullable=False),
        sa.Column('requested_by_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('input_data', postgresql.JSONB, server_default='{}'),
        sa.Column('input_entity_ids', postgresql.JSONB, server_default='[]'),
        sa.Column('output', postgresql.JSONB),
        sa.Column('output_summary', sa.Text),
        sa.Column('confidence', sa.Numeric(5, 2), server_default='0'),
        sa.Column('explanation', sa.Text),
        sa.Column('model_card', postgresql.JSONB, server_default='{}'),
        sa.Column('model_name', sa.String(100), server_default="'cortex-v1'"),
        sa.Column('model_version', sa.String(50), server_default="'1.0.0'"),
        sa.Column('requires_human_approval', sa.Boolean, server_default='true'),
        sa.Column('approved_by_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='SET NULL')),
        sa.Column('approved_at', sa.DateTime(timezone=True)),
        sa.Column('approval_notes', sa.Text),
        sa.Column('rejection_reason', sa.Text),
        sa.Column('processing_started_at', sa.DateTime(timezone=True)),
        sa.Column('processing_completed_at', sa.DateTime(timezone=True)),
        sa.Column('error_message', sa.Text),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
    )
    op.create_index('ix_ai_analyses_tenant', 'ai_analyses', ['tenant_id'])
    op.create_index('ix_ai_analyses_status', 'ai_analyses', ['status'])

    # Anomaly Detections table
    op.create_table(
        'anomaly_detections',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False),
        sa.Column('ai_analysis_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('ai_analyses.id', ondelete='SET NULL')),
        sa.Column('entity_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('entities.id', ondelete='CASCADE'), nullable=False),
        sa.Column('anomaly_type', sa.String(100), nullable=False),
        sa.Column('anomaly_description', sa.Text, nullable=False),
        sa.Column('anomaly_score', sa.Numeric(5, 2), nullable=False),
        sa.Column('baseline_value', sa.String(255)),
        sa.Column('detected_value', sa.String(255)),
        sa.Column('deviation_percentage', sa.Numeric(10, 2)),
        sa.Column('is_reviewed', sa.Boolean, server_default='false'),
        sa.Column('reviewed_by_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='SET NULL')),
        sa.Column('reviewed_at', sa.DateTime(timezone=True)),
        sa.Column('is_confirmed_anomaly', sa.Boolean),
        sa.Column('review_notes', sa.Text),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
    )
    op.create_index('ix_anomaly_detections_entity', 'anomaly_detections', ['entity_id'])
    op.create_index('ix_anomaly_detections_reviewed', 'anomaly_detections', ['is_reviewed'])


def downgrade() -> None:
    op.drop_table('anomaly_detections')
    op.drop_table('ai_analyses')
    op.drop_table('transition_reports')
    op.drop_table('constraint_changes')
    op.drop_table('decision_outcomes')
    op.drop_table('historical_snapshots')
    op.drop_table('risk_justifications')
    op.drop_table('chain_effects')
    op.drop_table('scenario_chains')

    op.execute("DROP TYPE aianalysisstatus")
    op.execute("DROP TYPE aianalysistype")
    op.execute("DROP TYPE effectseverity")
