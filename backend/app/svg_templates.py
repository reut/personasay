"""
Role-specific SVG Dashboard Templates for PersonaSay
Each role gets a unique dashboard layout and chart combination
"""

from typing import Any, Dict


def generate_trading_dashboard(data: Dict[str, Any]) -> str:
    """
    Trading/Risk roles: Gauge meters + Line chart + Risk indicator
    Focus: Real-time metrics, risk levels, performance trends
    """
    # Extract data
    gauge1_value = min(data.get("gauge1_value", 85), 100)
    gauge1_label = data.get("gauge1_label", "Accuracy")
    gauge2_value = min(data.get("gauge2_value", 92), 100)
    gauge2_label = data.get("gauge2_label", "Margin")

    line_values = [
        data.get("trend1", 450),
        data.get("trend2", 520),
        data.get("trend3", 680),
        data.get("trend4", 890),
    ]
    line_title = data.get("line_title", "Performance Trend")

    risk_value = data.get("risk_level", 2.1)
    risk_label = data.get("risk_label", "Risk Exposure")

    # Calculate positions for line chart
    max_val = max(line_values)
    min_val = min(line_values)
    val_range = max_val - min_val if max_val != min_val else 1

    y_positions = []
    for val in line_values:
        y = 380 - ((val - min_val) / val_range * 180 + 50)
        y_positions.append(y)

    # Calculate gauge angles
    gauge1_angle = (gauge1_value / 100) * 180
    gauge2_angle = (gauge2_value / 100) * 180

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="1080" height="620" viewBox="0 0 1080 620">
  <defs>
    <style>
      text {{ font-family: system-ui, -apple-system, sans-serif; }}
      .bg {{ fill: #0f172a; }}
      .panel {{ fill: #1e293b; }}
      .title {{ fill: #f1f5f9; font-size: 16px; font-weight: 600; }}
      .label {{ fill: #cbd5e1; font-size: 13px; }}
      .value {{ fill: #f8fafc; font-size: 18px; font-weight: 600; }}
    </style>
  </defs>

  <rect width="1080" height="620" class="bg"/>

  <!-- Panel 1: Gauge Meter 1 -->
  <g transform="translate(40, 40)">
    <rect width="300" height="250" rx="8" class="panel"/>
    <text x="150" y="35" text-anchor="middle" class="title">{gauge1_label}</text>

    <!-- Gauge Arc -->
    <g transform="translate(150, 150)">
      <path d="M -80 0 A 80 80 0 0 1 80 0" stroke="#334155" stroke-width="20" fill="none"/>
      <path d="M -80 0 A 80 80 0 0 1 {80 * (gauge1_angle/180) - 80} {-80 * (1 - abs((gauge1_angle - 90)/90))}"
            stroke="#3b82f6" stroke-width="20" fill="none" stroke-linecap="round"/>
      <text y="10" text-anchor="middle" class="value">{gauge1_value}%</text>
    </g>
  </g>

  <!-- Panel 2: Gauge Meter 2 -->
  <g transform="translate(40, 330)">
    <rect width="300" height="250" rx="8" class="panel"/>
    <text x="150" y="35" text-anchor="middle" class="title">{gauge2_label}</text>

    <!-- Gauge Arc -->
    <g transform="translate(150, 150)">
      <path d="M -80 0 A 80 80 0 0 1 80 0" stroke="#334155" stroke-width="20" fill="none"/>
      <path d="M -80 0 A 80 80 0 0 1 {80 * (gauge2_angle/180) - 80} {-80 * (1 - abs((gauge2_angle - 90)/90))}"
            stroke="#10b981" stroke-width="20" fill="none" stroke-linecap="round"/>
      <text y="10" text-anchor="middle" class="value">{gauge2_value}%</text>
    </g>
  </g>

  <!-- Panel 3: Line Chart (Full Height) -->
  <g transform="translate(380, 40)">
    <rect width="660" height="540" rx="8" class="panel"/>
    <text x="330" y="35" text-anchor="middle" class="title">{line_title}</text>

    <!-- Line Chart -->
    <g transform="translate(80, 100)">
      <polyline points="50,{y_positions[0]} 200,{y_positions[1]} 350,{y_positions[2]} 500,{y_positions[3]}"
                stroke="#f59e0b" stroke-width="3" fill="none"/>

      <circle cx="50" cy="{y_positions[0]}" r="6" fill="#f59e0b"/>
      <circle cx="200" cy="{y_positions[1]}" r="6" fill="#f59e0b"/>
      <circle cx="350" cy="{y_positions[2]}" r="6" fill="#f59e0b"/>
      <circle cx="500" cy="{y_positions[3]}" r="6" fill="#f59e0b"/>

      <text x="50" y="380" text-anchor="middle" class="label">Week 1</text>
      <text x="200" y="380" text-anchor="middle" class="label">Week 2</text>
      <text x="350" y="380" text-anchor="middle" class="label">Week 3</text>
      <text x="500" y="380" text-anchor="middle" class="label">Week 4</text>

      <text x="50" y="{y_positions[0] - 15}" text-anchor="middle" class="value">{line_values[0]}</text>
      <text x="200" y="{y_positions[1] - 15}" text-anchor="middle" class="value">{line_values[1]}</text>
      <text x="350" y="{y_positions[2] - 15}" text-anchor="middle" class="value">{line_values[2]}</text>
      <text x="500" y="{y_positions[3] - 15}" text-anchor="middle" class="value">{line_values[3]}</text>
    </g>

    <!-- Risk Indicator -->
    <g transform="translate(80, 440)">
      <text x="0" y="0" class="label">{risk_label}: </text>
      <text x="120" y="0" class="value" fill="#ef4444">{risk_value}%</text>
    </g>
  </g>
</svg>"""


def generate_product_dashboard(data: Dict[str, Any]) -> str:
    """
    Product/PM roles: Funnel chart + Bar comparison + Satisfaction meter
    Focus: User journey, adoption, satisfaction
    """
    funnel_stages = [
        {"name": data.get("funnel1_name", "Awareness"), "value": data.get("funnel1_value", 10000)},
        {"name": data.get("funnel2_name", "Interest"), "value": data.get("funnel2_value", 5000)},
        {"name": data.get("funnel3_name", "Adoption"), "value": data.get("funnel3_value", 2500)},
        {"name": data.get("funnel4_name", "Active"), "value": data.get("funnel4_value", 1500)},
    ]

    bar_items = [
        {"name": data.get("bar1_name", "Segment A"), "value": data.get("bar1_value", 85)},
        {"name": data.get("bar2_name", "Segment B"), "value": data.get("bar2_value", 72)},
    ]
    bar_title = data.get("bar_title", "Adoption by Segment")

    satisfaction = data.get("satisfaction", 4.2)

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="1080" height="620" viewBox="0 0 1080 620">
  <defs>
    <style>
      text {{ font-family: system-ui, -apple-system, sans-serif; }}
      .bg {{ fill: #0f172a; }}
      .panel {{ fill: #1e293b; }}
      .title {{ fill: #f1f5f9; font-size: 16px; font-weight: 600; }}
      .label {{ fill: #cbd5e1; font-size: 13px; }}
      .value {{ fill: #f8fafc; font-size: 16px; font-weight: 600; }}
    </style>
  </defs>

  <rect width="1080" height="620" class="bg"/>

  <!-- Panel 1: Funnel Chart -->
  <g transform="translate(40, 40)">
    <rect width="480" height="540" rx="8" class="panel"/>
    <text x="240" y="35" text-anchor="middle" class="title">User Journey Funnel</text>

    <!-- Funnel stages -->
    <g transform="translate(90, 80)">
      <polygon points="0,0 300,0 270,80 30,80" fill="#3b82f6" opacity="0.9"/>
      <text x="150" y="45" text-anchor="middle" class="label">{funnel_stages[0]['name']}: {funnel_stages[0]['value']:,}</text>

      <polygon points="30,90 270,90 240,170 60,170" fill="#10b981" opacity="0.9"/>
      <text x="150" y="135" text-anchor="middle" class="label">{funnel_stages[1]['name']}: {funnel_stages[1]['value']:,}</text>

      <polygon points="60,180 240,180 210,260 90,260" fill="#f59e0b" opacity="0.9"/>
      <text x="150" y="225" text-anchor="middle" class="label">{funnel_stages[2]['name']}: {funnel_stages[2]['value']:,}</text>

      <polygon points="90,270 210,270 180,350 120,350" fill="#8b5cf6" opacity="0.9"/>
      <text x="150" y="315" text-anchor="middle" class="label">{funnel_stages[3]['name']}: {funnel_stages[3]['value']:,}</text>
    </g>

    <!-- Conversion rate -->
    <text x="240" y="480" text-anchor="middle" class="value">
      Conversion: {(funnel_stages[3]['value'] / funnel_stages[0]['value'] * 100):.1f}%
    </text>
  </g>

  <!-- Panel 2: Bar Comparison -->
  <g transform="translate(560, 40)">
    <rect width="480" height="350" rx="8" class="panel"/>
    <text x="240" y="35" text-anchor="middle" class="title">{bar_title}</text>

    <!-- Horizontal bars -->
    <g transform="translate(80, 100)">
      <rect x="0" y="40" width="{bar_items[0]['value'] * 3.2}" height="50" fill="#3b82f6" rx="4"/>
      <text x="{bar_items[0]['value'] * 3.2 + 15}" y="70" class="value">{bar_items[0]['value']}%</text>
      <text x="0" y="25" class="label">{bar_items[0]['name']}</text>

      <rect x="0" y="140" width="{bar_items[1]['value'] * 3.2}" height="50" fill="#10b981" rx="4"/>
      <text x="{bar_items[1]['value'] * 3.2 + 15}" y="170" class="value">{bar_items[1]['value']}%</text>
      <text x="0" y="125" class="label">{bar_items[1]['name']}</text>
    </g>
  </g>

  <!-- Panel 3: Satisfaction Score -->
  <g transform="translate(560, 430)">
    <rect width="480" height="150" rx="8" class="panel"/>
    <text x="240" y="35" text-anchor="middle" class="title">User Satisfaction</text>

    <g transform="translate(240, 90)">
      <!-- Star rating visualization -->
      <text y="0" text-anchor="middle" class="value" font-size="36" fill="#f59e0b">{satisfaction}/5.0</text>
    </g>
  </g>
</svg>"""


def generate_operations_dashboard(data: Dict[str, Any]) -> str:
    """
    Operations roles: Status indicators + Area chart + Capacity meters
    Focus: System health, uptime, resource utilization
    """
    uptime = data.get("uptime", 99.8)
    incidents = data.get("incidents", 3)
    response_time = data.get("response_time", 245)

    capacity_items = [
        {"name": data.get("capacity1_name", "Server"), "value": data.get("capacity1_value", 68)},
        {"name": data.get("capacity2_name", "Database"), "value": data.get("capacity2_value", 82)},
        {"name": data.get("capacity3_name", "Network"), "value": data.get("capacity3_value", 45)},
    ]

    area_values = [
        data.get("load1", 45),
        data.get("load2", 62),
        data.get("load3", 78),
        data.get("load4", 55),
        data.get("load5", 48),
    ]

    # Calculate area chart path
    max_load = 100
    points = []
    for i, val in enumerate(area_values):
        x = 60 + i * 100
        y = 280 - (val / max_load * 200)
        points.append(f"{x},{y}")

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="1080" height="620" viewBox="0 0 1080 620">
  <defs>
    <style>
      text {{ font-family: system-ui, -apple-system, sans-serif; }}
      .bg {{ fill: #0f172a; }}
      .panel {{ fill: #1e293b; }}
      .title {{ fill: #f1f5f9; font-size: 16px; font-weight: 600; }}
      .label {{ fill: #cbd5e1; font-size: 13px; }}
      .value {{ fill: #f8fafc; font-size: 16px; font-weight: 600; }}
    </style>
    <linearGradient id="areaGradient" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" style="stop-color:#10b981;stop-opacity:0.4" />
      <stop offset="100%" style="stop-color:#10b981;stop-opacity:0.05" />
    </linearGradient>
  </defs>

  <rect width="1080" height="620" class="bg"/>

  <!-- Panel 1: Status Indicators (top row) -->
  <g transform="translate(40, 40)">
    <rect width="320" height="180" rx="8" class="panel"/>
    <g transform="translate(20, 30)">
      <circle cx="15" cy="15" r="12" fill="#10b981"/>
      <text x="40" y="22" class="title">System Uptime</text>
      <text x="40" y="75" class="value" font-size="32">{uptime}%</text>
    </g>
  </g>

  <g transform="translate(400, 40)">
    <rect width="320" height="180" rx="8" class="panel"/>
    <g transform="translate(20, 30)">
      <circle cx="15" cy="15" r="12" fill="#f59e0b"/>
      <text x="40" y="22" class="title">Active Incidents</text>
      <text x="40" y="75" class="value" font-size="32">{incidents}</text>
    </g>
  </g>

  <g transform="translate(760, 40)">
    <rect width="280" height="180" rx="8" class="panel"/>
    <g transform="translate(20, 30)">
      <circle cx="15" cy="15" r="12" fill="#3b82f6"/>
      <text x="40" y="22" class="title">Avg Response</text>
      <text x="40" y="75" class="value" font-size="32">{response_time}ms</text>
    </g>
  </g>

  <!-- Panel 2: Area Chart (System Load) -->
  <g transform="translate(40, 260)">
    <rect width="640" height="320" rx="8" class="panel"/>
    <text x="320" y="35" text-anchor="middle" class="title">System Load Over Time</text>

    <g transform="translate(40, 60)">
      <!-- Area fill -->
      <polygon points="{' '.join(points)} 460,280 60,280" fill="url(#areaGradient)"/>
      <!-- Line -->
      <polyline points="{' '.join(points)}" stroke="#10b981" stroke-width="3" fill="none"/>

      <!-- Data points -->
      {''.join([f'<circle cx="{60 + i * 100}" cy="{280 - (val / max_load * 200)}" r="5" fill="#10b981"/>' for i, val in enumerate(area_values)])}

      <!-- Labels -->
      <text x="60" y="295" text-anchor="middle" class="label">12h</text>
      <text x="160" y="295" text-anchor="middle" class="label">9h</text>
      <text x="260" y="295" text-anchor="middle" class="label">6h</text>
      <text x="360" y="295" text-anchor="middle" class="label">3h</text>
      <text x="460" y="295" text-anchor="middle" class="label">Now</text>
    </g>
  </g>

  <!-- Panel 3: Capacity Meters -->
  <g transform="translate(720, 260)">
    <rect width="320" height="320" rx="8" class="panel"/>
    <text x="160" y="35" text-anchor="middle" class="title">Resource Capacity</text>

    <g transform="translate(40, 80)">
      <!-- Capacity bar 1 -->
      <text x="0" y="15" class="label">{capacity_items[0]['name']}</text>
      <rect x="0" y="25" width="240" height="30" fill="#334155" rx="4"/>
      <rect x="0" y="25" width="{capacity_items[0]['value'] * 2.4}" height="30" fill="#3b82f6" rx="4"/>
      <text x="250" y="45" class="value">{capacity_items[0]['value']}%</text>

      <!-- Capacity bar 2 -->
      <text x="0" y="95" class="label">{capacity_items[1]['name']}</text>
      <rect x="0" y="105" width="240" height="30" fill="#334155" rx="4"/>
      <rect x="0" y="105" width="{capacity_items[1]['value'] * 2.4}" height="30" fill="#10b981" rx="4"/>
      <text x="250" y="125" class="value">{capacity_items[1]['value']}%</text>

      <!-- Capacity bar 3 -->
      <text x="0" y="175" class="label">{capacity_items[2]['name']}</text>
      <rect x="0" y="185" width="240" height="30" fill="#334155" rx="4"/>
      <rect x="0" y="185" width="{capacity_items[2]['value'] * 2.4}" height="30" fill="#8b5cf6" rx="4"/>
      <text x="250" y="205" class="value">{capacity_items[2]['value']}%</text>
    </g>
  </g>
</svg>"""


def generate_analytics_dashboard(data: Dict[str, Any]) -> str:
    """
    Analytics/Data roles: Scatter plot + Heat map grid + Distribution bars
    Focus: Data patterns, correlations, distributions
    """
    # Scatter plot data
    scatter_points = []
    for i in range(8):
        x = data.get(f"scatter_x{i}", 50 + i * 50)
        y = data.get(f"scatter_y{i}", 60 + (i % 3) * 40)
        scatter_points.append((x, y))

    # Heat map data
    heatmap_title = data.get("heatmap_title", "Data Quality Matrix")

    # Distribution bars
    dist_items = [
        {"range": data.get("dist1_range", "0-20"), "count": data.get("dist1_count", 45)},
        {"range": data.get("dist2_range", "20-40"), "count": data.get("dist2_count", 78)},
        {"range": data.get("dist3_range", "40-60"), "count": data.get("dist3_count", 95)},
        {"range": data.get("dist4_range", "60-80"), "count": data.get("dist4_count", 62)},
        {"range": data.get("dist5_range", "80-100"), "count": data.get("dist5_count", 38)},
    ]

    max_count = max(item["count"] for item in dist_items)

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="1080" height="620" viewBox="0 0 1080 620">
  <defs>
    <style>
      text {{ font-family: system-ui, -apple-system, sans-serif; }}
      .bg {{ fill: #0f172a; }}
      .panel {{ fill: #1e293b; }}
      .title {{ fill: #f1f5f9; font-size: 16px; font-weight: 600; }}
      .label {{ fill: #cbd5e1; font-size: 12px; }}
      .value {{ fill: #f8fafc; font-size: 14px; font-weight: 600; }}
    </style>
  </defs>

  <rect width="1080" height="620" class="bg"/>

  <!-- Panel 1: Scatter Plot -->
  <g transform="translate(40, 40)">
    <rect width="640" height="270" rx="8" class="panel"/>
    <text x="320" y="30" text-anchor="middle" class="title">Correlation Analysis</text>

    <g transform="translate(80, 60)">
      <!-- Grid lines -->
      <line x1="0" y1="0" x2="0" y2="180" stroke="#334155" stroke-width="1"/>
      <line x1="0" y1="180" x2="480" y2="180" stroke="#334155" stroke-width="1"/>

      <!-- Scatter points -->
      {''.join([f'<circle cx="{x * 0.9}" cy="{180 - y * 0.9}" r="6" fill="#8b5cf6" opacity="0.7"/>' for x, y in scatter_points])}

      <!-- Trend line -->
      <line x1="0" y1="150" x2="432" y2="50" stroke="#f59e0b" stroke-width="2" stroke-dasharray="5,5"/>

      <text x="240" y="210" text-anchor="middle" class="label">Variable X</text>
      <text x="-90" y="90" text-anchor="middle" class="label" transform="rotate(-90, -90, 90)">Variable Y</text>
    </g>
  </g>

  <!-- Panel 2: Heat Map Grid -->
  <g transform="translate(720, 40)">
    <rect width="320" height="270" rx="8" class="panel"/>
    <text x="160" y="30" text-anchor="middle" class="title">{heatmap_title}</text>

    <g transform="translate(40, 60)">
      <!-- 4x4 heat map grid -->
      <rect x="0" y="0" width="50" height="40" fill="#10b981" opacity="0.9"/>
      <rect x="60" y="0" width="50" height="40" fill="#10b981" opacity="0.6"/>
      <rect x="120" y="0" width="50" height="40" fill="#f59e0b" opacity="0.4"/>
      <rect x="180" y="0" width="50" height="40" fill="#ef4444" opacity="0.3"/>

      <rect x="0" y="50" width="50" height="40" fill="#10b981" opacity="0.7"/>
      <rect x="60" y="50" width="50" height="40" fill="#10b981" opacity="0.9"/>
      <rect x="120" y="50" width="50" height="40" fill="#10b981" opacity="0.5"/>
      <rect x="180" y="50" width="50" height="40" fill="#f59e0b" opacity="0.5"/>

      <rect x="0" y="100" width="50" height="40" fill="#f59e0b" opacity="0.4"/>
      <rect x="60" y="100" width="50" height="40" fill="#10b981" opacity="0.6"/>
      <rect x="120" y="100" width="50" height="40" fill="#10b981" opacity="0.8"/>
      <rect x="180" y="100" width="50" height="40" fill="#f59e0b" opacity="0.6"/>

      <rect x="0" y="150" width="50" height="40" fill="#ef4444" opacity="0.4"/>
      <rect x="60" y="150" width="50" height="40" fill="#f59e0b" opacity="0.5"/>
      <rect x="120" y="150" width="50" height="40" fill="#10b981" opacity="0.7"/>
      <rect x="180" y="150" width="50" height="40" fill="#10b981" opacity="0.8"/>
    </g>
  </g>

  <!-- Panel 3: Distribution Chart -->
  <g transform="translate(40, 350)">
    <rect width="1000" height="230" rx="8" class="panel"/>
    <text x="500" y="30" text-anchor="middle" class="title">Data Distribution</text>

    <g transform="translate(80, 60)">
      {''.join([f'''
      <rect x="{i * 180}" y="{130 - (item['count'] / max_count * 110)}"
            width="140" height="{item['count'] / max_count * 110}"
            fill="#8b5cf6" opacity="0.8" rx="4"/>
      <text x="{i * 180 + 70}" y="{130 - (item['count'] / max_count * 110) - 10}"
            text-anchor="middle" class="value">{item['count']}</text>
      <text x="{i * 180 + 70}" y="155" text-anchor="middle" class="label">{item['range']}</text>
      ''' for i, item in enumerate(dist_items)])}
    </g>
  </g>
</svg>"""


def get_dashboard_template_for_role(role: str, data: Dict[str, Any]) -> str:
    """
    Route to appropriate dashboard template based on role
    """
    role_lower = role.lower()

    if any(keyword in role_lower for keyword in ["trading", "trader", "risk", "quant"]):
        return generate_trading_dashboard(data)

    elif any(
        keyword in role_lower for keyword in ["product", "pm", "owner", "manager", "design", "ux"]
    ):
        return generate_product_dashboard(data)

    elif any(
        keyword in role_lower for keyword in ["operations", "ops", "support", "engineer", "devops"]
    ):
        return generate_operations_dashboard(data)

    elif any(keyword in role_lower for keyword in ["data", "analytics", "analyst", "scientist"]):
        return generate_analytics_dashboard(data)

    else:
        # Default to generic dashboard (original one)
        from app.svg_generator import generate_svg_dashboard

        return generate_svg_dashboard(data)
