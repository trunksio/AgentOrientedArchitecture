"""Visualization Agent - Creates intelligent charts and visual representations"""
import sys
sys.path.append("/app/shared")
from typing import Dict, Any, List, Optional
from unified_base_agent import UnifiedBaseAgent
from mcp.schemas import MCPTool, ToolParameter, ParameterType
from llm import LLMConfig
from models import A2AMessage, MessageType
import json
import logging

logger = logging.getLogger(__name__)

class VisualizationAgent(UnifiedBaseAgent):
    AGENT_TYPE = "visualization"
    
    def __init__(self, llm_config=None):
        super().__init__(
            agent_id="viz-agent-001",
            name="Visualization Agent",
            description="Creates intelligent charts, graphs, and visual representations using AI-driven selection",
            llm_config=llm_config
        )
    

    def _get_capabilities(self) -> List[str]:
        """Get agent capabilities"""
        return [tool.description for tool in self.get_tools()]
    
    def _get_tags(self) -> List[str]:
        """Get agent tags"""
        # Override in subclass to provide specific tags
        return []

    def _register_tools(self):
        """Register MCP tools for visualization"""
        # Intelligent visualization tool
        self.register_tool(
            MCPTool(
                name="create_visualization",
                description="Intelligently analyze data and create the most appropriate visualization",
                parameters=[
                    ToolParameter(
                        name="data",
                        type=ParameterType.OBJECT,
                        description="Data to visualize",
                        required=True
                    ),
                    ToolParameter(
                        name="intent",
                        type=ParameterType.STRING,
                        description="What the user wants to see or understand",
                        required=True
                    ),
                    ToolParameter(
                        name="preferences",
                        type=ParameterType.OBJECT,
                        description="User preferences for visualization",
                        required=False
                    )
                ],
                returns={
                    "type": "object",
                    "description": "Visualization with explanation of why it was chosen"
                },
                examples=[
                    {
                        "parameters": {
                            "data": {"countries": ["USA", "China"], "values": [100, 200]},
                            "intent": "compare renewable capacity between countries"
                        },
                        "description": "AI selects best visualization for comparison"
                    }
                ]
            ),
            self._execute_create_visualization
        )
        
        # Create chart tool (specific chart type)
        self.register_tool(
            MCPTool(
                name="create_chart",
                description="Generate a specific type of chart with intelligent configuration",
                parameters=[
                    ToolParameter(
                        name="chart_type",
                        type=ParameterType.STRING,
                        description="Type of chart to create",
                        required=True,
                        enum=["line", "bar", "pie", "scatter", "area", "heatmap", "radar"]
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
                        name="options",
                        type=ParameterType.OBJECT,
                        description="Chart-specific options",
                        required=False
                    )
                ],
                returns={
                    "type": "object",
                    "description": "Chart configuration with rendering code"
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
        
        # Create comparison visualization
        self.register_tool(
            MCPTool(
                name="create_comparison",
                description="Create intelligent comparison visualizations",
                parameters=[
                    ToolParameter(
                        name="data",
                        type=ParameterType.OBJECT,
                        description="Data sets to compare",
                        required=True
                    ),
                    ToolParameter(
                        name="comparison_type",
                        type=ParameterType.STRING,
                        description="What aspect to compare",
                        required=True
                    ),
                    ToolParameter(
                        name="entities",
                        type=ParameterType.ARRAY,
                        description="Entities being compared",
                        required=True
                    )
                ],
                returns={
                    "type": "object",
                    "description": "Comparison visualization with insights"
                },
                examples=[
                    {
                        "parameters": {
                            "comparison_type": "technology mix",
                            "entities": ["USA", "China", "Germany"],
                            "data": {"solar": [100, 300, 80], "wind": [200, 150, 120]}
                        },
                        "description": "Compare energy mix across countries"
                    }
                ]
            ),
            self._execute_create_comparison
        )
        
        # Create dashboard tool
        self.register_tool(
            MCPTool(
                name="create_dashboard",
                description="Create an intelligent dashboard with multiple coordinated visualizations",
                parameters=[
                    ToolParameter(
                        name="data_sources",
                        type=ParameterType.ARRAY,
                        description="Multiple data sources for the dashboard",
                        required=True
                    ),
                    ToolParameter(
                        name="focus",
                        type=ParameterType.STRING,
                        description="Main focus or story of the dashboard",
                        required=True
                    ),
                    ToolParameter(
                        name="layout_preference",
                        type=ParameterType.STRING,
                        description="Preferred layout style",
                        required=False,
                        enum=["auto", "grid", "flow", "highlight"],
                        default="auto"
                    )
                ],
                returns={
                    "type": "object",
                    "description": "Dashboard configuration with multiple visualizations"
                },
                examples=[
                    {
                        "parameters": {
                            "data_sources": [{"type": "trends"}, {"type": "comparison"}],
                            "focus": "renewable energy progress",
                            "layout_preference": "highlight"
                        },
                        "description": "Create a comprehensive dashboard"
                    }
                ]
            ),
            self._execute_create_dashboard
        )
        
        # Explain visualization choice tool
        self.register_tool(
            MCPTool(
                name="explain_visualization",
                description="Explain why a particular visualization was chosen",
                parameters=[
                    ToolParameter(
                        name="visualization_type",
                        type=ParameterType.STRING,
                        description="Type of visualization to explain",
                        required=True
                    ),
                    ToolParameter(
                        name="data_characteristics",
                        type=ParameterType.OBJECT,
                        description="Characteristics of the data",
                        required=True
                    ),
                    ToolParameter(
                        name="user_goal",
                        type=ParameterType.STRING,
                        description="What the user wants to achieve",
                        required=True
                    )
                ],
                returns={
                    "type": "object",
                    "description": "Explanation of visualization choice"
                },
                examples=[
                    {
                        "parameters": {
                            "visualization_type": "heatmap",
                            "data_characteristics": {"dimensions": 2, "values": "continuous"},
                            "user_goal": "see patterns across countries and years"
                        },
                        "description": "Explain why a heatmap was chosen"
                    }
                ]
            ),
            self._execute_explain_visualization
        )
    
    async def handle_a2a_message(self, message: A2AMessage) -> Any:
        """Enhanced message handling with intelligent visualization selection"""
        logger.info(f"Viz Agent received message: {message.action}")
        
        # For visualization requests, always use intelligent selection
        if message.action in ["visualize", "show", "display", "plot"]:
            return await self._handle_intelligent_visualization(message)
        
        # Otherwise use base class handling
        return await super().handle_a2a_message(message)
    
    async def _handle_intelligent_visualization(self, message: A2AMessage) -> Dict[str, Any]:
        """Handle visualization requests with AI-driven selection"""
        data = message.payload.get("data", {})
        intent = message.payload.get("intent", message.payload.get("query", "visualize data"))
        
        # Use the intelligent visualization tool
        result = await self.execute_tool("create_visualization", {
            "data": data,
            "intent": intent,
            "preferences": message.payload.get("preferences", {})
        })
        
        if result.success:
            return result.result
        else:
            return {"error": result.error}
    
    async def _execute_create_visualization(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Intelligently analyze data and create the most appropriate visualization"""
        data = parameters["data"]
        intent = parameters["intent"]
        preferences = parameters.get("preferences", {})
        
        if not self.llm.is_available():
            # Fallback to simple heuristics
            return await self._fallback_visualization_selection(data, intent)
        
        # Analyze data characteristics
        data_analysis = await self._analyze_data_structure(data)
        
        # Use LLM to select best visualization
        prompt = f"""Analyze this data and user intent to select the best visualization:

User Intent: "{intent}"

Data Analysis:
{json.dumps(data_analysis, indent=2)}

User Preferences: {json.dumps(preferences, indent=2)}

Consider:
1. Data dimensions and types
2. User's goal (comparison, trend, distribution, correlation, composition)
3. Number of data points
4. Best practices for data visualization

Respond with JSON:
{{
    "visualization_type": "specific type (line, bar, scatter, heatmap, etc.)",
    "reasoning": "why this visualization is best",
    "configuration": {{
        "title": "suggested title",
        "key_features": ["list of important features to highlight"],
        "color_scheme": "suggested color approach",
        "interactive_elements": ["suggested interactions"]
    }},
    "alternatives": ["other viable options with brief explanation"]
}}"""

        system_prompt = """You are an expert data visualization specialist who understands:
- Edward Tufte's principles of data visualization
- Best practices for different data types
- How to match visualizations to user goals
- Accessibility and clarity in design"""

        try:
            viz_selection = await self.llm.generate_json(prompt, system_prompt)
            
            if viz_selection:
                # Create the selected visualization
                viz_result = await self._create_intelligent_chart(
                    viz_type=viz_selection["visualization_type"],
                    data=data,
                    config=viz_selection["configuration"],
                    data_analysis=data_analysis
                )
                
                return {
                    "type": "intelligent_visualization",
                    "visualization": viz_result,
                    "selection_reasoning": viz_selection["reasoning"],
                    "alternatives_considered": viz_selection.get("alternatives", []),
                    "data_insights": data_analysis["insights"]
                }
            
        except Exception as e:
            logger.error(f"Error in intelligent visualization: {e}")
        
        # Fallback if LLM fails
        return await self._fallback_visualization_selection(data, intent)
    
    async def _analyze_data_structure(self, data: Any) -> Dict[str, Any]:
        """Analyze the structure and characteristics of the data"""
        analysis = {
            "data_type": "unknown",
            "dimensions": 0,
            "size": 0,
            "characteristics": [],
            "insights": []
        }
        
        if isinstance(data, dict):
            analysis["data_type"] = "dictionary"
            analysis["dimensions"] = len(data)
            
            # Check for common data patterns
            if "data" in data and isinstance(data["data"], list):
                # Tabular data from Data Agent
                analysis["data_type"] = "tabular"
                analysis["size"] = len(data["data"])
                if data["data"]:
                    analysis["columns"] = list(data["data"][0].keys())
                    analysis["characteristics"].append("structured_table")
                    
                    # Analyze numerical columns
                    for col in analysis["columns"]:
                        if any(isinstance(row.get(col), (int, float)) for row in data["data"]):
                            analysis["characteristics"].append(f"numerical:{col}")
            
            elif all(isinstance(v, list) for v in data.values()):
                # Multiple arrays (time series, categories)
                analysis["data_type"] = "multi_array"
                analysis["characteristics"].append("parallel_arrays")
                
            elif all(isinstance(v, (int, float)) for v in data.values()):
                # Single data points
                analysis["data_type"] = "single_values"
                analysis["characteristics"].append("key_value_pairs")
        
        elif isinstance(data, list):
            analysis["data_type"] = "array"
            analysis["size"] = len(data)
            if data and isinstance(data[0], dict):
                analysis["characteristics"].append("array_of_objects")
        
        # Generate insights
        if "time" in str(data).lower() or "year" in str(data).lower():
            analysis["insights"].append("temporal_data_detected")
        
        if analysis["dimensions"] > 5:
            analysis["insights"].append("high_dimensional_data")
        
        if analysis["size"] > 100:
            analysis["insights"].append("large_dataset")
        
        return analysis
    
    async def _create_intelligent_chart(self, viz_type: str, data: Any, config: Dict[str, Any], data_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Create a chart with intelligent configuration"""
        # Map visualization types to chart types
        viz_mapping = {
            "comparison": "bar",
            "trend": "line",
            "distribution": "scatter",
            "composition": "pie",
            "correlation": "scatter",
            "heatmap": "heatmap",
            "multi-dimensional": "radar"
        }
        
        chart_type = viz_mapping.get(viz_type, viz_type)
        
        # Process data for the selected chart type
        processed_data = await self._process_data_for_chart(chart_type, data, data_analysis)
        
        # Generate the chart component
        component_code = self._generate_intelligent_chart_component(
            chart_type=chart_type,
            data=processed_data,
            config=config,
            insights=data_analysis.get("insights", [])
        )
        
        return {
            "chart_type": chart_type,
            "component_code": component_code,
            "config": config,
            "processed_data": processed_data
        }
    
    async def _process_data_for_chart(self, chart_type: str, data: Any, data_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Process data into the format needed for the chart type"""
        if data_analysis["data_type"] == "tabular" and "data" in data:
            # Extract data from tabular format
            df_data = data["data"]
            
            if chart_type == "line":
                # Find time column and value columns
                time_col = next((col for col in data_analysis.get("columns", []) if "year" in col.lower()), None)
                value_cols = [col for col in data_analysis.get("columns", []) if "capacity" in col.lower() or "mw" in col.lower()]
                
                if time_col and value_cols:
                    return {
                        "labels": [row[time_col] for row in df_data],
                        "datasets": [
                            {
                                "label": col,
                                "data": [row.get(col, 0) for row in df_data]
                            } for col in value_cols[:3]  # Limit to 3 series
                        ]
                    }
            
            elif chart_type == "bar":
                # Use first string column as labels, first numeric as values
                label_col = next((col for col in data_analysis.get("columns", []) if isinstance(df_data[0].get(col), str)), None)
                value_col = next((col for col in data_analysis.get("columns", []) if isinstance(df_data[0].get(col), (int, float))), None)
                
                if label_col and value_col:
                    return {
                        "labels": [row[label_col] for row in df_data[:10]],  # Limit to 10
                        "data": [row[value_col] for row in df_data[:10]]
                    }
        
        # Return original data if no processing needed
        return data
    
    async def _execute_create_chart(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Create a specific chart type with intelligent enhancements"""
        chart_type = parameters["chart_type"]
        data = parameters["data"]
        title = parameters.get("title", "")
        options = parameters.get("options", {})
        
        # Use LLM to enhance chart configuration
        enhanced_config = await self._enhance_chart_config(chart_type, data, title)
        
        # Merge with provided options
        final_config = {**enhanced_config, **options}
        
        # Generate React component code
        component_code = self._generate_chart_component(
            chart_type=chart_type,
            data=data,
            title=title or final_config.get("title", ""),
            config=final_config
        )
        
        return {
            "type": "chart",
            "chart_type": chart_type,
            "component_code": component_code,
            "config": final_config,
            "enhancement_applied": bool(enhanced_config)
        }
    
    async def _enhance_chart_config(self, chart_type: str, data: Dict, title: str) -> Dict[str, Any]:
        """Use LLM to enhance chart configuration"""
        if not self.llm.is_available():
            return {}
        
        prompt = f"""Enhance this {chart_type} chart configuration:

Data structure: {json.dumps(list(data.keys()) if isinstance(data, dict) else "array", indent=2)}
Title: "{title}"

Suggest optimal:
1. Axis labels
2. Color scheme (considering accessibility)
3. Legend placement
4. Grid and scale options
5. Any chart-specific enhancements

Respond with JSON configuration object."""

        try:
            config = await self.llm.generate_json(prompt)
            return config if config else {}
        except:
            return {}
    
    async def _execute_create_comparison(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Create intelligent comparison visualizations"""
        data = parameters["data"]
        comparison_type = parameters["comparison_type"]
        entities = parameters["entities"]
        
        # Determine best comparison visualization
        if self.llm.is_available():
            viz_type = await self._select_comparison_viz(data, comparison_type, entities)
        else:
            viz_type = "grouped_bar"  # Default
        
        # Generate comparison component
        component_code = self._generate_comparison_component(
            viz_type=viz_type,
            data=data,
            entities=entities,
            comparison_type=comparison_type
        )
        
        return {
            "type": "comparison",
            "visualization_type": viz_type,
            "component_code": component_code,
            "comparison_type": comparison_type,
            "entities_compared": entities,
            "insights": await self._generate_comparison_insights(data, entities, comparison_type)
        }
    
    async def _select_comparison_viz(self, data: Dict, comparison_type: str, entities: List[str]) -> str:
        """Select best visualization for comparison"""
        prompt = f"""Select the best visualization for this comparison:

Comparison Type: {comparison_type}
Number of Entities: {len(entities)}
Data Dimensions: {len(data) if isinstance(data, dict) else 1}

Options: grouped_bar, stacked_bar, radar, parallel_coordinates, small_multiples

Return just the visualization type name."""

        try:
            viz_type = await self.llm.generate(prompt)
            return viz_type.strip().lower().replace(" ", "_")
        except:
            return "grouped_bar"
    
    async def _generate_comparison_insights(self, data: Dict, entities: List[str], comparison_type: str) -> List[str]:
        """Generate insights about the comparison"""
        if not self.llm.is_available():
            return ["Comparison visualization created"]
        
        prompt = f"""Generate 2-3 insights from this {comparison_type} comparison:

Entities: {entities}
Data: {json.dumps(data, indent=2)}

Focus on: differences, patterns, outliers, implications

Format as JSON array of insight strings."""

        try:
            insights = await self.llm.generate_json(prompt)
            return insights if isinstance(insights, list) else []
        except:
            return []
    
    async def _execute_create_dashboard(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Create an intelligent dashboard with multiple visualizations"""
        data_sources = parameters["data_sources"]
        focus = parameters["focus"]
        layout_pref = parameters.get("layout_preference", "auto")
        
        # Plan dashboard layout
        dashboard_plan = await self._plan_dashboard(data_sources, focus, layout_pref)
        
        # Generate dashboard component
        component_code = self._generate_dashboard_component(
            plan=dashboard_plan,
            focus=focus
        )
        
        return {
            "type": "dashboard",
            "focus": focus,
            "layout": dashboard_plan["layout"],
            "visualizations": dashboard_plan["visualizations"],
            "component_code": component_code,
            "narrative": dashboard_plan.get("narrative", "")
        }
    
    async def _plan_dashboard(self, data_sources: List[Dict], focus: str, layout_pref: str) -> Dict[str, Any]:
        """Plan the dashboard layout and visualizations"""
        if not self.llm.is_available():
            return {
                "layout": "grid",
                "visualizations": [{"type": "chart", "position": i} for i, _ in enumerate(data_sources)],
                "narrative": f"Dashboard focused on {focus}"
            }
        
        prompt = f"""Plan a dashboard layout for:

Focus: "{focus}"
Data Sources: {json.dumps(data_sources, indent=2)}
Layout Preference: {layout_pref}

Create a plan with:
1. Overall layout strategy
2. Visualization types and positions
3. Visual hierarchy (what to emphasize)
4. Connecting narrative

Respond with JSON:
{{
    "layout": "layout type",
    "visualizations": [
        {{"type": "viz type", "position": "position", "purpose": "what it shows", "size": "relative size"}}
    ],
    "visual_hierarchy": ["ordered list of importance"],
    "narrative": "connecting story"
}}"""

        try:
            plan = await self.llm.generate_json(prompt)
            return plan if plan else self._plan_dashboard({}, focus, layout_pref)
        except Exception as e:
            logger.error(f"Dashboard planning error: {e}")
            return self._plan_dashboard({}, focus, layout_pref)
    
    async def _execute_explain_visualization(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Explain why a visualization was chosen"""
        viz_type = parameters["visualization_type"]
        data_chars = parameters["data_characteristics"]
        user_goal = parameters["user_goal"]
        
        if not self.llm.is_available():
            return {
                "explanation": f"{viz_type} was selected for {user_goal}",
                "principles": ["Shows data clearly", "Matches user intent"]
            }
        
        prompt = f"""Explain why {viz_type} is the best choice for:

User Goal: "{user_goal}"
Data Characteristics: {json.dumps(data_chars, indent=2)}

Include:
1. Why this visualization matches the goal
2. What principles support this choice
3. What alternatives were considered
4. Any limitations to be aware of

Be concise but educational."""

        explanation = await self.llm.generate(prompt)
        
        return {
            "visualization_type": viz_type,
            "explanation": explanation,
            "user_goal": user_goal,
            "data_characteristics": data_chars
        }
    
    async def _fallback_visualization_selection(self, data: Any, intent: str) -> Dict[str, Any]:
        """Fallback visualization selection without LLM"""
        intent_lower = intent.lower()
        
        # Simple keyword-based selection
        if "compar" in intent_lower:
            viz_type = "bar"
        elif "trend" in intent_lower or "time" in intent_lower:
            viz_type = "line"
        elif "distribut" in intent_lower:
            viz_type = "scatter"
        elif "composition" in intent_lower or "breakdown" in intent_lower:
            viz_type = "pie"
        else:
            viz_type = "bar"  # Default
        
        return {
            "type": "visualization",
            "chart_type": viz_type,
            "component_code": self._generate_chart_component(viz_type, data, intent),
            "selection_method": "keyword_matching",
            "reasoning": f"Selected {viz_type} chart based on intent keywords"
        }
    
    def _generate_intelligent_chart_component(self, chart_type: str, data: Dict, config: Dict, insights: List[str]) -> str:
        """Generate React component with intelligent features"""
        return f'''
import {{ Line, Bar, Pie, Scatter, Radar }} from 'react-chartjs-2';
import {{ Chart as ChartJS, registerables }} from 'chart.js';
import {{ motion }} from 'framer-motion';

ChartJS.register(...registerables);

export default function IntelligentChart() {{
  const chartData = {json.dumps(data, indent=2)};
  const config = {json.dumps(config, indent=2)};
  const insights = {json.dumps(insights, indent=2)};
  
  const options = {{
    responsive: true,
    plugins: {{
      legend: {{ 
        position: config.legendPosition || 'top',
        display: config.showLegend !== false 
      }},
      title: {{ 
        display: true, 
        text: '{config.get("title", "")}',
        font: {{ size: 16, weight: 'bold' }}
      }},
      tooltip: {{
        callbacks: {{
          afterLabel: (context) => {{
            // Add insights to tooltips
            return insights.length > 0 ? `Insight: ${{insights[0]}}` : '';
          }}
        }}
      }}
    }},
    ...config.chartOptions
  }};

  const ChartComponent = {{'line': Line, 'bar': Bar, 'pie': Pie, 'scatter': Scatter, 'radar': Radar}}['{chart_type}'] || Bar;
  
  return (
    <motion.div 
      className="bg-white dark:bg-slate-800 rounded-lg shadow-lg p-6"
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.5 }}
    >
      <ChartComponent data={{chartData}} options={{options}} />
      
      {{insights.length > 0 && (
        <motion.div 
          className="mt-4 p-3 bg-blue-50 dark:bg-blue-900/20 rounded"
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
        >
          <p className="text-sm text-blue-800 dark:text-blue-200">
            <strong>Visualization Insight:</strong> {{insights[0]}}
          </p>
        </motion.div>
      )}}
    </motion.div>
  );
}}
'''
    
    def _generate_chart_component(self, chart_type: str, data: Dict, title: str, config: Dict = None) -> str:
        """Generate standard chart component"""
        config = config or {}
        return f'''
import {{ Line, Bar, Pie, Scatter }} from 'react-chartjs-2';
import {{ Chart as ChartJS, registerables }} from 'chart.js';

ChartJS.register(...registerables);

export default function GeneratedChart() {{
  const chartData = {json.dumps(data, indent=2)};
  
  const options = {{
    responsive: true,
    plugins: {{
      legend: {{ position: '{config.get("legendPosition", "top")}' }},
      title: {{ display: true, text: '{title}' }}
    }},
    scales: {json.dumps(config.get("scales", {}))}
  }};

  const ChartComponent = {{'line': Line, 'bar': Bar, 'pie': Pie, 'scatter': Scatter}}['{chart_type}'];
  
  return (
    <div className="bg-white dark:bg-slate-800 rounded-lg shadow-lg p-6">
      <ChartComponent data={{chartData}} options={{options}} />
    </div>
  );
}}
'''
    
    def _generate_comparison_component(self, viz_type: str, data: Dict, entities: List[str], comparison_type: str) -> str:
        """Generate comparison visualization component"""
        return f'''
import {{ Bar, Radar }} from 'react-chartjs-2';
import {{ Chart as ChartJS, registerables }} from 'chart.js';

ChartJS.register(...registerables);

export default function ComparisonVisualization() {{
  const data = {json.dumps(data, indent=2)};
  const entities = {json.dumps(entities, indent=2)};
  const comparisonType = "{comparison_type}";
  
  // Transform data for visualization
  const chartData = {{
    labels: entities,
    datasets: Object.keys(data).map((key, idx) => ({{
      label: key,
      data: Array.isArray(data[key]) ? data[key] : entities.map(e => data[key][e] || 0),
      backgroundColor: `hsla(${{idx * 60}}, 70%, 50%, 0.5)`,
      borderColor: `hsl(${{idx * 60}}, 70%, 50%)`,
    }}))
  }};

  const options = {{
    responsive: true,
    plugins: {{
      title: {{ 
        display: true, 
        text: `${{comparisonType}} Comparison: ${{entities.join(' vs ')}}` 
      }}
    }},
    scales: {{
      r: {{ beginAtZero: true }} // For radar charts
    }}
  }};

  const ChartComponent = '{viz_type}' === 'radar' ? Radar : Bar;

  return (
    <div className="bg-white dark:bg-slate-800 rounded-lg shadow-lg p-6">
      <ChartComponent data={{chartData}} options={{options}} />
      <div className="mt-4 text-sm text-gray-600 dark:text-gray-400">
        <p>Comparing {{comparisonType}} across {{entities.length}} entities</p>
      </div>
    </div>
  );
}}
'''
    
    def _generate_dashboard_component(self, plan: Dict[str, Any], focus: str) -> str:
        """Generate dashboard component with multiple visualizations"""
        layout_classes = {
            "grid": "grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6",
            "flow": "flex flex-col space-y-6",
            "highlight": "grid grid-cols-12 gap-6"
        }
        
        return f'''
import React from 'react';
import {{ motion }} from 'framer-motion';

export default function IntelligentDashboard() {{
  const plan = {json.dumps(plan, indent=2)};
  const focus = "{focus}";
  
  return (
    <div className="space-y-6">
      <motion.div 
        className="text-center"
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
          {{focus}}
        </h1>
        {{plan.narrative && (
          <p className="mt-2 text-gray-600 dark:text-gray-400">
            {{plan.narrative}}
          </p>
        )}}
      </motion.div>
      
      <div className="{layout_classes.get(plan.get('layout', 'grid'), layout_classes['grid'])}">
        {{plan.visualizations && plan.visualizations.map((viz, index) => (
          <motion.div
            key={{index}}
            className={{viz.size === 'large' ? 'col-span-full' : viz.size === 'medium' ? 'col-span-6' : 'col-span-4'}}
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: index * 0.15 }}
          >
            <div className="h-full bg-white dark:bg-slate-800 rounded-lg shadow-lg p-6">
              <h3 className="text-lg font-semibold mb-4">{{viz.purpose}}</h3>
              {{/* Visualization component will be rendered here */}}
              <div className="visualization-placeholder">
                {{viz.type}} visualization
              </div>
            </div>
          </motion.div>
        ))}}
      </div>
    </div>
  );
}}
'''