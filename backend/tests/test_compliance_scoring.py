"""
Tests for Compliance Scoring API Endpoints.
"""

import pytest
import pytest_asyncio
from uuid import uuid4
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Tenant, User
from app.models.compliance.framework import (
    Framework, Control, FrameworkType, ControlCategory, AssessmentResult
)
from app.core.security import create_access_token


@pytest_asyncio.fixture
async def test_frameworks(test_db: AsyncSession, test_tenant: Tenant) -> list[Framework]:
    """Create test frameworks with controls."""
    frameworks = []

    # Create ISO 27001 framework
    iso_framework = Framework(
        id=uuid4(),
        tenant_id=test_tenant.id,
        type=FrameworkType.ISO_27001,
        name="ISO/IEC 27001:2022",
        version="2022",
        description="Information Security Management System",
        is_active=True,
        total_controls=10,
    )
    test_db.add(iso_framework)
    frameworks.append(iso_framework)

    # Create SOC 2 framework
    soc2_framework = Framework(
        id=uuid4(),
        tenant_id=test_tenant.id,
        type=FrameworkType.SOC_2,
        name="SOC 2 Type II",
        version="2022",
        description="Service Organization Control 2",
        is_active=True,
        total_controls=5,
    )
    test_db.add(soc2_framework)
    frameworks.append(soc2_framework)

    await test_db.commit()
    for fw in frameworks:
        await test_db.refresh(fw)
    return frameworks


@pytest_asyncio.fixture
async def test_controls(
    test_db: AsyncSession, test_tenant: Tenant, test_frameworks: list[Framework]
) -> list[Control]:
    """Create test controls with various implementation statuses."""
    controls = []
    iso_framework = test_frameworks[0]
    soc2_framework = test_frameworks[1]

    # ISO 27001 controls - mix of statuses
    iso_control_data = [
        ("A.5.1", "Policies for information security", AssessmentResult.FULLY_IMPLEMENTED, 1),
        ("A.5.2", "Information security roles", AssessmentResult.FULLY_IMPLEMENTED, 1),
        ("A.5.3", "Segregation of duties", AssessmentResult.PARTIALLY_IMPLEMENTED, 2),
        ("A.5.4", "Management responsibilities", AssessmentResult.PARTIALLY_IMPLEMENTED, 2),
        ("A.5.5", "Contact with authorities", AssessmentResult.NOT_IMPLEMENTED, 1),
        ("A.5.6", "Contact with special groups", AssessmentResult.NOT_IMPLEMENTED, 2),
        ("A.5.7", "Threat intelligence", AssessmentResult.NOT_ASSESSED, 2),
        ("A.5.8", "Information security in projects", AssessmentResult.NOT_ASSESSED, 3),
        ("A.5.9", "Inventory of information assets", AssessmentResult.FULLY_IMPLEMENTED, 1),
        ("A.5.10", "Acceptable use of assets", AssessmentResult.PARTIALLY_IMPLEMENTED, 2),
    ]

    for control_id, title, status, priority in iso_control_data:
        control = Control(
            id=uuid4(),
            tenant_id=test_tenant.id,
            framework_id=iso_framework.id,
            control_id=control_id,
            title=title,
            description=f"Description for {control_id}",
            category=ControlCategory.GOVERNANCE,
            implementation_status=status,
            priority=priority,
        )
        test_db.add(control)
        controls.append(control)

    # SOC 2 controls
    soc2_control_data = [
        ("CC1.1", "Control Environment", AssessmentResult.FULLY_IMPLEMENTED, 1),
        ("CC1.2", "Board of Directors", AssessmentResult.FULLY_IMPLEMENTED, 1),
        ("CC1.3", "Management Philosophy", AssessmentResult.NOT_IMPLEMENTED, 1),
        ("CC1.4", "Organizational Structure", AssessmentResult.PARTIALLY_IMPLEMENTED, 2),
        ("CC1.5", "Commitment to Competence", AssessmentResult.NOT_ASSESSED, 2),
    ]

    for control_id, title, status, priority in soc2_control_data:
        control = Control(
            id=uuid4(),
            tenant_id=test_tenant.id,
            framework_id=soc2_framework.id,
            control_id=control_id,
            title=title,
            description=f"Description for {control_id}",
            category=ControlCategory.GOVERNANCE,
            implementation_status=status,
            priority=priority,
        )
        test_db.add(control)
        controls.append(control)

    await test_db.commit()
    for c in controls:
        await test_db.refresh(c)
    return controls


@pytest_asyncio.fixture
async def auth_headers(test_user: User, test_tenant: Tenant) -> dict:
    """Create authentication headers for API requests."""
    token = create_access_token(
        user_id=test_user.id,
        tenant_id=test_tenant.id,
        role=test_user.role,
    )
    return {
        "Authorization": f"Bearer {token}",
        "X-Tenant-ID": str(test_tenant.id),
    }


