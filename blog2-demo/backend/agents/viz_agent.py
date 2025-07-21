"""Visualization Agent - Creates charts and visual representations"""
from typing import Dict, Any, List
from .base_agent import BaseAgent
from mcp.schemas import MCPTool, ToolParameter, ParameterType
import json

class VisualizationAgent(BaseAgent):
    AGENT_TYPE = "visualization"
    
    def __init__(self):
        super().__init__(
            agent_id="viz-agent-001",
            name="Visualization Agent",
            description="Creates charts, graphs, and visual representations of data"
        )
    
    def _register_tools(self):
        """Register MCP tools for visualization"""
        # Create chart tool
        self.register_tool(
            MCPTool(
                name="create_chart",
                description="Generate interactive charts from data",
                parameters=[
                    ToolParameter(
                        name="chart_type",
                        type=ParameterType.STRING,
                        description="Type of chart to create",
                        required=True,
                        enum=["line", "bar", "pie", "scatter", "area"]
                    ),
                    ToolParameter(
                        name="data",
                        type=ParameterType.OBJECT,
                        description="Data to visualize",
                        required=True
                    ),
                    ToolParameter(
                        name="title",
                        type=ParameterType.STRING,
                        description="Chart title",
                        required=False
                    ),
                    ToolParameter(
                        name="x_axis",
                        type=ParameterType.STRING,
                        description="X-axis field name",
                        required=False
                    ),
                    ToolParameter(
                        name="y_axis",
                        type=ParameterType.STRING,
                        description="Y-axis field name",
                        required=False
                    )
                ],
                returns={
                    "type": "object",
                    "description": "Chart configuration for rendering"
                },
                examples=[
                    {
                        "parameters": {
                            "chart_type": "line",
                            "data": {"x": [2020, 2021, 2022], "y": [100, 150, 200]},
                            "title": "Growth Over Time"
                        },
                        "description": "Create a line chart showing growth"
                    }
                ]
            ),
            self._execute_create_chart
        )
        
        # Create comparison chart tool
        self.register_tool(
            MCPTool(
                name="create_comparison",
                description="Create comparison visualizations",
                parameters=[
                    ToolParameter(
                        name="data",
                        type=ParameterType.OBJECT,
                        description="Data to compare",
                        required=True
                    ),
                    ToolParameter(
                        name="comparison_type",
                        type=ParameterType.STRING,
                        description="Type of comparison",
                        required=True,
                        enum=["side_by_side", "stacked", "grouped"]
                    ),
                    ToolParameter(
                        name="categories",
                        type=ParameterType.ARRAY,
                        description="Categories to compare",
                        required=True
                    )
                ],
                returns={
                    "type": "object",
                    "description": "Comparison visualization configuration"
                },
                examples=[
                    {
                        "parameters": {
                            "comparison_type": "side_by_side",
                            "categories": ["solar", "wind", "hydro"],
                            "data": {"countries": ["USA", "China"], "values": [[100, 200], [300, 400]]}
                        },
                        "description": "Compare energy types across countries"
                    }
                ]
            ),
            self._execute_create_comparison
        )
        
        # Create dashboard tool
        self.register_tool(
            MCPTool(
                name="create_dashboard",
                description="Create a dashboard with multiple visualizations",
                parameters=[
                    ToolParameter(
                        name="visualizations",
                        type=ParameterType.ARRAY,
                        description="List of visualization configurations",
                        required=True
                    ),
                    ToolParameter(
                        name="layout",
                        type=ParameterType.STRING,
                        description="Dashboard layout",
                        required=False,
                        enum=["grid", "vertical", "horizontal"],
                        default="grid"
                    )
                ],
                returns={
                    "type": "object",
                    "description": "Dashboard configuration"
                },
                examples=[
                    {
                        "parameters": {
                            "visualizations": [{"type": "chart"}, {"type": "table"}],
                            "layout": "grid"
                        },
                        "description": "Create a dashboard with charts and tables"
                    }
                ]
            ),
            self._execute_create_dashboard
        )
    
    async def _execute_create_chart(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Generate chart configuration"""
        chart_type = parameters["chart_type"]
        data = parameters["data"]
        title = parameters.get("title", "")
        
        # Use LLM to enhance chart configuration if available
        enhanced_config = None
        if self.llm.is_available() and title:
            prompt = f"""Given this data for a {chart_type} chart titled "{title}":
{json.dumps(data, indent=2)}

Suggest the best configuration including:
1. Appropriate axis labels
2. Color scheme
3. Any data transformations needed
4. Chart-specific options

Respond with JSON containing: axis_labels, colors, options"""
            
            enhanced_config = await self.llm.generate_json(prompt)
        
        # Generate React component code for the chart
        component_code = self._generate_chart_component(
            chart_type=chart_type,
            data=data,
            title=title,
            x_axis=parameters.get("x_axis", "x"),
            y_axis=parameters.get("y_axis", "y"),
            enhanced_config=enhanced_config
        )
        
        return {
            "type": "chart",
            "chart_type": chart_type,
            "component_code": component_code,
            "config": {
                "data": data,
                "title": title,
                "x_axis": parameters.get("x_axis", "x"),
                "y_axis": parameters.get("y_axis", "y"),
                "enhanced": enhanced_config
            }
        }
    
    async def _execute_create_comparison(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comparison visualization"""
        comparison_type = parameters["comparison_type"]
        data = parameters["data"]
        categories = parameters["categories"]
        
        # Generate comparison visualization component
        component_code = self._generate_comparison_component(
            comparison_type=comparison_type,
            data=data,
            categories=categories
        )
        
        return {
            "type": "comparison",
            "comparison_type": comparison_type,
            "component_code": component_code,
            "config": {
                "data": data,
                "categories": categories
            }
        }
    
    async def _execute_create_dashboard(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Generate dashboard configuration"""
        visualizations = parameters["visualizations"]
        layout = parameters.get("layout", "grid")
        
        return {
            "type": "dashboard",
            "layout": layout,
            "visualizations": visualizations,
            "component_code": self._generate_dashboard_component(visualizations, layout)
        }
    
    def _generate_chart_component(self, chart_type: str, data: Dict, title: str, x_axis: str, y_axis: str, enhanced_config: Dict = None) -> str:
        """Generate React component code for a chart"""
        return f'''
import {{ Line, Bar, Pie, Scatter }} from 'react-chartjs-2';
import {{ Chart as ChartJS, registerables }} from 'chart.js';

ChartJS.register(...registerables);

export default function GeneratedChart() {{
  const chartData = {{
    labels: {json.dumps(data.get(x_axis, []))},
    datasets: [{{
      label: '{title}',
      data: {json.dumps(data.get(y_axis, []))},
      backgroundColor: 'rgba(59, 130, 246, 0.5)',
      borderColor: 'rgb(59, 130, 246)',
      borderWidth: 2,
    }}]
  }};

  const options = {{
    responsive: true,
    plugins: {{
      legend: {{ position: 'top' }},
      title: {{ display: true, text: '{title}' }}
    }}
  }};

  const ChartComponent = {{'line': Line, 'bar': Bar, 'pie': Pie, 'scatter': Scatter}}['{chart_type}'];
  
  return (
    <div className="bg-white dark:bg-slate-800 rounded-lg shadow-lg p-6">
      <ChartComponent data={{chartData}} options={{options}} />
    </div>
  );
}}
'''
    
    def _generate_comparison_component(self, comparison_type: str, data: Dict, categories: List[str]) -> str:
        """Generate React component code for comparison visualization"""
        return f'''
import {{ Bar }} from 'react-chartjs-2';
import {{ Chart as ChartJS, registerables }} from 'chart.js';

ChartJS.register(...registerables);

export default function GeneratedComparison() {{
  const data = {json.dumps(data)};
  const categories = {json.dumps(categories)};
  
  const chartData = {{
    labels: data.countries || [],
    datasets: categories.map((cat, idx) => ({{
      label: cat,
      data: data.values?.[idx] || [],
      backgroundColor: `hsla(${{idx * 60}}, 70%, 50%, 0.5)`,
    }}))
  }};

  const options = {{
    responsive: true,
    plugins: {{
      legend: {{ position: 'top' }},
      title: {{ display: true, text: 'Energy Comparison' }}
    }},
    scales: {{
      x: {{ stacked: {comparison_type == 'stacked'} }},
      y: {{ stacked: {comparison_type == 'stacked'} }}
    }}
  }};

  return (
    <div className="bg-white dark:bg-slate-800 rounded-lg shadow-lg p-6">
      <Bar data={{chartData}} options={{options}} />
    </div>
  );
}}
'''
    
    def _generate_dashboard_component(self, visualizations: List[Dict], layout: str) -> str:
        """Generate React component code for a dashboard"""
        grid_class = {
            "grid": "grid grid-cols-2 gap-4",
            "vertical": "flex flex-col space-y-4",
            "horizontal": "flex flex-row space-x-4"
        }.get(layout, "grid grid-cols-2 gap-4")
        
        return f'''
export default function GeneratedDashboard() {{
  return (
    <div className="{grid_class}">
      {{/* Dashboard with {len(visualizations)} visualizations */}}
      {{% for (let i = 0; i < {len(visualizations)}; i++) {{
        <div key={{i}} className="dashboard-item">
          {{/* Visualization component will be rendered here */}}
        </div>
      }} %}}
    </div>
  );
}}
'''