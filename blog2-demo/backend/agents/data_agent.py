"""Data Agent - Provides access to renewable energy datasets"""
import pandas as pd
import os
from typing import Dict, Any, List, Optional
from .unified_base_agent import UnifiedBaseAgent
from mcp.schemas import MCPTool, ToolParameter, ParameterType

class DataAgent(UnifiedBaseAgent):
    AGENT_TYPE = "data"
    
    def __init__(self):
        super().__init__(
            agent_id="data-agent-001",
            name="Data Agent",
            description="Provides access to renewable energy datasets and performs data analysis",
            capabilities=[
                "Query renewable energy data",
                "Analyze energy trends",
                "Aggregate data by country/year",
                "Calculate growth rates",
                "Access to historical data"
            ],
            tags=["data", "analytics", "renewable-energy", "statistics"]
        )
        self.data_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "renewable_energy.csv")
        self._load_data()
    
    def _load_data(self):
        """Load the renewable energy dataset"""
        try:
            self.df = pd.read_csv(self.data_path)
        except Exception as e:
            print(f"Error loading data: {e}")
            self.df = pd.DataFrame()
    
    def _register_tools(self):
        """Register MCP tools for data operations"""
        # Query data tool
        self.register_tool(
            MCPTool(
                name="query_data",
                description="Query renewable energy data by country, year, or energy type",
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
                    )
                ],
                returns={
                    "type": "object",
                    "description": "Filtered data with columns and rows"
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
                description="Aggregate and summarize energy data with calculations",
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
                    )
                ],
                returns={
                    "type": "object",
                    "description": "Aggregated data results"
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
                description="Analyze trends in renewable energy data",
                parameters=[
                    ToolParameter(
                        name="country",
                        type=ParameterType.STRING,
                        description="Country to analyze",
                        required=True
                    ),
                    ToolParameter(
                        name="metric",
                        type=ParameterType.STRING,
                        description="Metric to analyze",
                        required=True,
                        enum=["solar_capacity_mw", "wind_capacity_mw", "hydro_capacity_mw", "total_renewable_mw", "growth_rate"]
                    )
                ],
                returns={
                    "type": "object",
                    "description": "Trend analysis with yearly data"
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
    
    async def _execute_query_data(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute data query"""
        filtered_df = self.df.copy()
        
        # Apply filters
        if parameters.get("country"):
            filtered_df = filtered_df[filtered_df["country"] == parameters["country"]]
        
        if parameters.get("year"):
            filtered_df = filtered_df[filtered_df["year"] == parameters["year"]]
        
        if parameters.get("energy_type") and parameters["energy_type"] != "all":
            # Select relevant columns based on energy type
            base_cols = ["country", "year"]
            if parameters["energy_type"] == "solar":
                cols = base_cols + ["solar_capacity_mw"]
            elif parameters["energy_type"] == "wind":
                cols = base_cols + ["wind_capacity_mw"]
            elif parameters["energy_type"] == "hydro":
                cols = base_cols + ["hydro_capacity_mw"]
            filtered_df = filtered_df[cols]
        
        return {
            "columns": list(filtered_df.columns),
            "data": filtered_df.to_dict("records"),
            "row_count": len(filtered_df)
        }
    
    async def _execute_aggregate_data(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute data aggregation"""
        metric = parameters["metric"]
        group_by = parameters.get("group_by", "none")
        column = parameters["column"]
        
        if group_by == "none":
            # Simple aggregation
            if metric == "sum":
                result = self.df[column].sum()
            elif metric == "average":
                result = self.df[column].mean()
            elif metric == "max":
                result = self.df[column].max()
            elif metric == "min":
                result = self.df[column].min()
            
            return {
                "metric": metric,
                "column": column,
                "value": float(result)
            }
        else:
            # Grouped aggregation
            grouped = self.df.groupby(group_by)[column]
            
            if metric == "sum":
                result = grouped.sum()
            elif metric == "average":
                result = grouped.mean()
            elif metric == "max":
                result = grouped.max()
            elif metric == "min":
                result = grouped.min()
            
            return {
                "metric": metric,
                "column": column,
                "group_by": group_by,
                "data": result.reset_index().to_dict("records")
            }
    
    async def _execute_get_trends(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute trend analysis"""
        country = parameters["country"]
        metric = parameters["metric"]
        
        # Filter data for the country
        country_data = self.df[self.df["country"] == country].sort_values("year")
        
        if country_data.empty:
            return {
                "error": f"No data found for country: {country}"
            }
        
        # Calculate year-over-year change
        country_data["yoy_change"] = country_data[metric].pct_change() * 100
        
        return {
            "country": country,
            "metric": metric,
            "data": country_data[["year", metric, "yoy_change"]].to_dict("records"),
            "summary": {
                "start_value": float(country_data[metric].iloc[0]),
                "end_value": float(country_data[metric].iloc[-1]),
                "total_growth": float(country_data[metric].iloc[-1] - country_data[metric].iloc[0]),
                "average_yoy_change": float(country_data["yoy_change"].mean())
            }
        }