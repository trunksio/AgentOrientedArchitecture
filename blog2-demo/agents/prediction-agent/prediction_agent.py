import asyncio
import logging
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import sys
import os

# Add the shared directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'shared'))

from base_agent import BaseAgent
from models import A2AMessage
from mcp.tool_registry import mcp_tool

logger = logging.getLogger(__name__)

class PredictionAgent(BaseAgent):
    """Agent specialized in forecasting and trend prediction for renewable energy"""
    
    def __init__(self):
        super().__init__(
            agent_id="prediction-agent-001",
            name="Prediction Agent",
            description="I specialize in forecasting future trends, creating predictions, and analyzing growth patterns in renewable energy data",
            capabilities=[
                "trend forecasting",
                "future predictions", 
                "growth modeling",
                "scenario analysis",
                "pattern recognition",
                "time series analysis"
            ]
        )
        
    @mcp_tool(
        name="analyze_trends",
        description="Analyze historical data to identify trends and patterns",
        parameters={
            "data": "Historical data for trend analysis",
            "metric": "Metric to analyze (e.g., 'total_renewable_mw', 'growth_rate')",
            "time_column": "Column containing time/date information"
        }
    )
    async def analyze_trends(self, data: List[Dict], metric: str, time_column: str = "year") -> Dict[str, Any]:
        """Analyze trends in historical data"""
        try:
            df = pd.DataFrame(data)
            
            if metric not in df.columns:
                return {"error": f"Metric '{metric}' not found in data"}
            
            # Calculate trend analysis
            trends = {}
            
            # Overall trend
            correlation = df[time_column].corr(df[metric])
            
            # Growth rate calculation
            if len(df) > 1:
                total_growth = ((df[metric].iloc[-1] / df[metric].iloc[0]) - 1) * 100
                years = df[time_column].iloc[-1] - df[time_column].iloc[0]
                annual_growth = ((df[metric].iloc[-1] / df[metric].iloc[0]) ** (1/years) - 1) * 100 if years > 0 else 0
            else:
                total_growth = 0
                annual_growth = 0
            
            # Trend direction
            if correlation > 0.7:
                direction = "Strong upward trend"
            elif correlation > 0.3:
                direction = "Moderate upward trend"
            elif correlation > -0.3:
                direction = "Stable/flat trend"
            elif correlation > -0.7:
                direction = "Moderate downward trend"
            else:
                direction = "Strong downward trend"
            
            return {
                "metric": metric,
                "direction": direction,
                "correlation": round(correlation, 3),
                "total_growth_percent": round(total_growth, 2),
                "annual_growth_rate": round(annual_growth, 2),
                "data_points": len(df),
                "time_range": f"{df[time_column].min()} - {df[time_column].max()}"
            }
            
        except Exception as e:
            logger.error(f"Error analyzing trends: {e}")
            return {"error": f"Failed to analyze trends: {str(e)}"}
    
    @mcp_tool(
        name="generate_forecast",
        description="Generate future predictions based on historical data",
        parameters={
            "data": "Historical data for forecasting",
            "metric": "Metric to forecast",
            "forecast_years": "Number of years to forecast into the future",
            "scenario": "Scenario type: 'conservative', 'moderate', 'aggressive'"
        }
    )
    async def generate_forecast(self, data: List[Dict], metric: str, forecast_years: int = 5, scenario: str = "moderate") -> Dict[str, Any]:
        """Generate forecast predictions"""
        try:
            df = pd.DataFrame(data)
            
            if metric not in df.columns or "year" not in df.columns:
                return {"error": f"Required columns not found in data"}
            
            # Sort by year
            df = df.sort_values("year")
            
            # Calculate growth rates
            df['growth_rate'] = df[metric].pct_change() * 100
            
            # Get recent growth trends (last 5 years)
            recent_years = 5
            recent_data = df.tail(recent_years)
            avg_growth = recent_data['growth_rate'].mean()
            
            # Scenario adjustments
            scenario_multipliers = {
                "conservative": 0.7,
                "moderate": 1.0,
                "aggressive": 1.3
            }
            
            growth_rate = avg_growth * scenario_multipliers.get(scenario, 1.0)
            
            # Generate forecast
            last_year = df["year"].max()
            last_value = df[df["year"] == last_year][metric].iloc[0]
            
            forecast_data = []
            current_value = last_value
            
            for i in range(1, forecast_years + 1):
                # Apply some randomness to make it more realistic
                year_growth = growth_rate + np.random.normal(0, 2)  # Add some noise
                current_value = current_value * (1 + year_growth / 100)
                
                forecast_data.append({
                    "year": last_year + i,
                    metric: round(current_value, 0),
                    "growth_rate": round(year_growth, 2),
                    "confidence": max(90 - (i * 10), 50)  # Confidence decreases over time
                })
            
            return {
                "metric": metric,
                "scenario": scenario,
                "base_growth_rate": round(avg_growth, 2),
                "adjusted_growth_rate": round(growth_rate, 2),
                "forecast_period": f"{last_year + 1} - {last_year + forecast_years}",
                "forecasts": forecast_data,
                "methodology": f"Based on {recent_years}-year average growth rate with {scenario} scenario adjustments"
            }
            
        except Exception as e:
            logger.error(f"Error generating forecast: {e}")
            return {"error": f"Failed to generate forecast: {str(e)}"}
    
    @mcp_tool(
        name="explain_methodology",
        description="Explain the prediction methodology and assumptions",
        parameters={
            "forecast_type": "Type of forecast to explain",
            "data_characteristics": "Description of the input data"
        }
    )
    async def explain_methodology(self, forecast_type: str = "trend_based", data_characteristics: str = "") -> Dict[str, Any]:
        """Explain prediction methodology"""
        
        explanations = {
            "trend_based": {
                "method": "Historical Trend Analysis",
                "description": "Uses recent historical growth rates to project future values",
                "assumptions": [
                    "Historical trends will continue",
                    "No major disruptive events",
                    "Policy environment remains stable",
                    "Technology adoption follows similar patterns"
                ],
                "limitations": [
                    "Cannot predict black swan events",
                    "Accuracy decreases over longer time horizons",
                    "Assumes linear or exponential growth patterns",
                    "Market saturation effects not fully modeled"
                ],
                "confidence_factors": [
                    "Data quality and completeness",
                    "Length of historical period",
                    "Consistency of past trends",
                    "External validation sources"
                ]
            }
        }
        
        explanation = explanations.get(forecast_type, explanations["trend_based"])
        
        return {
            "forecast_type": forecast_type,
            "methodology": explanation,
            "data_notes": data_characteristics,
            "recommendation": "Use multiple scenarios and external validation for decision-making"
        }
    
    @mcp_tool(
        name="scenario_analysis", 
        description="Compare multiple forecast scenarios",
        parameters={
            "data": "Historical data for analysis",
            "metric": "Metric to analyze",
            "scenarios": "List of scenarios to compare"
        }
    )
    async def scenario_analysis(self, data: List[Dict], metric: str, scenarios: List[str] = None) -> Dict[str, Any]:
        """Compare multiple forecast scenarios"""
        if scenarios is None:
            scenarios = ["conservative", "moderate", "aggressive"]
        
        try:
            scenario_results = {}
            
            for scenario in scenarios:
                forecast = await self.generate_forecast(data, metric, forecast_years=5, scenario=scenario)
                if "error" not in forecast:
                    scenario_results[scenario] = forecast
            
            # Calculate scenario ranges
            if scenario_results:
                years = set()
                for scenario_data in scenario_results.values():
                    for forecast in scenario_data["forecasts"]:
                        years.add(forecast["year"])
                
                comparison = []
                for year in sorted(years):
                    year_data = {"year": year}
                    values = []
                    for scenario, scenario_data in scenario_results.items():
                        for forecast in scenario_data["forecasts"]:
                            if forecast["year"] == year:
                                year_data[f"{scenario}_{metric}"] = forecast[metric]
                                values.append(forecast[metric])
                    
                    if values:
                        year_data["range_low"] = min(values)
                        year_data["range_high"] = max(values)
                        year_data["spread_percent"] = round(((max(values) - min(values)) / min(values)) * 100, 1)
                    
                    comparison.append(year_data)
                
                return {
                    "metric": metric,
                    "scenarios": list(scenarios),
                    "individual_forecasts": scenario_results,
                    "comparison": comparison,
                    "insights": [
                        f"Forecast range varies by {comparison[-1].get('spread_percent', 0)}% in final year",
                        f"Conservative scenario projects {scenario_results.get('conservative', {}).get('adjusted_growth_rate', 0)}% annual growth",
                        f"Aggressive scenario projects {scenario_results.get('aggressive', {}).get('adjusted_growth_rate', 0)}% annual growth"
                    ]
                }
            
            return {"error": "No valid scenarios generated"}
            
        except Exception as e:
            logger.error(f"Error in scenario analysis: {e}")
            return {"error": f"Failed to perform scenario analysis: {str(e)}"}

    async def handle_a2a_message(self, message: A2AMessage) -> Any:
        """Handle A2A messages with intelligent tool selection"""
        logger.info(f"Prediction Agent received message: {message.action}")
        
        # Use LLM for complex prediction queries
        if self.llm.is_available() and any(keyword in message.action.lower() 
                                         for keyword in ["predict", "forecast", "future", "trend", "growth", "scenario"]):
            return await self._handle_prediction_query(message)
        
        # Fall back to standard handling
        return await super().handle_a2a_message(message)
    
    async def _handle_prediction_query(self, message: A2AMessage) -> Dict[str, Any]:
        """Handle prediction queries with LLM intelligence"""
        query = message.payload.get("query", message.action)
        
        prompt = f"""Analyze this prediction request: "{query}"

Available prediction tools:
1. analyze_trends - Identify patterns in historical data
2. generate_forecast - Create future predictions with scenarios
3. explain_methodology - Explain prediction approach
4. scenario_analysis - Compare multiple forecast scenarios

Determine the best approach and create a tool execution plan.

Respond with JSON:
{{
    "intent": "what the user wants to predict",
    "recommended_tools": [
        {{"tool": "tool_name", "parameters": {{}}, "purpose": "why this tool"}}
    ],
    "prediction_type": "trend_based|scenario_based|comparative",
    "key_insights_to_provide": ["list of insights to highlight"]
}}"""

        system_prompt = """You are an intelligent prediction agent specializing in renewable energy forecasting.
You understand complex prediction requests and select the best tools for accurate forecasting."""

        try:
            response = await self.llm.get_completion(prompt, system_prompt)
            plan = self.llm.parse_json_response(response)
            
            results = []
            for tool_step in plan.get("recommended_tools", []):
                tool_name = tool_step["tool"]
                params = tool_step["parameters"]
                
                # Add data from message if available
                if "data" in message.payload:
                    params["data"] = message.payload["data"]
                
                # Execute the tool
                if hasattr(self, tool_name):
                    tool_method = getattr(self, tool_name)
                    result = await tool_method(**params)
                    results.append({
                        "tool": tool_name,
                        "purpose": tool_step["purpose"],
                        "result": result
                    })
            
            return {
                "query": query,
                "intent": plan.get("intent"),
                "prediction_type": plan.get("prediction_type"),
                "results": results,
                "key_insights": plan.get("key_insights_to_provide", []),
                "agent": self.agent_id,
                "method": "llm_guided_prediction"
            }
            
        except Exception as e:
            logger.error(f"Error in LLM-guided prediction: {e}")
            # Fallback to simple forecast
            return await self.generate_forecast(
                data=message.payload.get("data", []),
                metric="total_renewable_mw",
                forecast_years=5
            )

if __name__ == "__main__":
    import uvicorn
    from agent_runner import run_agent
    
    agent = PredictionAgent()
    run_agent(agent, port=8007) 