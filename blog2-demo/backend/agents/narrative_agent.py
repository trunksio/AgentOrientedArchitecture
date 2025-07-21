"""Narrative Agent - Generates data-driven stories and explanations"""
from typing import Dict, Any, List
import json
import logging
from .unified_base_agent import UnifiedBaseAgent
from mcp.schemas import MCPTool, ToolParameter, ParameterType

logger = logging.getLogger(__name__)

class NarrativeAgent(UnifiedBaseAgent):
    AGENT_TYPE = "narrative"
    
    def __init__(self):
        super().__init__(
            agent_id="narrative-agent-001",
            name="Narrative Agent",
            description="Generates data-driven stories and explanations",
            capabilities=[
                "Generate data stories",
                "Create narrative explanations",
                "Produce insights summaries",
                "Write trend analysis",
                "Craft compelling narratives"
            ],
            tags=["narrative", "storytelling", "content", "writing"]
        )
    
    def _register_tools(self):
        """Register MCP tools for narrative generation"""
        # Generate story tool
        self.register_tool(
            MCPTool(
                name="generate_story",
                description="Create narrative explanations from data",
                parameters=[
                    ToolParameter(
                        name="data",
                        type=ParameterType.OBJECT,
                        description="Data to create narrative from",
                        required=True
                    ),
                    ToolParameter(
                        name="theme",
                        type=ParameterType.STRING,
                        description="Narrative theme or angle",
                        required=True
                    ),
                    ToolParameter(
                        name="length",
                        type=ParameterType.STRING,
                        description="Story length",
                        required=False,
                        enum=["brief", "standard", "detailed"],
                        default="standard"
                    ),
                    ToolParameter(
                        name="audience",
                        type=ParameterType.STRING,
                        description="Target audience",
                        required=False,
                        enum=["general", "technical", "executive", "academic"],
                        default="general"
                    )
                ],
                returns={
                    "type": "object",
                    "description": "Narrative content with structure"
                },
                examples=[
                    {
                        "parameters": {
                            "data": {"solar_growth": "300%", "period": "2015-2024"},
                            "theme": "renewable revolution",
                            "audience": "general"
                        },
                        "description": "Tell the story of solar energy growth"
                    }
                ]
            ),
            self._execute_generate_story
        )
        
        # Create summary tool
        self.register_tool(
            MCPTool(
                name="create_summary",
                description="Summarize complex data insights",
                parameters=[
                    ToolParameter(
                        name="data",
                        type=ParameterType.OBJECT,
                        description="Data to summarize",
                        required=True
                    ),
                    ToolParameter(
                        name="focus_points",
                        type=ParameterType.ARRAY,
                        description="Key points to focus on",
                        required=False
                    ),
                    ToolParameter(
                        name="style",
                        type=ParameterType.STRING,
                        description="Summary style",
                        required=False,
                        enum=["bullet_points", "paragraph", "executive"],
                        default="paragraph"
                    )
                ],
                returns={
                    "type": "object",
                    "description": "Structured summary"
                },
                examples=[
                    {
                        "parameters": {
                            "data": {"countries": 5, "total_capacity": "2000GW"},
                            "focus_points": ["growth", "leaders"],
                            "style": "executive"
                        },
                        "description": "Executive summary of renewable capacity"
                    }
                ]
            ),
            self._execute_create_summary
        )
        
        # Explain trends tool
        self.register_tool(
            MCPTool(
                name="explain_trends",
                description="Explain data trends in narrative form",
                parameters=[
                    ToolParameter(
                        name="trend_data",
                        type=ParameterType.OBJECT,
                        description="Trend data to explain",
                        required=True
                    ),
                    ToolParameter(
                        name="complexity",
                        type=ParameterType.STRING,
                        description="Explanation complexity",
                        required=False,
                        enum=["simple", "moderate", "detailed"],
                        default="moderate"
                    ),
                    ToolParameter(
                        name="include_forecast",
                        type=ParameterType.BOOLEAN,
                        description="Include future projections",
                        required=False,
                        default=False
                    )
                ],
                returns={
                    "type": "object",
                    "description": "Trend explanation with narrative"
                },
                examples=[
                    {
                        "parameters": {
                            "trend_data": {"type": "exponential", "rate": "20% yearly"},
                            "complexity": "simple"
                        },
                        "description": "Explain exponential growth trend"
                    }
                ]
            ),
            self._execute_explain_trends
        )
    
    async def _execute_generate_story(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a narrative story from data"""
        data = parameters["data"]
        theme = parameters["theme"]
        length = parameters.get("length", "standard")
        audience = parameters.get("audience", "general")
        
        if not self.llm.is_available():
            # Provide basic narrative without LLM
            return {
                "title": f"The Story of {theme}",
                "narrative": {
                    "introduction": f"This is a story about {theme} based on the data provided.",
                    "body": [
                        "The data shows significant changes over time.",
                        "Key metrics indicate positive trends.",
                        "Future outlook remains promising."
                    ],
                    "conclusion": "The transformation continues to accelerate."
                },
                "style": "basic",
                "confidence": "limited"
            }
        
        # Generate narrative using LLM
        word_counts = {"brief": 200, "standard": 500, "detailed": 1000}
        target_words = word_counts.get(length, 500)
        
        prompt = f"""Create a compelling {length} narrative (approximately {target_words} words) about "{theme}" using this data:

Data: {json.dumps(data, indent=2)}

Target audience: {audience}

Structure the narrative with:
1. Engaging title
2. Compelling introduction that hooks the reader
3. Body with 3-5 key points woven into the story
4. Data-driven insights presented narratively
5. Forward-looking conclusion

Make it engaging and accessible to a {audience} audience. Use metaphors and analogies where appropriate.

Format as JSON with: title, introduction, body (array of paragraphs), key_insights, conclusion"""

        system_prompt = f"""You are a master storyteller specializing in making data come alive through narrative.
You excel at transforming complex renewable energy data into engaging stories for {audience} audiences.
Your narratives are accurate, compelling, and inspire action."""

        story = await self.llm.generate_json(prompt, system_prompt)
        
        if not story:
            story = {
                "title": f"Understanding {theme}",
                "introduction": "Data tells an important story.",
                "body": ["Analysis unavailable"],
                "conclusion": "More insights to come."
            }
        
        # Generate React component for the narrative
        component_code = self._generate_narrative_component(story, theme)
        
        return {
            "theme": theme,
            "audience": audience,
            "length": length,
            "story": story,
            "component_code": component_code,
            "confidence": "high" if story else "low"
        }
    
    async def _execute_create_summary(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Create a summary of complex data"""
        data = parameters["data"]
        focus_points = parameters.get("focus_points", [])
        style = parameters.get("style", "paragraph")
        
        if not self.llm.is_available():
            return {
                "summary": "Data summary: Key metrics show positive trends across all measured categories.",
                "highlights": ["Growth observed", "Trends positive", "Outlook favorable"],
                "style": style,
                "confidence": "limited"
            }
        
        # Generate summary using LLM
        prompt = f"""Summarize this renewable energy data in {style} format:

Data: {json.dumps(data, indent=2)}
{f"Focus on: {', '.join(focus_points)}" if focus_points else ""}

Create a {style} summary that:
1. Captures the most important insights
2. Highlights key numbers and trends
3. Provides context and meaning
4. Is concise yet comprehensive

Format as JSON with: summary, key_points, highlights, context"""

        system_prompt = """You are an expert at distilling complex data into clear, actionable summaries.
You understand what matters most to different stakeholders and communicate insights effectively."""

        summary_data = await self.llm.generate_json(prompt, system_prompt)
        
        if not summary_data:
            summary_data = {
                "summary": "Summary generation failed",
                "key_points": [],
                "highlights": []
            }
        
        return {
            "data": data,
            "focus_points": focus_points,
            "style": style,
            "content": summary_data,
            "confidence": "high" if summary_data else "low"
        }
    
    async def _execute_explain_trends(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Explain trends in narrative form"""
        trend_data = parameters["trend_data"]
        complexity = parameters.get("complexity", "moderate")
        include_forecast = parameters.get("include_forecast", False)
        
        if not self.llm.is_available():
            return {
                "explanation": "This trend shows consistent patterns over time.",
                "factors": ["Market dynamics", "Technology improvements", "Policy support"],
                "forecast": "Continued growth expected" if include_forecast else None,
                "confidence": "limited"
            }
        
        # Generate trend explanation
        prompt = f"""Explain this renewable energy trend in a {complexity} way:

Trend data: {json.dumps(trend_data, indent=2)}

Provide an explanation that:
1. Describes what the trend shows
2. Explains why this trend is occurring
3. Identifies key driving factors
4. Discusses implications
{f"5. Projects future developments" if include_forecast else ""}

Use analogies and examples to make it accessible.

Format as JSON with: explanation, driving_factors, implications, {f"forecast," if include_forecast else ""} analogies"""

        system_prompt = f"""You are an expert at explaining complex trends in {"simple terms" if complexity == "simple" else "appropriate detail"}.
Make data trends understandable and meaningful to your audience."""

        explanation = await self.llm.generate_json(prompt, system_prompt)
        
        if not explanation:
            explanation = {
                "explanation": "Trend analysis unavailable",
                "driving_factors": [],
                "implications": []
            }
        
        return {
            "trend_data": trend_data,
            "complexity": complexity,
            "narrative": explanation,
            "include_forecast": include_forecast,
            "confidence": "high" if explanation else "low"
        }
    
    def _generate_narrative_component(self, story: Dict[str, Any], theme: str) -> str:
        """Generate React component for narrative display"""
        return f'''
import React from 'react';
import {{ motion }} from 'framer-motion';

export default function NarrativeStory() {{
  const story = {json.dumps(story, indent=2)};
  
  return (
    <div className="bg-white dark:bg-slate-800 rounded-lg shadow-lg p-8 max-w-4xl mx-auto">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
      >
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-6">
          {{story.title}}
        </h1>
        
        <div className="prose prose-lg dark:prose-invert max-w-none">
          <p className="text-xl text-gray-700 dark:text-gray-300 mb-6 leading-relaxed">
            {{story.introduction}}
          </p>
          
          <div className="space-y-4">
            {{story.body && story.body.map((paragraph, index) => (
              <motion.p
                key={{index}}
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: index * 0.2 }}
                className="text-gray-600 dark:text-gray-300"
              >
                {{paragraph}}
              </motion.p>
            ))}}
          </div>
          
          {{story.key_insights && (
            <div className="bg-aoa-primary/10 border-l-4 border-aoa-primary p-4 my-6">
              <h3 className="font-semibold mb-2">Key Insights</h3>
              <ul className="list-disc list-inside space-y-1">
                {{story.key_insights.map((insight, idx) => (
                  <li key={{idx}} className="text-sm">{{insight}}</li>
                ))}}
              </ul>
            </div>
          )}}
          
          <div className="mt-8 pt-6 border-t border-gray-200 dark:border-gray-700">
            <p className="text-gray-700 dark:text-gray-300 italic">
              {{story.conclusion}}
            </p>
          </div>
        </div>
      </motion.div>
    </div>
  );
}}
'''