"""
SVG Dashboard and Visualization Generator for PersonaSay
"""

from typing import Any, Dict


def generate_svg_dashboard(data: Dict[str, Any]) -> str:
    """
    Generate a high-quality, professional SVG dashboard with 3 panels.
    This ensures perfect rendering every time with proper calculations.
    """
    # Extract data with defaults
    bar_title = data.get("bar_title", "Performance Metrics")
    bar_items = [
        {"name": data.get("bar1_name", "Metric 1"), "value": data.get("bar1_value", 95.0)},
        {"name": data.get("bar2_name", "Metric 2"), "value": data.get("bar2_value", 88.0)},
        {"name": data.get("bar3_name", "Metric 3"), "value": data.get("bar3_value", 92.0)},
    ]

    line_title = data.get("line_title", "Trend Analysis")
    line_items = [
        {"label": data.get("line1_label", "Point 1"), "value": data.get("line1_value", 450)},
        {"label": data.get("line2_label", "Point 2"), "value": data.get("line2_value", 820)},
        {"label": data.get("line3_label", "Point 3"), "value": data.get("line3_value", 1250)},
        {"label": data.get("line4_label", "Point 4"), "value": data.get("line4_value", 1700)},
    ]

    donut_title = data.get("donut_title", "Distribution")
    donut_items = [
        {
            "name": data.get("donut1_name", "Category 1"),
            "value": data.get("donut1_value", 50),
            "color": "#ef4444",
        },
        {
            "name": data.get("donut2_name", "Category 2"),
            "value": data.get("donut2_value", 30),
            "color": "#10b981",
        },
        {
            "name": data.get("donut3_name", "Category 3"),
            "value": data.get("donut3_value", 20),
            "color": "#3b82f6",
        },
    ]

    # Calculate bar heights (max 350px for 100%)
    bar_heights = [min(item["value"] * 3.5, 350) for item in bar_items]

    # Calculate line chart positions (normalize to 70-350 range)
    max_val = max(item["value"] for item in line_items)
    min_val = min(item["value"] for item in line_items)
    val_range = max_val - min_val if max_val != min_val else 1
    line_y_positions = [
        420 - ((item["value"] - min_val) / val_range * 280 + 70) for item in line_items
    ]

    # Calculate donut segments (circumference = 2π * 100 = 628)
    circumference = 628
    donut_percentages = [item["value"] / 100 for item in donut_items]
    donut_lengths = [p * circumference for p in donut_percentages]

    # Calculate rotation angles for donut segments
    rotation_angles = [-90]  # Start at top
    cumulative = 0
    for p in donut_percentages[:-1]:
        cumulative += p
        rotation_angles.append(-90 + cumulative * 360)

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="1080" height="620" viewBox="0 0 1080 620">
  <defs>
    <style>
      text {{ font-family: system-ui, -apple-system, sans-serif; }}
      .bg {{ fill: #0f172a; }}
      .panel {{ fill: #1e293b; }}
      .title {{ fill: #f1f5f9; font-size: 18px; font-weight: 600; }}
      .label {{ fill: #cbd5e1; font-size: 13px; }}
      .value {{ fill: #f8fafc; font-size: 16px; font-weight: 600; }}
    </style>
  </defs>

  <rect width="1080" height="620" class="bg"/>

  <!-- Panel 1: Bar Chart -->
  <g transform="translate(40, 40)">
    <rect width="300" height="520" rx="8" class="panel"/>
    <text x="150" y="40" text-anchor="middle" class="title">{bar_title}</text>

    <rect x="40" y="{420 - bar_heights[0]}" width="60" height="{bar_heights[0]}" fill="#3b82f6" rx="3"/>
    <text x="70" y="460" text-anchor="middle" class="value">{bar_items[0]['value']:.1f}%</text>
    <text x="70" y="485" text-anchor="middle" class="label">{bar_items[0]['name']}</text>

    <rect x="120" y="{420 - bar_heights[1]}" width="60" height="{bar_heights[1]}" fill="#10b981" rx="3"/>
    <text x="150" y="460" text-anchor="middle" class="value">{bar_items[1]['value']:.1f}%</text>
    <text x="150" y="485" text-anchor="middle" class="label">{bar_items[1]['name']}</text>

    <rect x="200" y="{420 - bar_heights[2]}" width="60" height="{bar_heights[2]}" fill="#8b5cf6" rx="3"/>
    <text x="230" y="460" text-anchor="middle" class="value">{bar_items[2]['value']:.1f}%</text>
    <text x="230" y="485" text-anchor="middle" class="label">{bar_items[2]['name']}</text>
  </g>

  <!-- Panel 2: Line Chart -->
  <g transform="translate(380, 40)">
    <rect width="300" height="520" rx="8" class="panel"/>
    <text x="150" y="40" text-anchor="middle" class="title">{line_title}</text>

    <polyline points="40,{line_y_positions[0]} 110,{line_y_positions[1]} 180,{line_y_positions[2]} 250,{line_y_positions[3]}"
              stroke="#f59e0b" stroke-width="3" fill="none"/>

    <circle cx="40" cy="{line_y_positions[0]}" r="6" fill="#f59e0b"/>
    <circle cx="110" cy="{line_y_positions[1]}" r="6" fill="#f59e0b"/>
    <circle cx="180" cy="{line_y_positions[2]}" r="6" fill="#f59e0b"/>
    <circle cx="250" cy="{line_y_positions[3]}" r="6" fill="#f59e0b"/>

    <text x="40" y="450" text-anchor="middle" class="label">{line_items[0]['label']}</text>
    <text x="110" y="450" text-anchor="middle" class="label">{line_items[1]['label']}</text>
    <text x="180" y="450" text-anchor="middle" class="label">{line_items[2]['label']}</text>
    <text x="250" y="450" text-anchor="middle" class="label">{line_items[3]['label']}</text>

    <text x="40" y="{line_y_positions[0] - 10}" text-anchor="middle" class="value">{line_items[0]['value']}</text>
    <text x="110" y="{line_y_positions[1] - 10}" text-anchor="middle" class="value">{line_items[1]['value']}</text>
    <text x="180" y="{line_y_positions[2] - 10}" text-anchor="middle" class="value">{line_items[2]['value']}</text>
    <text x="250" y="{line_y_positions[3] - 10}" text-anchor="middle" class="value">{line_items[3]['value']}</text>
  </g>

  <!-- Panel 3: Donut Chart -->
  <g transform="translate(720, 40)">
    <rect width="300" height="520" rx="8" class="panel"/>
    <text x="150" y="40" text-anchor="middle" class="title">{donut_title}</text>

    <g transform="translate(150, 250)">
      <circle r="100" fill="transparent" stroke="{donut_items[0]['color']}" stroke-width="60"
              stroke-dasharray="{donut_lengths[0]} {circumference}" transform="rotate({rotation_angles[0]})"/>
      <circle r="100" fill="transparent" stroke="{donut_items[1]['color']}" stroke-width="60"
              stroke-dasharray="{donut_lengths[1]} {circumference}" transform="rotate({rotation_angles[1]})"/>
      <circle r="100" fill="transparent" stroke="{donut_items[2]['color']}" stroke-width="60"
              stroke-dasharray="{donut_lengths[2]} {circumference}" transform="rotate({rotation_angles[2]})"/>
      <text y="5" text-anchor="middle" class="title">100%</text>
    </g>

    <g transform="translate(40, 400)">
      <rect x="0" y="0" width="20" height="20" fill="{donut_items[0]['color']}" rx="3"/>
      <text x="30" y="15" class="label">{donut_items[0]['name']}: {donut_items[0]['value']}%</text>

      <rect x="0" y="30" width="20" height="20" fill="{donut_items[1]['color']}" rx="3"/>
      <text x="30" y="45" class="label">{donut_items[1]['name']}: {donut_items[1]['value']}%</text>

      <rect x="0" y="60" width="20" height="20" fill="{donut_items[2]['color']}" rx="3"/>
      <text x="30" y="75" class="label">{donut_items[2]['name']}: {donut_items[2]['value']}%</text>
    </g>
  </g>
</svg>"""

    return svg


def populate_svg_template(template: str, data: dict) -> str:
    """Populates an SVG template string with data from a dictionary."""

    # Bar Chart Calculations
    max_height = 350
    for i in range(1, 4):
        perf = data.get(f"provider_{i}_perf", 0)
        height = (perf / 100) * max_height
        data[f"provider_{i}_height"] = height
        data[f"provider_{i}_y"] = 450 - height
        data[f"provider_{i}_label_y"] = 440 - height

    # Line Chart Calculations
    latencies = [
        data.get("league_1_latency", 0),
        data.get("league_2_latency", 0),
        data.get("league_3_latency", 0),
    ]
    max_latency = max(latencies) if latencies else 1
    points = []
    for i in range(1, 4):
        cx = 50 + (i - 1) * 120
        latency = data.get(f"league_{i}_latency", 0)
        cy = 350 - ((latency / max_latency) * 200) if max_latency > 0 else 350
        data[f"league_{i}_cx"] = cx
        data[f"league_{i}_cy"] = cy
        data[f"league_{i}_label_y"] = cy + 30
        data[f"league_{i}_data_y"] = cy - 15
        points.append(f"{cx},{cy}")
    data["league_polyline_points"] = " ".join(points)

    # Donut Chart Calculations
    total_percent = sum(data.get(f"metric_{i}_percent", 0) for i in range(1, 4))
    circumference = 628.32
    offset = 0
    for i in range(1, 4):
        percent = data.get(f"metric_{i}_percent", 0)
        normalized_percent = (percent / total_percent) * 100 if total_percent > 0 else 0
        arc = (normalized_percent / 100) * circumference
        data[f"metric_{i}_arc"] = f"{arc}"
        data[f"metric_{i}_rotate"] = (offset / 100) * 360
        offset += normalized_percent

    # Simple string replacement
    for key, value in data.items():
        template = template.replace(f"__{key.upper()}__", str(value))

    return template


def extract_kpis_as_structured_data(summary_text: str) -> list:
    """Extract KPIs from summary text into structured data format"""
    import re

    kpis = []

    # Pattern to match KPI blocks
    kpi_pattern = r"\*\*KPI (\d+): ([^*]+)\*\*\s*\n?(?:- \*\*What to Measure\*\*: ([^\n]+))?(?:\n- \*\*Target\*\*: ([^\n]+))?(?:\n- \*\*Timeline\*\*: ([^\n]+))?(?:\n- \*\*How to Measure\*\*: ([^\n]+))?(?:\n- \*\*Type\*\*: ([^\n]+))?(?:\n- \*\*Owner\*\*: ([^\n]+))?"

    matches = re.finditer(kpi_pattern, summary_text, re.MULTILINE)

    for match in matches:
        kpi = {
            "id": int(match.group(1)),
            "name": match.group(2).strip() if match.group(2) else "",
            "what_to_measure": match.group(3).strip() if match.group(3) else "",
            "target": match.group(4).strip() if match.group(4) else "",
            "timeline": match.group(5).strip() if match.group(5) else "",
            "how_to_measure": match.group(6).strip() if match.group(6) else "",
            "type": match.group(7).strip() if match.group(7) else "",
            "owner": match.group(8).strip() if match.group(8) else "",
        }
        kpis.append(kpi)

    return kpis


def ensure_kpis_in_summary(summary_text: str) -> str:
    """Ensure summary always has KPIs section with comprehensive metrics"""
    has_section_6 = "## 6." in summary_text or "## 6:" in summary_text
    has_kpi_section = "Success Metrics & KPIs" in summary_text or "KPI" in summary_text

    if has_section_6 or has_kpi_section:
        return summary_text

    # Add comprehensive fallback KPIs
    kpi_section = """

## 6. Success Metrics & KPIs

**KPI 1: Feature Adoption Rate**
- **What to Measure**: Percentage of target users actively using the new feature/product
- **Target**: Achieve 70% adoption rate among target user base
- **Timeline**: Within 90 days of launch
- **How to Measure**: Product analytics tracking daily/weekly active users
- **Type**: Leading indicator
- **Owner**: Product Manager

**KPI 2: User Engagement Score**
- **What to Measure**: Average session duration and interaction frequency with the feature
- **Target**: Increase from baseline by 40%
- **Timeline**: Within 60 days of implementation
- **How to Measure**: Analytics dashboard tracking session metrics
- **Type**: Leading indicator
- **Owner**: Product Analytics Team

**KPI 3: Customer Satisfaction (CSAT)**
- **What to Measure**: User satisfaction score via post-interaction surveys
- **Target**: Maintain CSAT score above 4.2/5.0
- **Timeline**: Ongoing, measured quarterly
- **How to Measure**: In-app surveys and feedback collection
- **Type**: Lagging indicator
- **Owner**: Customer Success Team

**KPI 4: Implementation Success Rate**
- **What to Measure**: Percentage of planned recommendations completed on time
- **Target**: 85% completion rate for priority recommendations
- **Timeline**: Within 6 months
- **How to Measure**: Project management system tracking
- **Type**: Lagging indicator
- **Owner**: Project Lead

**KPI 5: Business Impact**
- **What to Measure**: ROI or revenue impact from implemented changes
- **Target**: Achieve 15% improvement in target business metric
- **Timeline**: Within 12 months of full implementation
- **How to Measure**: Financial reporting and attribution analysis
- **Type**: Lagging indicator
- **Owner**: Business Analytics Team"""

    return summary_text + kpi_section
