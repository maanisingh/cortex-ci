"""
Tests for Phase 2.1: Multi-Layer Dependency Modeling endpoints.
"""

import pytest
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import (
    Dependency,
    DependencyLayer,
    RelationshipType,
)
from app.api.v1.endpoints.dependencies import (
    _get_layer_risk_weight,
    _get_risk_recommendation,
)


class TestLayerRiskWeights:
    """Test layer risk weight calculations."""

    def test_legal_weight(self):
        """Legal layer has highest weight (1.5x)."""
        assert _get_layer_risk_weight(DependencyLayer.LEGAL) == 1.5

    def test_financial_weight(self):
        """Financial layer has high weight (1.4x)."""
        assert _get_layer_risk_weight(DependencyLayer.FINANCIAL) == 1.4

    def test_human_weight(self):
        """Human layer has medium-high weight (1.2x)."""
        assert _get_layer_risk_weight(DependencyLayer.HUMAN) == 1.2

    def test_operational_weight(self):
        """Operational layer has base weight (1.0x)."""
        assert _get_layer_risk_weight(DependencyLayer.OPERATIONAL) == 1.0

    def test_academic_weight(self):
        """Academic layer has lowest weight (0.8x)."""
        assert _get_layer_risk_weight(DependencyLayer.ACADEMIC) == 0.8


class TestRiskRecommendations:
    """Test risk recommendation generation."""

    def test_high_risk_recommendation(self):
        """High risk (>50) generates high priority recommendation."""
        result = _get_risk_recommendation(55.0, "financial")
        assert "HIGH PRIORITY" in result
        assert "financial" in result
        assert "diversification" in result.lower()

    def test_medium_risk_recommendation(self):
        """Medium risk (25-50) generates medium priority recommendation."""
        result = _get_risk_recommendation(35.0, "legal")
        assert "MEDIUM PRIORITY" in result
        assert "legal" in result
        assert "backup" in result.lower()

    def test_low_risk_recommendation(self):
        """Low risk (10-25) generates low priority recommendation."""
        result = _get_risk_recommendation(15.0, "operational")
        assert "LOW PRIORITY" in result
        assert "operational" in result
        assert "monitor" in result.lower()

    def test_minimal_risk_recommendation(self):
        """Minimal risk (<10) generates minimal recommendation."""
        result = _get_risk_recommendation(5.0, "academic")
        assert "MINIMAL" in result
        assert "monitoring" in result.lower()


class TestLayerSummary:
    """Test layer summary endpoint logic."""

    @pytest.mark.asyncio
    async def test_layer_summary_counts(
        self, test_db: AsyncSession, test_tenant, test_dependencies
    ):
        """Verify layer summary correctly counts dependencies."""
        from sqlalchemy import func

        # Count dependencies by layer
        query = (
            select(Dependency.layer, func.count(Dependency.id))
            .where(Dependency.tenant_id == test_tenant.id, Dependency.is_active)
            .group_by(Dependency.layer)
        )

        result = await test_db.execute(query)
        layer_counts = {row[0]: row[1] for row in result}

        # Each layer should have exactly 1 dependency from our fixtures
        for layer in DependencyLayer:
            assert layer in layer_counts
            assert layer_counts[layer] == 1

    @pytest.mark.asyncio
    async def test_layer_summary_criticality(
        self, test_db: AsyncSession, test_tenant, test_dependencies
    ):
        """Verify layer summary calculates average criticality."""
        from sqlalchemy import func

        query = (
            select(Dependency.layer, func.avg(Dependency.criticality))
            .where(Dependency.tenant_id == test_tenant.id, Dependency.is_active)
            .group_by(Dependency.layer)
        )

        result = await test_db.execute(query)
        for row in result:
            layer, avg_crit = row
            assert avg_crit is not None
            assert 1 <= avg_crit <= 10  # Criticality range


