"""Data Agent - Provides intelligent access to renewable energy datasets"""
import pandas as pd
import os
from typing import Dict, Any, List, Optional
import sys
import json
import logging
sys.path.append('/app/shared')
from base_agent import BaseAgent
from mcp.schemas import MCPTool, ToolParameter, ParameterType
from llm import LLMConfig
from models import A2AMessage, MessageType

logger = logging.getLogger(__name__)

class DataAgent(BaseAgent):
    AGENT_TYPE = "data"
    
    def __init__(self, llm_config=None):
        super().__init__(
            agent_id="data-agent-001",
            name="Data Agent",
            description="Provides intelligent access to renewable energy datasets with semantic understanding",
            llm_config=llm_config
        )
        self.data_path = os.path.join(os.path.dirname(__file__), "data", "renewable_energy.csv")
        self._load_data()
    
    def _load_data(self):
        """Load the renewable energy dataset"""
        try:
            self.df = pd.read_csv(self.data_path)
            logger.info(f"Loaded data with shape: {self.df.shape}")
            logger.info(f"Columns: {list(self.df.columns)}")
        except Exception as e:
            logger.error(f"Error loading data: {e}")
            self.df = pd.DataFrame()
    
    def _register_tools(self):
        """Register MCP tools for data operations"""
        # Query data tool
        self.register_tool(
            MCPTool(
                name="query_data",
                description="Query renewable energy data by country, year, or energy type with intelligent filtering",
                parameters=[
                    ToolParameter(
                        name="country",
                        type=ParameterType.STRING,
                        description="Country name to filter by",
                        required=False
                    ),
                    ToolParameter(
                        name="year",
                        type=ParameterType.NUMBER,
                        description="Year to filter by",
                        required=False
                    ),
                    ToolParameter(
                        name="energy_type",
                        type=ParameterType.STRING,
                        description="Energy type (solar, wind, hydro)",
                        required=False,
                        enum=["solar", "wind", "hydro", "all"]
                    ),
                    ToolParameter(
                        name="countries",
                        type=ParameterType.ARRAY,
                        description="List of countries to filter by",
                        required=False
                    ),
                    ToolParameter(
                        name="year_range",
                        type=ParameterType.OBJECT,
                        description="Year range with 'start' and 'end' keys",
                        required=False
                    )
                ],
                returns={
                    "type": "object",
                    "description": "Filtered data with columns and rows, plus query explanation"
                },
                examples=[
                    {
                        "parameters": {"country": "Germany", "year": 2023},
                        "description": "Get Germany's renewable energy data for 2023"
                    }
                ]
            ),
            self._execute_query_data
        )
        
        # Aggregate data tool
        self.register_tool(
            MCPTool(
                name="aggregate_data",
                description="Intelligently aggregate and summarize energy data with calculations",
                parameters=[
                    ToolParameter(
                        name="metric",
                        type=ParameterType.STRING,
                        description="Metric to calculate (sum, average, max, min)",
                        required=True,
                        enum=["sum", "average", "max", "min"]
                    ),
                    ToolParameter(
                        name="group_by",
                        type=ParameterType.STRING,
                        description="Column to group by",
                        required=False,
                        enum=["country", "year", "none"]
                    ),
                    ToolParameter(
                        name="column",
                        type=ParameterType.STRING,
                        description="Column to aggregate",
                        required=True,
                        enum=["solar_capacity_mw", "wind_capacity_mw", "hydro_capacity_mw", "total_renewable_mw", "growth_rate"]
                    ),
                    ToolParameter(
                        name="filters",
                        type=ParameterType.OBJECT,
                        description="Additional filters to apply before aggregation",
                        required=False
                    )
                ],
                returns={
                    "type": "object",
                    "description": "Aggregated data results with explanation"
                },
                examples=[
                    {
                        "parameters": {"metric": "sum", "group_by": "country", "column": "total_renewable_mw"},
                        "description": "Total renewable capacity by country"
                    }
                ]
            ),
            self._execute_aggregate_data
        )
        
        # Get trends tool
        self.register_tool(
            MCPTool(
                name="get_trends",
                description="Analyze trends in renewable energy data with pattern detection",
                parameters=[
                    ToolParameter(
                        name="country",
                        type=ParameterType.STRING,
                        description="Country to analyze",
                        required=False
                    ),
                    ToolParameter(
                        name="countries",
                        type=ParameterType.ARRAY,
                        description="Multiple countries to compare trends",
                        required=False
                    ),
                    ToolParameter(
                        name="metric",
                        type=ParameterType.STRING,
                        description="Metric to analyze",
                        required=True,
                        enum=["solar_capacity_mw", "wind_capacity_mw", "hydro_capacity_mw", "total_renewable_mw", "growth_rate"]
                    ),
                    ToolParameter(
                        name="analysis_type",
                        type=ParameterType.STRING,
                        description="Type of trend analysis",
                        required=False,
                        enum=["growth", "comparison", "forecast", "anomaly"],
                        default="growth"
                    )
                ],
                returns={
                    "type": "object",
                    "description": "Trend analysis with yearly data and insights"
                },
                examples=[
                    {
                        "parameters": {"country": "China", "metric": "solar_capacity_mw"},
                        "description": "Analyze China's solar capacity trends"
                    }
                ]
            ),
            self._execute_get_trends
        )
        
        # Intelligent data discovery tool
        self.register_tool(
            MCPTool(
                name="discover_insights",
                description="Use AI to discover interesting patterns and insights in the data",
                parameters=[
                    ToolParameter(
                        name="focus_area",
                        type=ParameterType.STRING,
                        description="Area to focus the analysis on",
                        required=True
                    ),
                    ToolParameter(
                        name="depth",
                        type=ParameterType.STRING,
                        description="Analysis depth",
                        required=False,
                        enum=["quick", "standard", "comprehensive"],
                        default="standard"
                    )
                ],
                returns={
                    "type": "object",
                    "description": "Discovered insights with supporting data"
                },
                examples=[
                    {
                        "parameters": {"focus_area": "rapid growth regions", "depth": "comprehensive"},
                        "description": "Discover regions with rapid renewable growth"
                    }
                ]
            ),
            self._execute_discover_insights
        )
    
    async def handle_a2a_message(self, message: A2AMessage) -> Any:
        """Enhanced message handling with semantic understanding"""
        logger.info(f"Data Agent received message: {message.action}")
        
        # For exploratory or complex queries, use LLM to understand and plan
        if message.action in ["explore", "analyze", "understand", "compare"] or \
           "why" in message.action.lower() or "how" in message.action.lower():
            return await self._handle_complex_query(message)
        
        # Otherwise use base class handling
        return await super().handle_a2a_message(message)
    
    async def _handle_complex_query(self, message: A2AMessage) -> Dict[str, Any]:
        """Handle complex queries using LLM for intelligent data selection"""
        query = message.payload.get("query", message.action)
        
        if not self.llm.is_available():
            # Fallback to standard handling
            return await super().handle_a2a_message(message)
        
        # Analyze query intent
        prompt = f"""Analyze this renewable energy data query: "{query}"

Available data columns: {list(self.df.columns)}
Available countries: {sorted(self.df['country'].unique().tolist())}
Year range: {self.df['year'].min()} - {self.df['year'].max()}

Determine:
1. What data is needed to answer this query
2. Which tools to use and in what order
3. What insights would be most valuable

Respond with a JSON plan:
{{
    "intent": "brief description of what user wants",
    "data_needed": ["list of specific data points"],
    "tool_sequence": [
        {{"tool": "tool_name", "parameters": {{}}, "purpose": "why this tool"}}
    ],
    "key_insights_to_find": ["list of insights to look for"]
}}"""

        system_prompt = """You are an intelligent data agent specializing in renewable energy analysis. 
You understand complex queries and know how to extract the most relevant data and insights."""

        try:
            plan = await self.llm.generate_json(prompt, system_prompt)
            
            if plan and plan.get("tool_sequence"):
                results = {
                    "query": query,
                    "analysis_plan": plan,
                    "results": [],
                    "insights": []
                }
                
                # Execute the planned sequence
                for step in plan["tool_sequence"]:
                    tool_name = step["tool"]
                    parameters = step["parameters"]
                    
                    logger.info(f"Executing planned step: {tool_name} for {step['purpose']}")
                    
                    if tool_name in self.tools:
                        tool_result = await self.execute_tool(tool_name, parameters)
                        if tool_result.success:
                            results["results"].append({
                                "tool": tool_name,
                                "purpose": step["purpose"],
                                "data": tool_result.result
                            })
                
                # Generate insights based on results
                if results["results"]:
                    insights = await self._generate_insights(query, results["results"], plan.get("key_insights_to_find", []))
                    results["insights"] = insights
                
                return results
            
        except Exception as e:
            logger.error(f"Error in complex query handling: {e}")
        
        # Fallback to standard handling
        return await super().handle_a2a_message(message)
    
    async def _generate_insights(self, query: str, results: List[Dict], focus_areas: List[str]) -> List[str]:
        """Generate insights from the data results"""
        if not self.llm.is_available():
            return ["Data analysis completed"]
        
        prompt = f"""Based on this renewable energy data analysis for query: "{query}"

Results: {json.dumps(results, indent=2)}

Focus areas: {focus_areas}

Generate 3-5 key insights that directly answer the query or provide valuable context.
Format as JSON array of strings."""

        try:
            insights = await self.llm.generate_json(prompt)
            if isinstance(insights, list):
                return insights
        except Exception as e:
            logger.error(f"Error generating insights: {e}")
        
        return ["Analysis complete - see data results above"]
    
    async def _execute_query_data(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute data query with intelligent filtering"""
        filtered_df = self.df.copy()
        query_explanation = []
        
        # Handle multiple countries
        if parameters.get("countries"):
            countries = parameters["countries"]
            filtered_df = filtered_df[filtered_df["country"].isin(countries)]
            query_explanation.append(f"Filtering for countries: {', '.join(countries)}")
        elif parameters.get("country"):
            filtered_df = filtered_df[filtered_df["country"] == parameters["country"]]
            query_explanation.append(f"Filtering for country: {parameters['country']}")
        
        # Handle year range
        if parameters.get("year_range"):
            year_range = parameters["year_range"]
            if "start" in year_range:
                filtered_df = filtered_df[filtered_df["year"] >= year_range["start"]]
            if "end" in year_range:
                filtered_df = filtered_df[filtered_df["year"] <= year_range["end"]]
            query_explanation.append(f"Year range: {year_range.get('start', 'any')} - {year_range.get('end', 'any')}")
        elif parameters.get("year"):
            filtered_df = filtered_df[filtered_df["year"] == parameters["year"]]
            query_explanation.append(f"Year: {parameters['year']}")
        
        # Handle energy type filtering
        if parameters.get("energy_type") and parameters["energy_type"] != "all":
            # Select relevant columns based on energy type
            base_cols = ["country", "year"]
            if parameters["energy_type"] == "solar":
                cols = base_cols + ["solar_capacity_mw"]
                query_explanation.append("Focusing on solar energy data")
            elif parameters["energy_type"] == "wind":
                cols = base_cols + ["wind_capacity_mw"]
                query_explanation.append("Focusing on wind energy data")
            elif parameters["energy_type"] == "hydro":
                cols = base_cols + ["hydro_capacity_mw"]
                query_explanation.append("Focusing on hydro energy data")
            filtered_df = filtered_df[cols]
        
        # Add data quality insights
        data_insights = []
        if len(filtered_df) > 0:
            data_insights.append(f"Found {len(filtered_df)} data points")
            if "total_renewable_mw" in filtered_df.columns:
                avg_capacity = filtered_df["total_renewable_mw"].mean()
                data_insights.append(f"Average renewable capacity: {avg_capacity:.1f} MW")
        
        return {
            "columns": list(filtered_df.columns),
            "data": filtered_df.to_dict("records"),
            "row_count": len(filtered_df),
            "query_explanation": query_explanation,
            "data_insights": data_insights
        }
    
    async def _execute_aggregate_data(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute intelligent data aggregation"""
        metric = parameters["metric"]
        group_by = parameters.get("group_by", "none")
        column = parameters["column"]
        filters = parameters.get("filters", {})
        
        # Apply any filters first
        working_df = self.df.copy()
        filter_explanation = []
        
        if filters:
            if "min_year" in filters:
                working_df = working_df[working_df["year"] >= filters["min_year"]]
                filter_explanation.append(f"Years from {filters['min_year']}")
            if "countries" in filters:
                working_df = working_df[working_df["country"].isin(filters["countries"])]
                filter_explanation.append(f"Countries: {', '.join(filters['countries'])}")
        
        if group_by == "none":
            # Simple aggregation
            if metric == "sum":
                result = working_df[column].sum()
            elif metric == "average":
                result = working_df[column].mean()
            elif metric == "max":
                result = working_df[column].max()
            elif metric == "min":
                result = working_df[column].min()
            
            # Add context
            context = await self._get_aggregation_context(metric, column, result, working_df)
            
            return {
                "metric": metric,
                "column": column,
                "value": float(result),
                "filter_applied": filter_explanation,
                "context": context,
                "data_points_used": len(working_df)
            }
        else:
            # Grouped aggregation
            grouped = working_df.groupby(group_by)[column]
            
            if metric == "sum":
                result = grouped.sum()
            elif metric == "average":
                result = grouped.mean()
            elif metric == "max":
                result = grouped.max()
            elif metric == "min":
                result = grouped.min()
            
            # Find interesting patterns
            result_df = result.reset_index()
            patterns = []
            if len(result_df) > 0:
                if metric in ["sum", "average"]:
                    top_3 = result_df.nlargest(3, column)[group_by].tolist()
                    patterns.append(f"Top 3 by {metric}: {', '.join(map(str, top_3))}")
            
            return {
                "metric": metric,
                "column": column,
                "group_by": group_by,
                "data": result_df.to_dict("records"),
                "filter_applied": filter_explanation,
                "patterns": patterns,
                "groups_found": len(result_df)
            }
    
    async def _get_aggregation_context(self, metric: str, column: str, value: float, df: pd.DataFrame) -> str:
        """Generate context for aggregation results"""
        if not self.llm.is_available():
            return f"{metric.capitalize()} of {column}: {value:.1f}"
        
        # Generate meaningful context
        context_data = {
            "metric": metric,
            "column": column,
            "value": value,
            "total_countries": df["country"].nunique(),
            "year_range": f"{df['year'].min()}-{df['year'].max()}"
        }
        
        prompt = f"""Generate a brief, insightful context statement for this renewable energy statistic:
{json.dumps(context_data)}

Make it meaningful and easy to understand for non-technical users."""
        
        try:
            context = await self.llm.generate(prompt)
            return context
        except:
            return f"{metric.capitalize()} of {column}: {value:.1f}"
    
    async def _execute_get_trends(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute intelligent trend analysis"""
        metric = parameters["metric"]
        analysis_type = parameters.get("analysis_type", "growth")
        
        # Validate metric exists in dataframe
        valid_metrics = ['solar_capacity_mw', 'wind_capacity_mw', 'hydro_capacity_mw', 'total_renewable_mw', 'growth_rate']
        if metric not in valid_metrics:
            # Default to total_renewable_mw if invalid metric provided
            metric = 'total_renewable_mw'
        
        # Handle single or multiple countries
        countries = parameters.get("countries", [])
        if parameters.get("country"):
            countries = [parameters["country"]]
        
        if not countries:
            # Analyze global trends
            countries = self.df["country"].unique().tolist()
            scope = "global"
        else:
            scope = "specific"
        
        trend_results = {
            "metric": metric,
            "analysis_type": analysis_type,
            "scope": scope,
            "countries_analyzed": countries[:10],  # Limit for display
            "trends": []
        }
        
        # Analyze trends for each country
        for country in countries[:10]:  # Limit to prevent overwhelming results
            country_data = self.df[self.df["country"] == country].sort_values("year")
            
            if len(country_data) > 1:
                # Calculate year-over-year change
                country_data["yoy_change"] = country_data[metric].pct_change() * 100
                
                trend_info = {
                    "country": country,
                    "data_points": len(country_data),
                    "start_value": float(country_data[metric].iloc[0]),
                    "end_value": float(country_data[metric].iloc[-1]),
                    "total_growth": float(country_data[metric].iloc[-1] - country_data[metric].iloc[0]),
                    "average_yoy_change": float(country_data["yoy_change"].mean()),
                    "max_yoy_change": float(country_data["yoy_change"].max()),
                    "trend_direction": "increasing" if country_data[metric].iloc[-1] > country_data[metric].iloc[0] else "decreasing"
                }
                
                # Add time series data for visualization
                if scope == "specific":
                    trend_info["time_series"] = country_data[["year", metric, "yoy_change"]].to_dict("records")
                
                trend_results["trends"].append(trend_info)
        
        # Generate trend insights
        if self.llm.is_available() and trend_results["trends"]:
            insights = await self._generate_trend_insights(trend_results, analysis_type)
            trend_results["insights"] = insights
        
        return trend_results
    
    async def _generate_trend_insights(self, trend_data: Dict, analysis_type: str) -> List[str]:
        """Generate insights from trend analysis"""
        prompt = f"""Analyze these renewable energy trends ({analysis_type} analysis):
{json.dumps(trend_data, indent=2)}

Generate 3-4 key insights about:
1. Overall patterns
2. Notable outliers or exceptional cases
3. Implications for the future
4. Comparisons between entities (if multiple)

Format as JSON array of insight strings."""

        try:
            insights = await self.llm.generate_json(prompt)
            if isinstance(insights, list):
                return insights
        except Exception as e:
            logger.error(f"Error generating trend insights: {e}")
        
        return ["Trend analysis complete - see data above"]
    
    async def _execute_discover_insights(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Use AI to discover interesting patterns in the data"""
        focus_area = parameters["focus_area"]
        depth = parameters.get("depth", "standard")
        
        if not self.llm.is_available():
            return {
                "error": "LLM required for insight discovery",
                "suggestion": "Try using specific query tools instead"
            }
        
        # Prepare data summary for analysis
        data_summary = {
            "total_records": len(self.df),
            "countries": self.df["country"].nunique(),
            "year_range": f"{self.df['year'].min()}-{self.df['year'].max()}",
            "columns": list(self.df.columns),
            "sample_stats": {
                "avg_solar": self.df["solar_capacity_mw"].mean(),
                "avg_wind": self.df["wind_capacity_mw"].mean(),
                "avg_hydro": self.df["hydro_capacity_mw"].mean(),
                "total_renewable_sum": self.df["total_renewable_mw"].sum()
            }
        }
        
        # Let LLM explore the data
        prompt = f"""Explore renewable energy data to find insights about: "{focus_area}"

Data summary: {json.dumps(data_summary, indent=2)}

Based on this focus area and data, suggest:
1. Specific data queries to run
2. Patterns to look for
3. Comparisons that would be valuable

Depth level: {depth}

Respond with JSON:
{{
    "exploration_plan": ["list of things to explore"],
    "queries_to_run": [
        {{"description": "what to find", "approach": "how to find it"}}
    ],
    "expected_insights": ["potential insights to uncover"]
}}"""

        exploration = await self.llm.generate_json(prompt)
        
        # Execute some of the suggested queries
        discoveries = {
            "focus_area": focus_area,
            "exploration_plan": exploration,
            "discovered_insights": []
        }
        
        # Run a few automated analyses based on focus area
        if "growth" in focus_area.lower() or "rapid" in focus_area.lower():
            # Find fastest growing countries
            growth_analysis = await self._find_fastest_growing()
            discoveries["discovered_insights"].append(growth_analysis)
        
        if "leader" in focus_area.lower() or "top" in focus_area.lower():
            # Find leaders in renewable energy
            leaders = await self._find_leaders()
            discoveries["discovered_insights"].append(leaders)
        
        if "comparison" in focus_area.lower() or "difference" in focus_area.lower():
            # Find interesting comparisons
            comparisons = await self._find_interesting_comparisons()
            discoveries["discovered_insights"].append(comparisons)
        
        return discoveries
    
    async def _find_fastest_growing(self) -> Dict[str, Any]:
        """Find fastest growing countries/sectors"""
        # Calculate growth rates by country
        growth_rates = []
        
        for country in self.df["country"].unique():
            country_data = self.df[self.df["country"] == country].sort_values("year")
            if len(country_data) > 1:
                start_total = country_data["total_renewable_mw"].iloc[0]
                end_total = country_data["total_renewable_mw"].iloc[-1]
                if start_total > 0:
                    growth_rate = ((end_total - start_total) / start_total) * 100
                    growth_rates.append({
                        "country": country,
                        "growth_rate": growth_rate,
                        "absolute_growth": end_total - start_total
                    })
        
        # Sort by growth rate
        growth_rates.sort(key=lambda x: x["growth_rate"], reverse=True)
        
        return {
            "insight_type": "fastest_growing",
            "top_5": growth_rates[:5],
            "finding": f"Fastest growing: {growth_rates[0]['country']} with {growth_rates[0]['growth_rate']:.1f}% growth"
        }
    
    async def _find_leaders(self) -> Dict[str, Any]:
        """Find leaders in renewable energy"""
        latest_year = self.df["year"].max()
        latest_data = self.df[self.df["year"] == latest_year]
        
        leaders = {
            "insight_type": "market_leaders",
            "year": latest_year,
            "by_technology": {}
        }
        
        # Leaders by technology
        for tech in ["solar_capacity_mw", "wind_capacity_mw", "hydro_capacity_mw"]:
            top_country = latest_data.nlargest(1, tech).iloc[0]
            leaders["by_technology"][tech.split("_")[0]] = {
                "country": top_country["country"],
                "capacity": float(top_country[tech])
            }
        
        # Overall leader
        overall_leader = latest_data.nlargest(1, "total_renewable_mw").iloc[0]
        leaders["overall_leader"] = {
            "country": overall_leader["country"],
            "total_capacity": float(overall_leader["total_renewable_mw"])
        }
        
        return leaders
    
    async def _find_interesting_comparisons(self) -> Dict[str, Any]:
        """Find interesting comparisons in the data"""
        latest_year = self.df["year"].max()
        latest_data = self.df[self.df["year"] == latest_year]
        
        comparisons = {
            "insight_type": "interesting_comparisons",
            "findings": []
        }
        
        # Compare renewable mix
        for _, country_data in latest_data.iterrows():
            total = country_data["total_renewable_mw"]
            if total > 0:
                solar_pct = (country_data["solar_capacity_mw"] / total) * 100
                wind_pct = (country_data["wind_capacity_mw"] / total) * 100
                hydro_pct = (country_data["hydro_capacity_mw"] / total) * 100
                
                # Find countries with dominant technology
                if solar_pct > 60:
                    comparisons["findings"].append(f"{country_data['country']}: Solar-dominant ({solar_pct:.1f}%)")
                elif wind_pct > 60:
                    comparisons["findings"].append(f"{country_data['country']}: Wind-dominant ({wind_pct:.1f}%)")
                elif hydro_pct > 60:
                    comparisons["findings"].append(f"{country_data['country']}: Hydro-dominant ({hydro_pct:.1f}%)")
        
        return comparisons