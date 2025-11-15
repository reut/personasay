"""
Unit tests for SVG generator utilities
"""

import pytest

from app.svg_generator import ensure_kpis_in_summary, generate_svg_dashboard, populate_svg_template


class TestGenerateSvgDashboard:
    """Test SVG dashboard generation"""

    def test_generate_svg_with_complete_data(self, sample_svg_data):
        """Test generating SVG with all data provided"""
        svg = generate_svg_dashboard(sample_svg_data)

        assert svg.startswith("<svg")
        assert "Performance Metrics" in svg
        assert "Speed" in svg
        assert "95.0%" in svg
        assert "Trend Analysis" in svg
        assert "Distribution" in svg

    def test_generate_svg_with_default_data(self):
        """Test generating SVG with minimal/default data"""
        svg = generate_svg_dashboard({})

        assert svg.startswith("<svg")
        assert "Performance Metrics" in svg  # Default title
        assert "Metric 1" in svg  # Default bar name
        assert "Trend Analysis" in svg  # Default line title
        assert "Distribution" in svg  # Default donut title

    def test_generate_svg_with_partial_data(self):
        """Test generating SVG with partial data"""
        partial_data = {
            "bar_title": "Custom Title",
            "bar1_name": "Custom Metric",
            "bar1_value": 85.5,
        }
        svg = generate_svg_dashboard(partial_data)

        assert "Custom Title" in svg
        assert "Custom Metric" in svg
        assert "85.5%" in svg

    def test_svg_structure_validity(self, sample_svg_data):
        """Test that generated SVG has valid structure"""
        svg = generate_svg_dashboard(sample_svg_data)

        # Check for proper SVG tags
        assert svg.count("<svg") == 1
        assert svg.count("</svg>") == 1
        assert "<rect" in svg
        assert "<text" in svg
        assert "<circle" in svg

    def test_svg_with_extreme_values(self):
        """Test SVG generation with extreme values"""
        data = {
            "bar1_value": 100.0,
            "bar2_value": 0.0,
            "bar3_value": 50.0,
            "line1_value": 0,
            "line2_value": 10000,
            "line3_value": 5000,
            "line4_value": 7500,
        }
        svg = generate_svg_dashboard(data)

        assert svg is not None
        assert len(svg) > 1000  # Should generate substantial SVG


class TestPopulateSvgTemplate:
    """Test SVG template population"""

    def test_populate_template_basic(self):
        """Test basic template population"""
        template = "Value: __METRIC_VALUE__"
        data = {"metric_value": 42}

        result = populate_svg_template(template, data)
        assert result == "Value: 42"

    def test_populate_template_with_calculations(self):
        """Test template with bar chart calculations"""
        template = "Height: __PROVIDER_1_HEIGHT__, Y: __PROVIDER_1_Y__"
        data = {"provider_1_perf": 90}

        result = populate_svg_template(template, data)

        # Should have calculated height and y position
        assert "__PROVIDER_1_HEIGHT__" not in result
        assert "__PROVIDER_1_Y__" not in result

    def test_populate_template_preserves_unmapped_values(self):
        """Test that unmapped placeholders are preserved"""
        template = "Known: __VALUE__, Unknown: __UNMAPPED__"
        data = {"value": 100}

        result = populate_svg_template(template, data)
        assert "Known: 100" in result
        assert "__UNMAPPED__" in result  # Should remain unchanged


class TestEnsureKpisInSummary:
    """Test KPI section in summary"""

    def test_summary_with_existing_kpis(self):
        """Test summary that already has KPIs section"""
        summary = """
## 1. Key Insights
Content here

## 6. Success Metrics & KPIs
KPI 1: User engagement
"""
        result = ensure_kpis_in_summary(summary)

        # Should not add duplicate KPIs
        assert result == summary
        assert result.count("Success Metrics & KPIs") == 1

    def test_summary_without_kpis(self):
        """Test summary missing KPIs section"""
        summary = """
## 1. Key Insights
Content here

## 2. Recommendations
More content
"""
        result = ensure_kpis_in_summary(summary)

        # Should add KPIs section
        assert "Success Metrics & KPIs" in result
        # Check that KPIs were added (the actual KPI names may vary)
        assert "KPI 1:" in result
        assert "KPI 2:" in result
        assert len(result) > len(summary)

    def test_summary_with_section_6(self):
        """Test summary with section 6 (different format)"""
        summary = """
## 1. Insights
## 2. Recommendations
## 6. Key Metrics
Content here
"""
        result = ensure_kpis_in_summary(summary)

        # Should not add duplicate
        assert result == summary

    def test_empty_summary(self):
        """Test handling of empty summary"""
        summary = ""
        result = ensure_kpis_in_summary(summary)

        # Should add KPIs
        assert "Success Metrics & KPIs" in result
        assert len(result) > 0