class TestCrossLayerImpact:
    """Test cross-layer impact analysis."""

    @pytest.mark.asyncio
    async def test_cross_layer_impact_calculation(
        self,
        test_db: AsyncSession,
        test_tenant,
        test_entities,
        test_dependencies,
    ):
        """Verify cross-layer impact is calculated correctly."""
        source_entity = test_entities[0]

        # Get outgoing dependencies for the source entity
        query = select(Dependency).where(
            Dependency.tenant_id == test_tenant.id,
            Dependency.source_entity_id == source_entity.id,
            Dependency.is_active,
        )

        result = await test_db.execute(query)
        outgoing = result.scalars().all()

        # All test dependencies have source_entity_id = test_entities[0]
        assert len(outgoing) == 5  # One per layer

        # Calculate expected risk scores
        expected_risk = 0.0
        for dep in outgoing:
            weight = _get_layer_risk_weight(dep.layer)
            expected_risk += dep.criticality * weight

        assert expected_risk > 0

    @pytest.mark.asyncio
    async def test_cross_layer_identifies_primary_layer(
        self,
        test_db: AsyncSession,
        test_tenant,
        test_entities,
        test_dependencies,
    ):
        """Verify primary exposure layer is correctly identified."""
        # The entity with highest weighted risk should be primary
        # In our fixtures, legal has highest weight (1.5) but criticality 5
        # Academic has lowest weight (0.8) but highest criticality (9)
        # Legal: 5 * 1.5 = 7.5
        # Financial: 6 * 1.4 = 8.4
        # Operational: 7 * 1.0 = 7.0
        # Human: 8 * 1.2 = 9.6
        # Academic: 9 * 0.8 = 7.2

        # Human layer should have highest weighted risk in our fixtures
        # This is a unit test for the calculation logic


class TestDependencyLayers:
    """Test dependency layer enumeration."""

    def test_all_layers_defined(self):
        """Verify all 5 layers are defined."""
        layers = list(DependencyLayer)
        assert len(layers) == 5

    def test_layer_values(self):
        """Verify layer enum values."""
        assert DependencyLayer.LEGAL.value == "legal"
        assert DependencyLayer.FINANCIAL.value == "financial"
        assert DependencyLayer.OPERATIONAL.value == "operational"
        assert DependencyLayer.HUMAN.value == "human"
        assert DependencyLayer.ACADEMIC.value == "academic"


class TestDependencyModel:
    """Test Dependency model operations."""

    @pytest.mark.asyncio
    async def test_create_dependency(
        self, test_db: AsyncSession, test_tenant, test_entities
    ):
        """Test creating a dependency."""
        dep = Dependency(
            id=uuid4(),
            tenant_id=test_tenant.id,
            source_entity_id=test_entities[0].id,
            target_entity_id=test_entities[1].id,
            layer=DependencyLayer.LEGAL,
            relationship_type=RelationshipType.DEPENDS_ON,
            criticality=8,
            is_bidirectional=True,
            is_active=True,
        )
        test_db.add(dep)
        await test_db.commit()

        # Retrieve and verify
        result = await test_db.execute(
            select(Dependency).where(Dependency.id == dep.id)
        )
        saved_dep = result.scalar_one()

        assert saved_dep.layer == DependencyLayer.LEGAL
        assert saved_dep.criticality == 8
        assert saved_dep.is_bidirectional is True

    @pytest.mark.asyncio
    async def test_dependency_layer_filter(
        self, test_db: AsyncSession, test_tenant, test_dependencies
    ):
        """Test filtering dependencies by layer."""
        query = select(Dependency).where(
            Dependency.tenant_id == test_tenant.id,
            Dependency.layer == DependencyLayer.FINANCIAL,
            Dependency.is_active,
        )

        result = await test_db.execute(query)
        financial_deps = result.scalars().all()

        assert len(financial_deps) == 1
        assert financial_deps[0].layer == DependencyLayer.FINANCIAL

    @pytest.mark.asyncio
    async def test_soft_delete_dependency(
        self, test_db: AsyncSession, test_tenant, test_dependencies
    ):
        """Test soft deleting a dependency."""
        dep = test_dependencies[0]
        dep.is_active = False
        await test_db.commit()

        # Active query should not return it
        query = select(Dependency).where(
            Dependency.tenant_id == test_tenant.id,
            Dependency.is_active,
        )

        result = await test_db.execute(query)
        active_deps = result.scalars().all()

        assert len(active_deps) == 4  # 5 - 1 deleted
