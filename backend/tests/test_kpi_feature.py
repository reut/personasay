"""
Test suite for KPI feature in PersonaSay
Tests KPI generation, extraction, and formatting
"""

import pytest

from app.svg_generator import ensure_kpis_in_summary, extract_kpis_as_structured_data


class TestKPIFeature:
    """Test the KPI generation and extraction features"""

    def test_ensure_kpis_adds_fallback_when_missing(self):
        """Test that fallback KPIs are added when summary lacks them"""
        summary_without_kpis = """
## 1. Key Insights
Some insights here.

## 2. Concerns & Opportunities
Some concerns here.
"""

        result = ensure_kpis_in_summary(summary_without_kpis)

        # Verify KPI section was added
        assert "## 6. Success Metrics & KPIs" in result
        assert "**KPI 1:" in result
        assert "Feature Adoption Rate" in result
        assert "**What to Measure**:" in result
        assert "**Target**:" in result
        assert "**Timeline**:" in result

    def test_ensure_kpis_preserves_existing(self):
        """Test that existing KPIs are preserved"""
        summary_with_kpis = """
## 1. Key Insights
Some insights.

## 6. Success Metrics & KPIs

**KPI 1: Custom KPI**
- **What to Measure**: Custom metric
- **Target**: 100%
"""

        result = ensure_kpis_in_summary(summary_with_kpis)

        # Verify original KPIs preserved
        assert "Custom KPI" in result
        assert "Custom metric" in result
        # Should not add duplicate KPI section
        assert result.count("## 6.") == 1

    def test_extract_kpis_as_structured_data(self):
        """Test extraction of KPIs into structured format"""
        summary_with_kpis = """
## 6. Success Metrics & KPIs

**KPI 1: Feature Adoption Rate**
- **What to Measure**: Percentage of users adopting the feature
- **Target**: 75% adoption
- **Timeline**: Within 90 days
- **How to Measure**: Analytics dashboard
- **Type**: Leading indicator
- **Owner**: Product Manager

**KPI 2: User Satisfaction**
- **What to Measure**: CSAT score
- **Target**: Above 4.5/5.0
- **Timeline**: Quarterly measurement
- **How to Measure**: User surveys
- **Type**: Lagging indicator
- **Owner**: Customer Success Team
"""

        kpis = extract_kpis_as_structured_data(summary_with_kpis)

        # Verify correct number of KPIs extracted
        assert len(kpis) == 2

        # Verify first KPI structure
        kpi1 = kpis[0]
        assert kpi1["id"] == 1
        assert kpi1["name"] == "Feature Adoption Rate"
        assert "Percentage of users" in kpi1["what_to_measure"]
        assert "75% adoption" in kpi1["target"]
        assert "90 days" in kpi1["timeline"]
        assert "Analytics dashboard" in kpi1["how_to_measure"]
        assert "Leading indicator" in kpi1["type"]
        assert "Product Manager" in kpi1["owner"]

        # Verify second KPI structure
        kpi2 = kpis[1]
        assert kpi2["id"] == 2
        assert kpi2["name"] == "User Satisfaction"
        assert "CSAT" in kpi2["what_to_measure"]

    def test_extract_kpis_handles_empty_summary(self):
        """Test KPI extraction with no KPIs present"""
        summary_without_kpis = """
## 1. Key Insights
Some insights here.
"""

        kpis = extract_kpis_as_structured_data(summary_without_kpis)

        # Should return empty list
        assert len(kpis) == 0
        assert isinstance(kpis, list)

    def test_kpi_format_validation(self):
        """Test that fallback KPIs include all required fields"""
        summary_without_kpis = "## 1. Key Insights\nSome content"

        result = ensure_kpis_in_summary(summary_without_kpis)
        kpis = extract_kpis_as_structured_data(result)

        # Verify at least 4 KPIs are added
        assert len(kpis) >= 4

        # Verify each KPI has all required fields
        for kpi in kpis:
            assert "id" in kpi and kpi["id"] > 0
            assert "name" in kpi and len(kpi["name"]) > 0
            assert "what_to_measure" in kpi and len(kpi["what_to_measure"]) > 0
            assert "target" in kpi and len(kpi["target"]) > 0
            assert "timeline" in kpi and len(kpi["timeline"]) > 0
            assert "how_to_measure" in kpi and len(kpi["how_to_measure"]) > 0
            assert "type" in kpi and len(kpi["type"]) > 0
            assert "owner" in kpi and len(kpi["owner"]) > 0

    def test_kpi_types_validation(self):
        """Test that KPIs include both leading and lagging indicators"""
        summary_without_kpis = "## 1. Key Insights\nSome content"

        result = ensure_kpis_in_summary(summary_without_kpis)
        kpis = extract_kpis_as_structured_data(result)

        # Extract KPI types
        types = [kpi["type"].lower() for kpi in kpis]

        # Verify mix of leading and lagging indicators
        assert any("leading" in t for t in types), "Should have leading indicators"
        assert any("lagging" in t for t in types), "Should have lagging indicators"

    def test_kpi_section_number(self):
        """Test that KPIs are in section 6"""
        summary_without_kpis = """
## 1. Key Insights
Content

## 2. Concerns
Content
"""

        result = ensure_kpis_in_summary(summary_without_kpis)

        # Verify section number
        assert "## 6. Success Metrics & KPIs" in result
        # Should not be in any other section number
        assert "## 7. Success Metrics" not in result


# Integration test example (requires API running)
@pytest.mark.integration
class TestKPIIntegration:
    """Integration tests for KPI feature (requires running server)"""

    @pytest.mark.asyncio
    async def test_summary_endpoint_returns_kpis(self):
        """Test that /summary endpoint returns KPIs in response"""
        # This would be a full integration test with the API
        # Skipped in unit tests
        pass

    def test_kpi_frontend_rendering(self):
        """Test that frontend correctly renders KPI section"""
        # This would test the frontend rendering logic
        # Could be implemented with React testing library
        pass


if __name__ == "__main__":
    # Run basic tests
    test = TestKPIFeature()

    print("Testing KPI fallback addition...")
    test.test_ensure_kpis_adds_fallback_when_missing()
    print("✓ Fallback KPIs work")

    print("\nTesting KPI preservation...")
    test.test_ensure_kpis_preserves_existing()
    print("✓ Existing KPIs preserved")

    print("\nTesting KPI extraction...")
    test.test_extract_kpis_as_structured_data()
    print("✓ KPI extraction works")

    print("\nTesting KPI format validation...")
    test.test_kpi_format_validation()
    print("✓ KPI format validated")

    print("\nTesting KPI types...")
    test.test_kpi_types_validation()
    print("✓ KPI types validated")

    print("\n✅ All KPI tests passed!")
