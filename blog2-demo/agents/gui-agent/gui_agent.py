import sys
sys.path.append("/app/shared")
"""GUI Agent - Orchestrates other agents and manages UI composition"""
from typing import Dict, Any, List, Optional
import json
import logging
import httpx
import os
from base_agent import BaseAgent
from mcp.schemas import MCPTool, ToolParameter, ParameterType
from llm import LLMConfig
from models import MessageType

logger = logging.getLogger(__name__)

class GUIAgent(BaseAgent):
    AGENT_TYPE = "gui"
    
    def __init__(self, llm_config=None):
        super().__init__(
            agent_id="gui-agent-001",
            name="GUI Agent",
            description="Orchestrates other agents and manages the user interface",
            llm_config=llm_config
        )
        # Get backend URL for distributed A2A messaging
        self.backend_url = os.getenv("A2A_REGISTRY_URL", "http://backend:8000")
    
    def _register_tools(self):
        """Register MCP tools for orchestration"""
        # Orchestrate query tool
        self.register_tool(
            MCPTool(
                name="orchestrate_query",
                description="Coordinate multiple agents to answer complex queries",
                parameters=[
                    ToolParameter(
                        name="query",
                        type=ParameterType.STRING,
                        description="User's query or request",
                        required=True
                    ),
                    ToolParameter(
                        name="context",
                        type=ParameterType.OBJECT,
                        description="Additional context for the query",
                        required=False
                    )
                ],
                returns={
                    "type": "object",
                    "description": "Orchestration plan and results"
                },
                examples=[
                    {
                        "parameters": {"query": "Analyze renewable energy trends with visualizations"},
                        "description": "Coordinate data and visualization agents"
                    }
                ]
            ),
            self._execute_orchestrate_query
        )
        
        # Compose UI tool
        self.register_tool(
            MCPTool(
                name="compose_ui",
                description="Dynamically compose UI components from agent results",
                parameters=[
                    ToolParameter(
                        name="components",
                        type=ParameterType.ARRAY,
                        description="List of component specifications",
                        required=True
                    ),
                    ToolParameter(
                        name="layout",
                        type=ParameterType.STRING,
                        description="Layout strategy",
                        required=False,
                        enum=["auto", "grid", "vertical", "horizontal", "dashboard"],
                        default="auto"
                    )
                ],
                returns={
                    "type": "object",
                    "description": "Composed UI specification"
                },
                examples=[
                    {
                        "parameters": {
                            "components": [{"type": "chart"}, {"type": "narrative"}],
                            "layout": "dashboard"
                        },
                        "description": "Compose a dashboard with charts and narrative"
                    }
                ]
            ),
            self._execute_compose_ui
        )
        
        # Plan execution tool
        self.register_tool(
            MCPTool(
                name="plan_execution",
                description="Create an execution plan for a complex query",
                parameters=[
                    ToolParameter(
                        name="query",
                        type=ParameterType.STRING,
                        description="User's query",
                        required=True
                    ),
                    ToolParameter(
                        name="available_agents",
                        type=ParameterType.ARRAY,
                        description="List of available agent IDs",
                        required=False
                    )
                ],
                returns={
                    "type": "object",
                    "description": "Execution plan with steps and agent assignments"
                },
                examples=[
                    {
                        "parameters": {"query": "Show me renewable energy growth with predictions"},
                        "description": "Plan multi-agent execution"
                    }
                ]
            ),
            self._execute_plan_execution
        )
    
    async def _execute_orchestrate_query(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Orchestrate multiple agents to handle a query using A2A Protocol"""
        logger.info(f"Starting orchestration with parameters: {parameters}")
        query = parameters["query"]
        context = parameters.get("context", {})
        
        # Use A2A orchestration if registry is available
        if self.a2a_registry:
            orchestration_result = await self.a2a_registry.orchestrate_agents(
                intent=query,
                initiator=self.agent_id
            )
            
            # If A2A orchestration worked, return those results
            if orchestration_result.get("success"):
                return {
                    "query": query,
                    "method": "a2a_orchestration",
                    "agents_used": orchestration_result["agents_involved"],
                    "steps": orchestration_result["steps"],
                    "results": orchestration_result["results"],
                    "status": "completed"
                }
        
        # Fallback: Use LLM to create orchestration plan
        orchestration_plan = None
        if self.llm.is_available():
            prompt = f"""Analyze this user query and determine which agents and tools to use:
Query: "{query}"
Context: {json.dumps(context)}

Available agents (use these exact IDs):
1. data-agent-001 - Query and analyze renewable energy data
2. viz-agent-001 - Create charts and visualizations
3. research-agent-001 - Gather external insights
4. narrative-agent-001 - Generate stories and explanations

Create an orchestration plan with:
1. agents_needed: List of agent IDs needed
2. execution_steps: Ordered list of objects with agent_id, action, and parameters fields
3. expected_outputs: What each step should produce

Respond with JSON."""

            system_prompt = "You are an expert AI orchestrator that coordinates multiple specialized agents to fulfill user requests."
            
            orchestration_plan = await self.llm.generate_json(prompt, system_prompt)
        
        if not orchestration_plan:
            # Fallback to simple keyword-based orchestration
            orchestration_plan = self._simple_orchestration(query)
        else:
            # Fix agent IDs if LLM returned without suffix
            agent_id_map = {
                "data-agent": "data-agent-001",
                "viz-agent": "viz-agent-001",
                "research-agent": "research-agent-001",
                "narrative-agent": "narrative-agent-001"
            }
            
            # Fix agents_needed
            if "agents_needed" in orchestration_plan:
                orchestration_plan["agents_needed"] = [
                    agent_id_map.get(aid, aid) for aid in orchestration_plan["agents_needed"]
                ]
            
            # Fix execution_steps
            if "execution_steps" in orchestration_plan:
                for step in orchestration_plan["execution_steps"]:
                    if "agent_id" in step:
                        step["agent_id"] = agent_id_map.get(step["agent_id"], step["agent_id"])
        
        # Execute the plan using A2A messages
        logger.info(f"Executing plan with {len(orchestration_plan.get('agents_needed', []))} agents")
        logger.info(f"Agent IDs in plan: {orchestration_plan.get('agents_needed', [])}")
        results = await self._execute_plan_via_a2a(orchestration_plan, query, context)
        
        # Generate UI spec based on results
        ui_spec = {
            "layout": "dashboard",
            "components": []
        }
        
        # Add components based on what agents returned
        for agent_id, output in results.get("outputs", {}).items():
            if "viz-agent" in agent_id and output:
                ui_spec["components"].append({
                    "type": "chart",
                    "data": output
                })
            elif "narrative-agent" in agent_id and output:
                ui_spec["components"].append({
                    "type": "narrative",
                    "data": output
                })
            elif "data-agent" in agent_id and output:
                ui_spec["components"].append({
                    "type": "data_table",
                    "data": output
                })
        
        return {
            "query": query,
            "method": "llm_orchestration" if orchestration_plan else "simple_orchestration",
            "plan": orchestration_plan,
            "results": results,
            "ui_spec": ui_spec,
            "status": "completed"
        }
    
    async def _execute_compose_ui(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Compose UI components dynamically"""
        components = parameters["components"]
        layout = parameters.get("layout", "auto")
        
        # Use LLM to optimize layout if available
        optimized_layout = None
        if self.llm.is_available() and layout == "auto":
            prompt = f"""Given these UI components:
{json.dumps(components, indent=2)}

Determine the best layout arrangement considering:
1. Visual hierarchy
2. Data relationships
3. User flow
4. Responsive design

Respond with JSON containing:
- layout_type: grid, vertical, horizontal, or dashboard
- component_order: Optimized order of components
- layout_config: Specific configuration for the layout"""

            optimized_layout = await self.llm.generate_json(prompt)
        
        # Generate composed UI specification
        ui_spec = {
            "layout": optimized_layout or {"layout_type": layout},
            "components": components,
            "metadata": {
                "composed_by": "gui-agent",
                "component_count": len(components)
            }
        }
        
        # Generate React component code
        ui_spec["component_code"] = self._generate_composed_ui_code(ui_spec)
        
        return ui_spec
    
    async def _execute_plan_execution(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Create an execution plan for a query"""
        query = parameters["query"]
        available_agents = parameters.get("available_agents", [])
        
        if not available_agents and self.a2a_registry:
            # Discover relevant agents
            discovery_results = await self.a2a_registry.discover_agents(query)
            available_agents = [r.agent.id for r in discovery_results[:5]]
        
        # Use LLM to create execution plan
        execution_plan = None
        if self.llm.is_available():
            prompt = f"""Create an execution plan for this query:
"{query}"

Available agents: {available_agents}

Create a step-by-step plan with:
1. steps: List of execution steps
2. dependencies: Which steps depend on others
3. parallel_execution: Which steps can run in parallel
4. expected_duration: Estimated time

Respond with JSON."""

            execution_plan = await self.llm.generate_json(prompt)
        
        if not execution_plan:
            # Simple fallback plan
            execution_plan = {
                "steps": [
                    {"id": 1, "agent": "data-agent", "action": "query_data"},
                    {"id": 2, "agent": "viz-agent", "action": "create_chart", "depends_on": [1]}
                ],
                "parallel_execution": [],
                "expected_duration": "5-10 seconds"
            }
        
        return {
            "query": query,
            "plan": execution_plan,
            "agents_involved": available_agents
        }
    
    def _simple_orchestration(self, query: str) -> Dict[str, Any]:
        """Simple keyword-based orchestration fallback"""
        query_lower = query.lower()
        agents_needed = []
        
        # Map agent types to actual agent IDs
        agent_id_map = {
            "data-agent": "data-agent-001",
            "viz-agent": "viz-agent-001",
            "research-agent": "research-agent-001",
            "narrative-agent": "narrative-agent-001"
        }
        
        # Determine needed agents based on keywords
        if any(word in query_lower for word in ["data", "show", "analyze", "compare"]):
            agents_needed.append(agent_id_map["data-agent"])
        
        if any(word in query_lower for word in ["chart", "graph", "visualize", "plot"]):
            agents_needed.append(agent_id_map["viz-agent"])
        
        if any(word in query_lower for word in ["research", "trend", "insight", "why"]):
            agents_needed.append(agent_id_map["research-agent"])
        
        if any(word in query_lower for word in ["explain", "story", "narrative", "describe"]):
            agents_needed.append(agent_id_map["narrative-agent"])
        
        if not agents_needed:
            agents_needed = [agent_id_map["data-agent"]]  # Default to data agent
        
        return {
            "agents_needed": agents_needed,
            "execution_order": agents_needed,
            "data_flow": "sequential",
            "expected_outputs": {agent: "default" for agent in agents_needed}
        }
    
    async def _execute_plan_via_a2a(self, plan: Dict[str, Any], query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the orchestration plan using A2A Protocol"""
        results = {
            "agents_executed": [],
            "outputs": {},
            "errors": []
        }
        
        # For distributed agents, we'll send messages via HTTP to the backend
        # which will route them through the A2A registry
        
        logger.info(f"Plan contains {len(plan.get('execution_steps', []))} execution steps")
        
        # Execute steps from the plan
        steps = plan.get("execution_steps", [])
        if not steps and plan.get("agents_needed"):
            # Convert simple agent list to steps
            steps = [{"agent_id": aid, "action": "default"} for aid in plan["agents_needed"]]
        
        for step in steps:
            agent_id = step.get("agent_id")
            
            # Map default actions based on agent type
            default_actions = {
                "data-agent-001": "query_data",
                "viz-agent-001": "create_visualization",
                "research-agent-001": "search_insights",
                "narrative-agent-001": "generate_narrative"
            }
            
            action = step.get("action", "default")
            if action == "default":
                action = default_actions.get(agent_id, "handle_intent")
            
            params = step.get("parameters", {"query": query, "context": context})
            
            try:
                logger.info(f"GUI Agent sending {action} to {agent_id}")
                
                # Send A2A message to the agent
                result = await self.send_a2a_message(
                    to_agent=agent_id,
                    action=action,
                    payload=params
                )
                
                if result is not None:
                    results["agents_executed"].append(agent_id)
                    results["outputs"][agent_id] = result
                    
                    # Pass results to next agent if specified
                    if step.get("pass_to_next") and steps.index(step) < len(steps) - 1:
                        next_step = steps[steps.index(step) + 1]
                        if "parameters" not in next_step:
                            next_step["parameters"] = {}
                        next_step["parameters"]["previous_result"] = result
                else:
                    # No result received
                    results["errors"].append({
                        "agent": agent_id,
                        "action": action,
                        "error": "No response from agent"
                    })
                    
            except Exception as e:
                logger.error(f"Error sending A2A message to {agent_id}: {e}")
                results["errors"].append({
                    "agent": agent_id,
                    "action": action,
                    "error": str(e) if str(e) else "No response from agent"
                })
                
                # Continue with other agents even if one fails
                continue
        
        # Generate UI spec from results
        ui_spec = await self._generate_ui_spec(results, query)
        results["ui_spec"] = ui_spec
        
        return results
    
    def _generate_composed_ui_code(self, ui_spec: Dict[str, Any]) -> str:
        """Generate React component code for composed UI"""
        layout = ui_spec["layout"]
        components = ui_spec["components"]
        
        layout_type = layout.get("layout_type", "grid") if isinstance(layout, dict) else layout
        
        layout_classes = {
            "grid": "grid grid-cols-1 md:grid-cols-2 gap-6",
            "vertical": "flex flex-col space-y-6",
            "horizontal": "flex flex-row space-x-6 overflow-x-auto",
            "dashboard": "grid grid-cols-12 gap-6"
        }
        
        return f'''
import React from 'react';
import {{ motion }} from 'framer-motion';

export default function ComposedUI() {{
  const components = {json.dumps(components)};
  
  return (
    <div className="{layout_classes.get(layout_type, layout_classes['grid'])}">
      {{components.map((component, index) => (
        <motion.div
          key={{index}}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: index * 0.1 }}
          className={{layout_type === 'dashboard' ? 'col-span-6' : ''}}
        >
          {{/* Dynamic component will be rendered here based on component.type */}}
          <div className="component-placeholder">
            Component: {{component.type}}
          </div>
        </motion.div>
      ))}}
    </div>
  );
}}
'''
    
    async def send_a2a_message(self, to_agent: str, action: str, payload: Dict[str, Any], 
                              message_type: MessageType = MessageType.REQUEST) -> Optional[Any]:
        """Send a message to another agent via A2A using HTTP (for distributed agents)"""
        import uuid
        
        message_data = {
            "id": str(uuid.uuid4()),
            "from_agent": self.agent_id,
            "to_agent": to_agent,
            "message_type": message_type.value,
            "action": action,
            "payload": payload
        }
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.backend_url}/api/a2a/message",
                    json=message_data
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get("success"):
                        return result.get("result")
                    else:
                        logger.error(f"A2A message failed: {result.get('error')}")
                        return None
                else:
                    logger.error(f"A2A message failed with status {response.status_code}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error sending A2A message: {e}")
            return None