class TestComplianceScoreEndpoint:
    """Tests for GET /v1/compliance/scoring/score endpoint."""

    @pytest.mark.asyncio
    async def test_get_overall_score(
        self,
        test_client: AsyncClient,
        test_frameworks: list[Framework],
        test_controls: list[Control],
        auth_headers: dict,
    ):
        """Test getting overall compliance score."""
        response = await test_client.get(
            "/v1/compliance/scoring/score",
            headers=auth_headers,
        )
        assert response.status_code == 200

        data = response.json()
        assert "overall_score" in data
        assert "overall_grade" in data
        assert "total_frameworks" in data
        assert "total_controls" in data
        assert "frameworks" in data

        # Verify totals
        assert data["total_frameworks"] == 2
        assert data["total_controls"] == 15

        # Verify score calculation
        # ISO: 3 fully (300) + 3 partial (150) = 450 / 10 = 45%
        # SOC2: 2 fully (200) + 1 partial (50) = 250 / 5 = 50%
        # Overall: (450 + 250) / 15 = 46.67%
        assert 40.0 <= data["overall_score"] <= 55.0

    @pytest.mark.asyncio
    async def test_get_score_by_framework(
        self,
        test_client: AsyncClient,
        test_frameworks: list[Framework],
        test_controls: list[Control],
        auth_headers: dict,
    ):
        """Test getting score for a specific framework."""
        framework_id = str(test_frameworks[0].id)  # ISO 27001

        response = await test_client.get(
            f"/v1/compliance/scoring/score?framework_id={framework_id}",
            headers=auth_headers,
        )
        assert response.status_code == 200

        data = response.json()
        assert data["total_frameworks"] == 1
        assert data["total_controls"] == 10

    @pytest.mark.asyncio
    async def test_get_score_unauthenticated(
        self,
        test_client: AsyncClient,
    ):
        """Test that unauthenticated requests are rejected."""
        response = await test_client.get("/v1/compliance/scoring/score")
        assert response.status_code == 401


class TestComplianceGapsEndpoint:
    """Tests for GET /v1/compliance/scoring/gaps endpoint."""

    @pytest.mark.asyncio
    async def test_get_all_gaps(
        self,
        test_client: AsyncClient,
        test_frameworks: list[Framework],
        test_controls: list[Control],
        auth_headers: dict,
    ):
        """Test getting all compliance gaps."""
        response = await test_client.get(
            "/v1/compliance/scoring/gaps",
            headers=auth_headers,
        )
        assert response.status_code == 200

        data = response.json()
        assert "total_gaps" in data
        assert "critical" in data
        assert "high" in data
        assert "medium" in data
        assert "low" in data

        # We have controls that are NOT_IMPLEMENTED and PARTIALLY_IMPLEMENTED
        # which should show up as gaps
        assert data["total_gaps"] > 0

    @pytest.mark.asyncio
    async def test_get_gaps_by_severity(
        self,
        test_client: AsyncClient,
        test_frameworks: list[Framework],
        test_controls: list[Control],
        auth_headers: dict,
    ):
        """Test filtering gaps by severity."""
        response = await test_client.get(
            "/v1/compliance/scoring/gaps?severity=CRITICAL",
            headers=auth_headers,
        )
        assert response.status_code == 200

        data = response.json()
        # All returned gaps should be filtered (though critical might be empty)
        assert "total_gaps" in data

    @pytest.mark.asyncio
    async def test_get_gaps_by_framework(
        self,
        test_client: AsyncClient,
        test_frameworks: list[Framework],
        test_controls: list[Control],
        auth_headers: dict,
    ):
        """Test filtering gaps by framework."""
        framework_id = str(test_frameworks[0].id)

        response = await test_client.get(
            f"/v1/compliance/scoring/gaps?framework_id={framework_id}",
            headers=auth_headers,
        )
        assert response.status_code == 200

        data = response.json()
        # All gaps should be from ISO 27001
        for severity in ["critical", "high", "medium", "low"]:
            for gap in data.get(severity, []):
                assert gap["framework_id"] == framework_id


class TestComplianceMappingEndpoint:
    """Tests for GET /v1/compliance/scoring/mapping endpoint."""

    @pytest.mark.asyncio
    async def test_get_framework_mapping(
        self,
        test_client: AsyncClient,
        test_frameworks: list[Framework],
        auth_headers: dict,
    ):
        """Test getting cross-framework mappings."""
        response = await test_client.get(
            "/v1/compliance/scoring/mapping",
            headers=auth_headers,
        )
        assert response.status_code == 200

        data = response.json()
        assert "total_frameworks" in data
        assert "mappings" in data
        assert "summary" in data


