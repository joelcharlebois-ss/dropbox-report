"""HTML report generation with sortable table and progress chart."""

from datetime import datetime
from typing import List, Dict, Optional, Any
import json


def generate_html_report(
    folder_data: List[Dict[str, Any]],
    root_path: str,
    history_data: Optional[Dict] = None
) -> str:
    """
    Generate an interactive HTML report with a sortable table and progress chart.

    Args:
        folder_data: List of dictionaries with 'path' and 'file_count' keys
        root_path: The root path that was scanned
        history_data: Optional history dict for trend chart

    Returns:
        Complete HTML document as a string
    """
    timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')
    total_folders = len(folder_data)
    total_files = sum(f['file_count'] for f in folder_data if f['file_count'] >= 0)

    # Build table rows, stripping root path from display
    table_rows = []
    for folder in folder_data:
        path = folder['path']
        count = folder['file_count']

        # Strip root path prefix for privacy
        display_path = path
        if root_path and path.lower().startswith(root_path.lower()):
            display_path = path[len(root_path):]
            if not display_path:
                display_path = '/'
            elif not display_path.startswith('/'):
                display_path = '/' + display_path

        # Handle error cases
        if count < 0:
            count_display = '<span style="color: #dc3545;">Error</span>'
        else:
            count_display = str(count)

        table_rows.append({
            'path': display_path,
            'count': count,
            'count_display': count_display
        })

    # Convert to JSON for Tabulator
    table_data_json = json.dumps([
        {'path': r['path'], 'file_count': r['count']}
        for r in table_rows
    ])

    # Prepare chart data if history is available
    chart_html = ""
    chart_script = ""
    change_indicator_html = ""

    if history_data and history_data.get('data'):
        data_points = history_data['data']

        # Prepare labels (dates) and values (file counts)
        chart_labels = json.dumps([entry.get('date', '') for entry in data_points])
        chart_values = json.dumps([entry.get('total_files', 0) for entry in data_points])

        # Calculate change from yesterday
        if len(data_points) >= 2:
            today_files = data_points[-1].get('total_files', 0)
            yesterday_files = data_points[-2].get('total_files', 0)
            change = today_files - yesterday_files

            if change < 0:
                change_color = "#28a745"  # Green for reduction
                change_icon = "&#x2193;"  # Down arrow
                change_text = f"{abs(change):,} files"
            elif change > 0:
                change_color = "#dc3545"  # Red for increase
                change_icon = "&#x2191;"  # Up arrow
                change_text = f"{change:,} files"
            else:
                change_color = "#666"
                change_icon = "&#x2192;"  # Right arrow
                change_text = "No change"

            change_indicator_html = f'''
            <div class="stat-box change-box">
                <div class="label">Change from Yesterday</div>
                <div class="value" style="color: {change_color};">
                    <span style="font-size: 18px;">{change_icon}</span> {change_text}
                </div>
            </div>'''

        chart_html = '''
        <div class="chart-container">
            <h2 class="chart-title">14-Day Progress</h2>
            <canvas id="progressChart"></canvas>
        </div>'''

        chart_script = f'''
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <script>
            const ctx = document.getElementById('progressChart').getContext('2d');
            new Chart(ctx, {{
                type: 'line',
                data: {{
                    labels: {chart_labels},
                    datasets: [{{
                        label: 'Total Files',
                        data: {chart_values},
                        borderColor: '#0061fe',
                        backgroundColor: 'rgba(0, 97, 254, 0.1)',
                        borderWidth: 2,
                        fill: true,
                        tension: 0.3,
                        pointBackgroundColor: '#0061fe',
                        pointBorderColor: '#fff',
                        pointBorderWidth: 2,
                        pointRadius: 4,
                        pointHoverRadius: 6
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {{
                        legend: {{
                            display: false
                        }},
                        tooltip: {{
                            callbacks: {{
                                label: function(context) {{
                                    return context.parsed.y.toLocaleString() + ' files';
                                }}
                            }}
                        }}
                    }},
                    scales: {{
                        y: {{
                            beginAtZero: true,
                            ticks: {{
                                callback: function(value) {{
                                    return value.toLocaleString();
                                }}
                            }}
                        }},
                        x: {{
                            grid: {{
                                display: false
                            }}
                        }}
                    }}
                }}
            }});
        </script>'''

    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dropbox Folder File Count Report</title>
    <link rel="icon" type="image/x-icon" href="https://api.sortspoke.com/images/favicon.ico">
    <link href="https://unpkg.com/tabulator-tables@5.5.0/dist/css/tabulator.min.css" rel="stylesheet">
    <style>
        * {{
            box-sizing: border-box;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
            color: #333;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        h1 {{
            margin: 0 0 10px 0;
            color: #0061fe;
            font-size: 24px;
        }}
        .meta-info {{
            color: #666;
            font-size: 14px;
            margin-bottom: 20px;
            padding-bottom: 20px;
            border-bottom: 1px solid #eee;
        }}
        .meta-info span {{
            margin-right: 20px;
        }}
        .chart-container {{
            margin-bottom: 25px;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 6px;
            height: 250px;
        }}
        .chart-title {{
            margin: 0 0 15px 0;
            font-size: 16px;
            color: #333;
            font-weight: 600;
        }}
        #progressChart {{
            max-height: 180px;
        }}
        .stats {{
            display: flex;
            gap: 20px;
            margin-bottom: 20px;
            flex-wrap: wrap;
        }}
        .stat-box {{
            background: #f8f9fa;
            padding: 15px 20px;
            border-radius: 6px;
            border-left: 4px solid #0061fe;
        }}
        .stat-box.change-box {{
            border-left-color: #6c757d;
        }}
        .stat-box .label {{
            font-size: 12px;
            color: #666;
            text-transform: uppercase;
        }}
        .stat-box .value {{
            font-size: 24px;
            font-weight: bold;
            color: #333;
        }}
        #folder-table {{
            margin-top: 20px;
        }}
        .tabulator {{
            border: 1px solid #ddd;
            border-radius: 4px;
        }}
        .tabulator-row:nth-child(even) {{
            background-color: #f9f9f9;
        }}
        .tabulator-row:hover {{
            background-color: #e8f4ff !important;
        }}
        .tabulator-header {{
            background-color: #f8f9fa;
            border-bottom: 2px solid #0061fe;
        }}
        .tabulator-col-title {{
            font-weight: 600;
        }}
        .search-box {{
            margin-bottom: 15px;
        }}
        .search-box input {{
            padding: 10px 15px;
            font-size: 14px;
            border: 1px solid #ddd;
            border-radius: 4px;
            width: 300px;
        }}
        .search-box input:focus {{
            outline: none;
            border-color: #0061fe;
            box-shadow: 0 0 0 2px rgba(0,97,254,0.1);
        }}
        .footer {{
            margin-top: 20px;
            padding-top: 20px;
            border-top: 1px solid #eee;
            font-size: 12px;
            color: #999;
            text-align: center;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Dropbox Folder File Count Report</h1>
        <div class="meta-info">
            <span><strong>Generated:</strong> {timestamp}</span>
        </div>

        {chart_html}

        <div class="stats">
            <div class="stat-box">
                <div class="label">Total Folders</div>
                <div class="value">{total_folders:,}</div>
            </div>
            <div class="stat-box">
                <div class="label">Total Files</div>
                <div class="value">{total_files:,}</div>
            </div>
            {change_indicator_html}
        </div>

        <div class="search-box">
            <input type="text" id="search-input" placeholder="Search folders...">
        </div>

        <div id="folder-table"></div>

        <div class="footer">
            Report generated automatically by Dropbox Folder Counter
        </div>
    </div>

    <script src="https://unpkg.com/tabulator-tables@5.5.0/dist/js/tabulator.min.js"></script>
    {chart_script}
    <script>
        function escapeHtml(text) {{
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }}

        const tableData = {table_data_json};

        const table = new Tabulator("#folder-table", {{
            data: tableData,
            layout: "fitColumns",
            pagination: "local",
            paginationSize: 50,
            paginationSizeSelector: [25, 50, 100, 250, true],
            columns: [
                {{
                    title: "Folder Path",
                    field: "path",
                    sorter: "string",
                    headerFilter: false,
                    widthGrow: 3,
                    formatter: function(cell) {{
                        const value = cell.getValue();
                        return '<span style="font-family: monospace;">' + escapeHtml(value) + '</span>';
                    }}
                }},
                {{
                    title: "File Count",
                    field: "file_count",
                    sorter: "number",
                    hozAlign: "right",
                    headerHozAlign: "right",
                    width: 150,
                    formatter: function(cell) {{
                        const value = cell.getValue();
                        if (value < 0) {{
                            return '<span style="color: #dc3545;">Error</span>';
                        }}
                        return value.toLocaleString();
                    }}
                }}
            ],
            initialSort: [
                {{column: "path", dir: "asc"}}
            ]
        }});

        // Search functionality
        document.getElementById("search-input").addEventListener("input", function(e) {{
            const searchTerm = e.target.value.toLowerCase();
            table.setFilter("path", "like", searchTerm);
        }});
    </script>
</body>
</html>'''

    return html
