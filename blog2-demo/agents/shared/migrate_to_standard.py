#!/usr/bin/env python3
"""Migration helper to update agents to use the standard base class and runner"""

import os
import sys

# Template for updating agent imports
AGENT_IMPORT_TEMPLATE = """from typing import List, Dict, Any, Optional
from unified_base_agent import UnifiedBaseAgent
from mcp.schemas import MCPTool, ToolParameter, ParameterType
from llm import LLMConfig
"""

# Template for updating main.py to use StandardAgentRunner
MAIN_PY_TEMPLATE = """import asyncio
import sys
import os

# Add parent directory to path to import shared modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared.standard_agent_runner import StandardAgentRunner
from {agent_module} import {agent_class}

async def main():
    runner = StandardAgentRunner({agent_class})
    await runner.run()

if __name__ == "__main__":
    asyncio.run(main())
"""

def update_agent_class(agent_file_path: str, agent_class_name: str):
    """Update an agent class to inherit from UnifiedBaseAgent"""
    print(f"Updating {agent_file_path}...")
    
    with open(agent_file_path, 'r') as f:
        content = f.read()
    
    # Replace BaseAgent import and inheritance
    content = content.replace('from base_agent import BaseAgent', 'from unified_base_agent import UnifiedBaseAgent')
    content = content.replace('from shared.base_agent import BaseAgent', 'from shared.unified_base_agent import UnifiedBaseAgent')
    content = content.replace(f'class {agent_class_name}(BaseAgent):', f'class {agent_class_name}(UnifiedBaseAgent):')
    
    # Update constructor to include capabilities and tags
    if 'def __init__(self' in content and 'capabilities' not in content:
        # Find the constructor and add capabilities/tags parameters
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if 'def __init__(self' in line and agent_class_name in content[:content.find(line)]:
                # Check if super().__init__ is called
                for j in range(i, min(i+20, len(lines))):
                    if 'super().__init__(' in lines[j]:
                        # Add capabilities and tags to the super call if not present
                        if 'capabilities=' not in lines[j]:
                            lines[j] = lines[j].rstrip(')')
                            lines[j] += ', capabilities=self._get_capabilities(), tags=self._get_tags())'
                        break
        content = '\n'.join(lines)
        
        # Add helper methods if not present
        if '_get_capabilities' not in content:
            capabilities_method = """
    def _get_capabilities(self) -> List[str]:
        \"\"\"Get agent capabilities\"\"\"
        return [tool.description for tool in self.get_tools()]
    
    def _get_tags(self) -> List[str]:
        \"\"\"Get agent tags\"\"\"
        # Override in subclass to provide specific tags
        return []
"""
            # Insert before _register_tools method
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if 'def _register_tools(self):' in line:
                    lines.insert(i, capabilities_method)
                    break
            content = '\n'.join(lines)
    
    with open(agent_file_path, 'w') as f:
        f.write(content)
    
    print(f"✓ Updated {agent_file_path}")

def update_main_py(main_py_path: str, agent_module: str, agent_class: str):
    """Update main.py to use StandardAgentRunner"""
    print(f"Updating {main_py_path}...")
    
    content = MAIN_PY_TEMPLATE.format(
        agent_module=agent_module,
        agent_class=agent_class
    )
    
    with open(main_py_path, 'w') as f:
        f.write(content)
    
    print(f"✓ Updated {main_py_path}")

def main():
    """Run the migration"""
    agents_to_migrate = [
        {
            "path": "data-agent",
            "module": "data_agent",
            "class": "DataAgent"
        },
        {
            "path": "viz-agent", 
            "module": "viz_agent",
            "class": "VizAgent"
        },
        {
            "path": "research-agent",
            "module": "research_agent", 
            "class": "ResearchAgent"
        },
        {
            "path": "narrative-agent",
            "module": "narrative_agent",
            "class": "NarrativeAgent"
        }
    ]
    
    base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    for agent in agents_to_migrate:
        agent_dir = os.path.join(base_path, agent["path"])
        if os.path.exists(agent_dir):
            # Update agent class file
            agent_file = os.path.join(agent_dir, f"{agent['module']}.py")
            if os.path.exists(agent_file):
                update_agent_class(agent_file, agent["class"])
            
            # Update main.py
            main_file = os.path.join(agent_dir, "main.py")
            if os.path.exists(main_file):
                update_main_py(main_file, agent["module"], agent["class"])
        else:
            print(f"⚠ Agent directory not found: {agent_dir}")
    
    print("\n✅ Migration complete!")
    print("\nNext steps:")
    print("1. Update backend agents to use UnifiedBaseAgent")
    print("2. Test all agents with the new standard endpoints")
    print("3. Update A2A registry to discover agents via /agent-card endpoint")

if __name__ == "__main__":
    main()