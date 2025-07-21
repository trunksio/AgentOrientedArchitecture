import sys
sys.path.append("/app/shared")
"""Research Agent - Gathers external context and insights"""
from typing import Dict, Any, List, Optional
import json
import logging
from unified_base_agent import UnifiedBaseAgent
from mcp.schemas import MCPTool, ToolParameter, ParameterType
from llm import LLMConfig

logger = logging.getLogger(__name__)

class ResearchAgent(UnifiedBaseAgent):
    AGENT_TYPE = "research"
    
    def __init__(self, llm_config=None):
        super().__init__(, capabilities=self._get_capabilities(), tags=self._get_tags())
            agent_id="research-agent-001",
            name="Research Agent",
            description="Gathers external context and insights about renewable energy",
            llm_config=llm_config
        )
    
    def _register_tools(self):
        """Register MCP tools for research"""
        # Research trends tool
        self.register_tool(
            MCPTool(
                name="research_trends",
                description="Research current trends and news in renewable energy",
                parameters=[
                    ToolParameter(
                        name="topic",
                        type=ParameterType.STRING,
                        description="Topic to research",
                        required=True
                    ),
                    ToolParameter(
                        name="timeframe",
                        type=ParameterType.STRING,
                        description="Time period to focus on",
                        required=False,
                        enum=["recent", "past_year", "past_5_years", "all_time"],
                        default="recent"
                    ),
                    ToolParameter(
                        name="region",
                        type=ParameterType.STRING,
                        description="Geographic region to focus on",
                        required=False
                    )
                ],
                returns={
                    "type": "object",
                    "description": "Research findings and insights"
                },
                examples=[
                    {
                        "parameters": {"topic": "solar panel efficiency", "timeframe": "recent"},
                        "description": "Research recent solar panel efficiency improvements"
                    }
                ]
            ),
            self._execute_research_trends
        )
        
        # Analyze context tool
        self.register_tool(
            MCPTool(
                name="analyze_context",
                description="Provide contextual analysis for data",
                parameters=[
                    ToolParameter(
                        name="data",
                        type=ParameterType.OBJECT,
                        description="Data to analyze",
                        required=True
                    ),
                    ToolParameter(
                        name="focus",
                        type=ParameterType.STRING,
                        description="Specific aspect to focus on",
                        required=True
                    ),
                    ToolParameter(
                        name="depth",
                        type=ParameterType.STRING,
                        description="Analysis depth",
                        required=False,
                        enum=["summary", "detailed", "comprehensive"],
                        default="detailed"
                    )
                ],
                returns={
                    "type": "object",
                    "description": "Contextual analysis and insights"
                },
                examples=[
                    {
                        "parameters": {
                            "data": {"country": "China", "solar_growth": "25%"},
                            "focus": "growth factors"
                        },
                        "description": "Analyze factors behind China's solar growth"
                    }
                ]
            ),
            self._execute_analyze_context
        )
        
        # Generate insights tool
        self.register_tool(
            MCPTool(
                name="generate_insights",
                description="Generate strategic insights from data patterns",
                parameters=[
                    ToolParameter(
                        name="data_patterns",
                        type=ParameterType.OBJECT,
                        description="Data patterns to analyze",
                        required=True
                    ),
                    ToolParameter(
                        name="perspective",
                        type=ParameterType.STRING,
                        description="Analysis perspective",
                        required=False,
                        enum=["technical", "economic", "environmental", "policy", "comprehensive"],
                        default="comprehensive"
                    )
                ],
                returns={
                    "type": "object",
                    "description": "Strategic insights and recommendations"
                },
                examples=[
                    {
                        "parameters": {
                            "data_patterns": {"trend": "increasing", "rate": "15% annually"},
                            "perspective": "economic"
                        },
                        "description": "Generate economic insights from growth patterns"
                    }
                ]
            ),
            self._execute_generate_insights
        )
    
    async def _execute_research_trends(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Research trends in renewable energy"""
        topic = parameters["topic"]
        timeframe = parameters.get("timeframe", "recent")
        region = parameters.get("region", "global")
        
        if not self.llm.is_available():
            # Provide static insights if no LLM
            return {
                "topic": topic,
                "timeframe": timeframe,
                "findings": [
                    f"Research on {topic} shows significant developments",
                    "Technology improvements driving adoption",
                    "Policy support increasing globally"
                ],
                "sources": ["Industry reports", "Academic research", "Market analysis"],
                "confidence": "limited - no LLM available"
            }
        
        # Use LLM to generate research insights
        prompt = f"""Research the topic of "{topic}" in renewable energy, focusing on {timeframe} developments{' in ' + region if region != 'global' else ''}.

Provide insights on:
1. Current state and recent developments
2. Key drivers and challenges
3. Notable innovations or breakthroughs
4. Market trends and adoption rates
5. Future outlook

Format as JSON with sections: overview, key_findings, challenges, opportunities, outlook"""

        system_prompt = """You are a renewable energy research expert with deep knowledge of:
- Solar, wind, and hydro technologies
- Energy markets and economics
- Environmental impacts and sustainability
- Policy and regulatory frameworks
- Technological innovations

Provide well-researched, factual insights based on current trends."""

        research_data = await self.llm.generate_json(prompt, system_prompt)
        
        if not research_data:
            research_data = {
                "overview": f"Analysis of {topic}",
                "key_findings": ["Data unavailable"],
                "challenges": ["Research generation failed"],
                "opportunities": [],
                "outlook": "Unable to generate insights"
            }
        
        return {
            "topic": topic,
            "timeframe": timeframe,
            "region": region,
            "research": research_data,
            "confidence": "high" if research_data else "low"
        }
    
    async def _execute_analyze_context(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Provide contextual analysis for data"""
        data = parameters["data"]
        focus = parameters["focus"]
        depth = parameters.get("depth", "detailed")
        
        if not self.llm.is_available():
            return {
                "data": data,
                "focus": focus,
                "analysis": {
                    "summary": f"Analysis of {focus} for provided data",
                    "factors": ["Economic conditions", "Policy support", "Technology maturity"],
                    "implications": ["Continued growth expected", "Investment opportunities"]
                },
                "confidence": "limited"
            }
        
        # Create context-aware prompt
        prompt = f"""Analyze this renewable energy data with focus on "{focus}":

Data: {json.dumps(data, indent=2)}

Provide {depth} analysis covering:
1. Key factors influencing the {focus}
2. Historical context and comparisons
3. Causal relationships and correlations
4. Implications for stakeholders
5. Risk factors and uncertainties

Format as JSON with sections: summary, key_factors, historical_context, implications, risks"""

        system_prompt = """You are an expert analyst specializing in renewable energy markets and technology. 
Provide data-driven insights that consider technological, economic, environmental, and policy factors."""

        analysis = await self.llm.generate_json(prompt, system_prompt)
        
        if not analysis:
            analysis = {
                "summary": f"Unable to generate detailed analysis for {focus}",
                "key_factors": [],
                "implications": []
            }
        
        return {
            "data": data,
            "focus": focus,
            "depth": depth,
            "analysis": analysis,
            "confidence": "high" if analysis else "low"
        }
    
    async def _execute_generate_insights(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Generate strategic insights from patterns"""
        data_patterns = parameters["data_patterns"]
        perspective = parameters.get("perspective", "comprehensive")
        
        if not self.llm.is_available():
            return {
                "patterns": data_patterns,
                "insights": [
                    "Pattern analysis shows positive trends",
                    "Strategic opportunities identified",
                    "Risk mitigation strategies recommended"
                ],
                "recommendations": [
                    "Monitor emerging technologies",
                    "Diversify energy portfolio",
                    "Invest in grid infrastructure"
                ],
                "confidence": "limited"
            }
        
        # Generate strategic insights
        prompt = f"""Analyze these renewable energy data patterns from a {perspective} perspective:

Patterns: {json.dumps(data_patterns, indent=2)}

Generate strategic insights including:
1. Pattern interpretation and significance
2. Underlying drivers and mechanisms
3. Strategic implications
4. Actionable recommendations
5. Future scenarios and probabilities

Format as JSON with: pattern_analysis, strategic_insights, recommendations, scenarios"""

        system_prompt = f"""You are a strategic advisor specializing in renewable energy from a {perspective} perspective.
Provide actionable insights that consider market dynamics, technology trends, and stakeholder interests."""

        insights = await self.llm.generate_json(prompt, system_prompt)
        
        if not insights:
            insights = {
                "pattern_analysis": "Unable to generate detailed insights",
                "strategic_insights": [],
                "recommendations": []
            }
        
        return {
            "patterns": data_patterns,
            "perspective": perspective,
            "insights": insights,
            "confidence": "high" if insights else "low",
            "generated_by": "research-agent"
        }