class TestComplianceDashboardEndpoint:
    """Tests for GET /v1/compliance/scoring/dashboard endpoint."""

    @pytest.mark.asyncio
    async def test_get_dashboard(
        self,
        test_client: AsyncClient,
        test_frameworks: list[Framework],
        test_controls: list[Control],
        auth_headers: dict,
    ):
        """Test getting compliance dashboard summary."""
        response = await test_client.get(
            "/v1/compliance/scoring/dashboard",
            headers=auth_headers,
        )
        assert response.status_code == 200

        data = response.json()

        # Verify dashboard structure
        assert "score" in data
        assert "summary" in data
        assert "frameworks" in data
        assert "top_gaps" in data
        assert "efficiency" in data
        assert "recent_activity" in data

        # Verify score section
        assert "overall" in data["score"]
        assert "grade" in data["score"]
        assert "trend" in data["score"]

        # Verify summary section
        assert data["summary"]["total_frameworks"] == 2
        assert data["summary"]["total_controls"] == 15

    @pytest.mark.asyncio
    async def test_dashboard_without_data(
        self,
        test_client: AsyncClient,
        test_tenant: Tenant,
        auth_headers: dict,
    ):
        """Test dashboard with no frameworks/controls."""
        response = await test_client.get(
            "/v1/compliance/scoring/dashboard",
            headers=auth_headers,
        )
        assert response.status_code == 200

        data = response.json()
        assert data["summary"]["total_frameworks"] == 0
        assert data["summary"]["total_controls"] == 0
        assert data["score"]["overall"] == 0.0


class TestScoreCalculation:
    """Tests for compliance score calculation logic."""

    @pytest.mark.asyncio
    async def test_score_with_all_implemented(
        self,
        test_db: AsyncSession,
        test_tenant: Tenant,
        test_client: AsyncClient,
        auth_headers: dict,
    ):
        """Test score when all controls are fully implemented."""
        # Create a framework with all controls implemented
        framework = Framework(
            id=uuid4(),
            tenant_id=test_tenant.id,
            type=FrameworkType.CUSTOM,
            name="Test Framework",
            version="1.0",
            is_active=True,
        )
        test_db.add(framework)

        for i in range(5):
            control = Control(
                id=uuid4(),
                tenant_id=test_tenant.id,
                framework_id=framework.id,
                control_id=f"TEST-{i}",
                title=f"Test Control {i}",
                description=f"Description {i}",
                implementation_status=AssessmentResult.FULLY_IMPLEMENTED,
            )
            test_db.add(control)

        await test_db.commit()

        response = await test_client.get(
            f"/v1/compliance/scoring/score?framework_id={framework.id}",
            headers=auth_headers,
        )
        assert response.status_code == 200

        data = response.json()
        # All controls implemented = 100% score
        assert data["overall_score"] == 100.0
        assert data["overall_grade"] == "A"

    @pytest.mark.asyncio
    async def test_score_with_none_implemented(
        self,
        test_db: AsyncSession,
        test_tenant: Tenant,
        test_client: AsyncClient,
        auth_headers: dict,
    ):
        """Test score when no controls are implemented."""
        framework = Framework(
            id=uuid4(),
            tenant_id=test_tenant.id,
            type=FrameworkType.CUSTOM,
            name="Test Framework 2",
            version="1.0",
            is_active=True,
        )
        test_db.add(framework)

        for i in range(5):
            control = Control(
                id=uuid4(),
                tenant_id=test_tenant.id,
                framework_id=framework.id,
                control_id=f"TEST2-{i}",
                title=f"Test Control {i}",
                description=f"Description {i}",
                implementation_status=AssessmentResult.NOT_IMPLEMENTED,
            )
            test_db.add(control)

        await test_db.commit()

        response = await test_client.get(
            f"/v1/compliance/scoring/score?framework_id={framework.id}",
            headers=auth_headers,
        )
        assert response.status_code == 200

        data = response.json()
        # No controls implemented = 0% score
        assert data["overall_score"] == 0.0
        assert data["overall_grade"] == "F"

    @pytest.mark.asyncio
    async def test_partial_implementation_score(
        self,
        test_db: AsyncSession,
        test_tenant: Tenant,
        test_client: AsyncClient,
        auth_headers: dict,
    ):
        """Test score calculation with partially implemented controls."""
        framework = Framework(
            id=uuid4(),
            tenant_id=test_tenant.id,
            type=FrameworkType.CUSTOM,
            name="Test Framework 3",
            version="1.0",
            is_active=True,
        )
        test_db.add(framework)

        # 2 controls, both partially implemented = 50% each = 50% total
        for i in range(2):
            control = Control(
                id=uuid4(),
                tenant_id=test_tenant.id,
                framework_id=framework.id,
                control_id=f"TEST3-{i}",
                title=f"Test Control {i}",
                description=f"Description {i}",
                implementation_status=AssessmentResult.PARTIALLY_IMPLEMENTED,
            )
            test_db.add(control)

        await test_db.commit()

        response = await test_client.get(
            f"/v1/compliance/scoring/score?framework_id={framework.id}",
            headers=auth_headers,
        )
        assert response.status_code == 200

        data = response.json()
        # All partially implemented = 50% score
        assert data["overall_score"] == 50.0
        assert data["overall_grade"] == "F"  # 50% is grade F
